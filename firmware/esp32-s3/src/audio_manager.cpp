#include "audio_manager.h"
#include "ble_manager.h"
#include <driver/i2s.h>
#include <driver/gpio.h>
#include <math.h>

AudioManager::AudioManager() {}

bool AudioManager::init() {
  bool micOk = initMicrophone();
  bool spkOk = initSpeaker();
  return micOk || spkOk;
}

bool AudioManager::initMicrophone() {
  // 1. Pull down data line to eliminate floating noise when mic is disconnected
  gpio_set_pull_mode((gpio_num_t)I2S_MIC_DATA, GPIO_PULLDOWN_ONLY);

  // 2. Configure I2S driver in Standard I2S RX mode with 32-bit slot width for INMP441 Digital Mic
  // INMP441 delivers 24-bit 2's complement audio in a 32-bit frame.
  i2s_config_t i2s_mic_config = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
      .sample_rate = I2S_MIC_SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT, // 32-bit slot width avoids 0-sample alignment dropouts
      .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,   // INMP441 L/R tied to GND -> Left Channel
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8,
      .dma_buf_len = 256,
      .use_apll = false,
      .tx_desc_auto_clear = false,
      .fixed_mclk = 0
  };

  i2s_pin_config_t mic_pin_config = {
      .bck_io_num = I2S_MIC_BCLK,   // GPIO 7  (D8  / SCK)
      .ws_io_num = I2S_MIC_LRCLK,   // GPIO 4  (D3  / WS)
      .data_out_num = I2S_PIN_NO_CHANGE,
      .data_in_num = I2S_MIC_DATA   // GPIO 9  (D10 / SD)
  };

  esp_err_t err = i2s_driver_install(I2S_MIC_PORT, &i2s_mic_config, 0, NULL);
  if (err == ESP_OK) {
    i2s_set_pin(I2S_MIC_PORT, &mic_pin_config);
    i2s_set_clk(I2S_MIC_PORT, I2S_MIC_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_32BIT,
                I2S_CHANNEL_MONO);
    _micInitialized = true;
    Serial.printf("[AUDIO] INMP441 Mic Driver Initialized (16kHz 32b-Slot Mono, SCK=GPIO%d/D8, WS=GPIO%d/D3, SD=GPIO%d/D10)\n",
                  I2S_MIC_BCLK, I2S_MIC_LRCLK, I2S_MIC_DATA);
  } else {
    Serial.printf("[AUDIO] INMP441 Mic Driver Install Failed (err=0x%x)\n", err);
    _micInitialized = false;
  }
  return _micInitialized;
}

bool AudioManager::initSpeaker() {
  // Configure I2S driver in Master TX mode for MAX98357A I2S Class-D Amplifier on I2S_NUM_1
  i2s_config_t i2s_spk_config = {
      .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX),
      .sample_rate = I2S_SPK_SAMPLE_RATE,
      .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
      .channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT, // Stereo frames for MAX98357A
      .communication_format = I2S_COMM_FORMAT_STAND_I2S,
      .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
      .dma_buf_count = 8,
      .dma_buf_len = 256,
      .use_apll = false,
      .tx_desc_auto_clear = true, // Clear buffer on underflow to avoid buzzing
      .fixed_mclk = 0
  };

  i2s_pin_config_t spk_pin_config = {
      .bck_io_num = I2S_SPK_BCLK,   // GPIO 2 (D1 / BCLK)
      .ws_io_num = I2S_SPK_LRCLK,   // GPIO 3 (D2 / LRC)
      .data_out_num = I2S_SPK_DATA, // GPIO 1 (D0 / DIN)
      .data_in_num = I2S_PIN_NO_CHANGE
  };

  esp_err_t err = i2s_driver_install(I2S_SPK_PORT, &i2s_spk_config, 0, NULL);
  if (err == ESP_OK) {
    i2s_set_pin(I2S_SPK_PORT, &spk_pin_config);
    i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT,
                I2S_CHANNEL_STEREO);
    i2s_zero_dma_buffer(I2S_SPK_PORT);
    _speakerInitialized = true;
    Serial.printf("[AUDIO] MAX98357A Speaker Driver Initialized (16kHz Stereo-Out, DIN=GPIO%d/D0, BCLK=GPIO%d/D1, LRC=GPIO%d/D2)\n",
                  I2S_SPK_DATA, I2S_SPK_BCLK, I2S_SPK_LRCLK);
  } else {
    Serial.printf("[AUDIO] MAX98357A Speaker Driver Install Failed (err=0x%x)\n", err);
    _speakerInitialized = false;
  }
  return _speakerInitialized;
}

void AudioManager::setVolume(uint8_t volumePercent) {
  if (volumePercent > 100)
    volumePercent = 100;
  _volume = volumePercent;
  Serial.printf("[AUDIO] Speaker Volume set to %u%%\n", _volume);
}

void AudioManager::startMicrophone() {
  _isRecording = true;
  _audioFrameCount = 0;
  _lastLiveVuTime = millis();
  Serial.println("[AUDIO] >>> PUSH-TO-TALK ACTIVE: Speak into INMP441 Mic now...");
}

void AudioManager::stopMicrophone() {
  _isRecording = false;
  Serial.printf("[AUDIO] <<< PUSH-TO-TALK FINISHED: %u audio frames captured.\n", _audioFrameCount);
}

static float dcFilterLastIn = 0.0f;
static float dcFilterLastOut = 0.0f;

size_t AudioManager::readMicrophone(int16_t *buffer, size_t maxSamples) {
  if (!_micInitialized || buffer == nullptr || maxSamples == 0)
    return 0;

  const size_t STACK_MAX = 256;
  int32_t raw32[STACK_MAX];
  size_t toRead = (maxSamples > STACK_MAX) ? STACK_MAX : maxSamples;

  size_t bytesRead = 0;
  esp_err_t err = i2s_read(I2S_MIC_PORT, (void *)raw32, toRead * sizeof(int32_t),
                           &bytesRead, pdMS_TO_TICKS(50));
  if (err == ESP_OK && bytesRead > 0) {
    size_t samplesRead = bytesRead / sizeof(int32_t);

    // Single-pole DC-blocker filter and natural digital boost
    const float r = 0.992f;
    const float gain = 2.5f;

    for (size_t i = 0; i < samplesRead; i++) {
      // INMP441 24-bit MSB in 32-bit slot -> shift right by 14 bits to 16-bit range
      int32_t s32 = raw32[i];
      int16_t sample16 = (int16_t)(s32 >> 14);

      float inVal = (float)sample16;
      float filtered = inVal - dcFilterLastIn + (r * dcFilterLastOut);
      dcFilterLastIn = inVal;
      dcFilterLastOut = filtered;

      float boosted = filtered * gain;
      if (boosted > 32000.0f)
        boosted = 32000.0f;
      if (boosted < -32000.0f)
        boosted = -32000.0f;

      buffer[i] = (int16_t)boosted;
    }
    return samplesRead;
  }
  return 0;
}

float AudioManager::getAudioLevelRMS() {
  if (!_micInitialized)
    return 0.0f;
  int16_t samples[128];
  size_t count = readMicrophone(samples, 128);
  if (count == 0)
    return 0.0f;

  double sum = 0.0;
  for (size_t i = 0; i < count; i++) {
    sum += (double)samples[i];
  }
  double mean = sum / (double)count;

  double sumSq = 0.0;
  for (size_t i = 0; i < count; i++) {
    double acVal = (double)samples[i] - mean;
    sumSq += acVal * acVal;
  }
  _lastRms = (float)sqrt(sumSq / (double)count);
  return _lastRms;
}

void AudioManager::runMicrophoneDiagnostic(uint32_t durationMs) {
  if (!_micInitialized) {
    Serial.println("[MIC DIAGNOSTIC] ERROR: I2S Driver not initialized.");
    return;
  }

  Serial.println();
  Serial.println("==================================================");
  Serial.println("  INMP441 DIGITAL MICROPHONE LIVE DIAGNOSTIC");
  Serial.printf("  Sampling Rate: %d Hz | Pins: SCK=GPIO%d(D8), WS=GPIO%d(D3), SD=GPIO%d(D10)\n",
                I2S_MIC_SAMPLE_RATE, I2S_MIC_BCLK, I2S_MIC_LRCLK, I2S_MIC_DATA);
  Serial.println("  Speak into the microphone now or tap the desk...");
  Serial.println("==================================================");

  uint32_t startTime = millis();
  int16_t buffer[256];
  float maxRMS = 0.0f;
  int16_t absolutePeak = 0;
  uint32_t voiceFrames = 0;
  uint32_t totalFrames = 0;

  while (millis() - startTime < durationMs) {
    size_t samplesRead = readMicrophone(buffer, 256);
    if (samplesRead > 0) {
      totalFrames++;

      double sum = 0.0;
      for (size_t i = 0; i < samplesRead; i++)
        sum += (double)buffer[i];
      double mean = sum / (double)samplesRead;

      double sumSq = 0.0;
      int16_t framePeak = 0;
      for (size_t i = 0; i < samplesRead; i++) {
        double ac = (double)buffer[i] - mean;
        if (abs((int)ac) > framePeak)
          framePeak = abs((int)ac);
        sumSq += ac * ac;
      }

      float rms = (float)sqrt(sumSq / (double)samplesRead);
      if (rms > maxRMS)
        maxRMS = rms;
      if (framePeak > absolutePeak)
        absolutePeak = framePeak;

      int bars = (int)(rms / 60.0f);
      if (bars > 16)
        bars = 16;
      if (bars < 0)
        bars = 0;

      String vuMeter = "";
      for (int b = 0; b < 16; b++) {
        vuMeter += (b < bars) ? "#" : ".";
      }

      bool isVoice = (rms > 200.0f);
      if (isVoice)
        voiceFrames++;

      Serial.printf("[MIC VU] [%s] RMS:%5.0f | Peak:%5d | Status: %s\n",
                    vuMeter.c_str(), rms, framePeak,
                    isVoice ? "SOUND DETECTED" : "QUIET");
    }
    delay(60);
  }

  Serial.println("--------------------------------------------------");
  Serial.println("  MICROPHONE DIAGNOSTIC SUMMARY");
  Serial.printf("  - Max RMS Energy: %.1f\n", maxRMS);
  Serial.printf("  - Absolute Peak Amplitude: %d / 32767\n", absolutePeak);
  Serial.printf("  - Sound Detection Ratio: %u / %u frames (%.1f%%)\n",
                voiceFrames, totalFrames,
                totalFrames > 0 ? (voiceFrames * 100.0f / totalFrames) : 0.0f);

  if (maxRMS > 180.0f || absolutePeak > 400) {
    Serial.println("  - Final Verdict: [PASS] INMP441 Microphone is verified & functioning perfectly!");
  } else {
    Serial.println("  - Final Verdict: [NOTE] Low audio energy received (RMS=0 means mic is disconnected).");
  }
  Serial.println("==================================================");
  Serial.println();
}

void AudioManager::runVoiceLoopbackTest(uint32_t durationMs) {
  if (!_micInitialized || !_speakerInitialized) {
    Serial.println("[LOOPBACK] ERROR: Microphone or Speaker not initialized.");
    return;
  }

  Serial.println();
  Serial.println("==================================================");
  Serial.println("  VOICE LOOPBACK TEST (MIC -> RECORD -> SPEAKER PLAYBACK)");
  Serial.printf("  Recording %u seconds of your voice from INMP441...\n", durationMs / 1000);
  Serial.println("  Speak into the microphone NOW!");
  Serial.println("==================================================");

  playSound(SoundEffect::SOUND_PTT_START);
  delay(100);

  uint8_t *wavBuf = nullptr;
  size_t wavLen = 0;

  bool ok = recordWavAudio(durationMs, &wavBuf, &wavLen);
  playSound(SoundEffect::SOUND_PTT_STOP);
  delay(150);

  if (ok && wavBuf && wavLen > 0) {
    Serial.printf("[LOOPBACK] Recording successful (%u bytes). Playing back on MAX98357A speaker...\n", (unsigned int)wavLen);
    playWavAudio(wavBuf, wavLen);
    releaseWavBuffer(wavBuf);
    Serial.println("==================================================");
    Serial.println("  [PASS] Voice loopback playback finished!");
    Serial.println("==================================================");
  } else {
    Serial.println("[LOOPBACK] ERROR: Failed to record audio.");
  }
  Serial.println();
}

// -----------------------------------------------------------------------------
// Speaker Synthesizer & Playback (MAX98357A)
// -----------------------------------------------------------------------------

void AudioManager::playTone(uint16_t freqHz, uint32_t durationMs) {
  if (!_speakerInitialized || durationMs == 0)
    return;

  if (freqHz == 0) {
    delay(durationMs);
    return;
  }

  size_t totalSamples = (I2S_SPK_SAMPLE_RATE * durationMs) / 1000;
  const size_t CHUNK_SAMPLES = 128;
  int16_t stereoBuffer[CHUNK_SAMPLES * 2];

  float phase = 0.0f;
  float phaseInc =
      (2.0f * (float)M_PI * (float)freqHz) / (float)I2S_SPK_SAMPLE_RATE;
  float volScale = ((float)_volume / 100.0f) * 0.85f;

  size_t samplesGenerated = 0;
  while (samplesGenerated < totalSamples) {
    size_t currentBatch = (totalSamples - samplesGenerated > CHUNK_SAMPLES)
                              ? CHUNK_SAMPLES
                              : (totalSamples - samplesGenerated);
    for (size_t i = 0; i < currentBatch; i++) {
      float env = 1.0f;
      size_t sampleIdx = samplesGenerated + i;
      if (sampleIdx < 64) {
        env = (float)sampleIdx / 64.0f;
      } else if (totalSamples - sampleIdx < 64) {
        env = (float)(totalSamples - sampleIdx) / 64.0f;
      }

      float sampleVal = sinf(phase) * 30000.0f * volScale * env;
      int16_t s = (int16_t)sampleVal;
      stereoBuffer[i * 2] = s;     // Left channel
      stereoBuffer[i * 2 + 1] = s; // Right channel

      phase += phaseInc;
      if (phase >= 2.0f * (float)M_PI)
        phase -= 2.0f * (float)M_PI;
    }

    size_t bytesWritten = 0;
    i2s_write(I2S_SPK_PORT, (const void *)stereoBuffer,
              currentBatch * 2 * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
    samplesGenerated += currentBatch;
  }
}

void AudioManager::playMelody(const uint16_t *freqs,
                              const uint16_t *durationsMs, size_t count) {
  if (!_speakerInitialized || !freqs || !durationsMs || count == 0)
    return;
  for (size_t i = 0; i < count; i++) {
    playTone(freqs[i], durationsMs[i]);
    delay(12);
  }
}

void AudioManager::playSound(SoundEffect effect) {
  if (!_speakerInitialized)
    return;

  switch (effect) {
  case SoundEffect::SOUND_WAKE: {
    uint16_t notes[] = {659, 988};
    uint16_t durs[] = {80, 140};
    playMelody(notes, durs, 2);
    break;
  }
  case SoundEffect::SOUND_AI_RESPONSE: {
    uint16_t notes[] = {523, 659, 784, 1046};
    uint16_t durs[] = {70, 70, 90, 150};
    playMelody(notes, durs, 4);
    break;
  }
  case SoundEffect::SOUND_MESSAGE_ALERT: {
    uint16_t notes[] = {784, 0, 1046};
    uint16_t durs[] = {90, 40, 180};
    playMelody(notes, durs, 3);
    break;
  }
  case SoundEffect::SOUND_CALL_INCOMING: {
    uint16_t notes[] = {880, 1046, 880, 1046};
    uint16_t durs[] = {100, 100, 100, 150};
    playMelody(notes, durs, 4);
    break;
  }
  case SoundEffect::SOUND_SUCCESS: {
    uint16_t notes[] = {523, 784, 1046};
    uint16_t durs[] = {60, 60, 140};
    playMelody(notes, durs, 3);
    break;
  }
  case SoundEffect::SOUND_ERROR: {
    uint16_t notes[] = {349, 261};
    uint16_t durs[] = {110, 200};
    playMelody(notes, durs, 2);
    break;
  }
  case SoundEffect::SOUND_DEVICE_CONNECTED: {
    uint16_t notes[] = {523, 784};
    uint16_t durs[] = {60, 120};
    playMelody(notes, durs, 2);
    break;
  }
  case SoundEffect::SOUND_DEVICE_DISCONNECTED: {
    uint16_t notes[] = {784, 523};
    uint16_t durs[] = {80, 140};
    playMelody(notes, durs, 2);
    break;
  }
  case SoundEffect::SOUND_PTT_START: {
    playTone(1046, 45); // High beep for Push-To-Talk Start
    break;
  }
  case SoundEffect::SOUND_PTT_STOP: {
    playTone(659, 45);  // Lower beep for Push-To-Talk Stop
    break;
  }
  }
}

void AudioManager::playPcmAudio(const int16_t *samples, size_t sampleCount,
                                uint32_t sampleRate) {
  if (!_speakerInitialized || !samples || sampleCount == 0)
    return;

  if (sampleRate != I2S_SPK_SAMPLE_RATE) {
    i2s_set_clk(I2S_SPK_PORT, sampleRate, I2S_BITS_PER_SAMPLE_16BIT,
                I2S_CHANNEL_STEREO);
  }

  const size_t BATCH_SIZE = 128;
  int16_t stereoBuffer[BATCH_SIZE * 2];
  float volScale = (float)_volume / 100.0f;

  size_t processed = 0;
  while (processed < sampleCount) {
    size_t toProcess = (sampleCount - processed > BATCH_SIZE)
                           ? BATCH_SIZE
                           : (sampleCount - processed);
    for (size_t i = 0; i < toProcess; i++) {
      int16_t s = (int16_t)((float)samples[processed + i] * volScale);
      stereoBuffer[i * 2] = s;     // Left
      stereoBuffer[i * 2 + 1] = s; // Right
    }
    size_t bytesWritten = 0;
    i2s_write(I2S_SPK_PORT, (const void *)stereoBuffer,
              toProcess * 2 * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
    processed += toProcess;
  }

  if (sampleRate != I2S_SPK_SAMPLE_RATE) {
    i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT,
                I2S_CHANNEL_STEREO);
  }
}

struct WavHeader {
  char riff_tag[4];
  uint32_t riff_size;
  char wave_tag[4];
  char fmt_tag[4];
  uint32_t fmt_size;
  uint16_t audio_format;
  uint16_t num_channels;
  uint32_t sample_rate;
  uint32_t byte_rate;
  uint16_t block_align;
  uint16_t bits_per_sample;
  char data_tag[4];
  uint32_t data_size;
};

void AudioManager::playWavAudio(const uint8_t *wavBytes, size_t wavLength) {
  if (!_speakerInitialized || !wavBytes || wavLength < sizeof(WavHeader))
    return;

  const WavHeader *header = (const WavHeader *)wavBytes;
  if (strncmp(header->riff_tag, "RIFF", 4) != 0 ||
      strncmp(header->wave_tag, "WAVE", 4) != 0) {
    Serial.println("[AUDIO] ERROR: Invalid WAV header format.");
    return;
  }

  size_t dataOffset = 12;
  while (dataOffset + 8 <= wavLength) {
    if (memcmp(wavBytes + dataOffset, "data", 4) == 0) {
      dataOffset += 8;
      break;
    }
    uint32_t chunkSize = *(uint32_t *)(wavBytes + dataOffset + 4);
    dataOffset += 8 + chunkSize;
  }

  if (dataOffset >= wavLength) {
    dataOffset = sizeof(WavHeader);
  }

  const int16_t *pcmSamples = (const int16_t *)(wavBytes + dataOffset);
  size_t pcmBytes = wavLength - dataOffset;
  size_t sampleCount = pcmBytes / sizeof(int16_t);

  Serial.printf("[AUDIO] Playing WAV: %u bytes (%u Hz, %d-channel, %u samples)\n",
                (unsigned int)wavLength, header->sample_rate, header->num_channels,
                (unsigned int)sampleCount);

  if (header->num_channels == 1) {
    playPcmAudio(pcmSamples, sampleCount, header->sample_rate);
  } else {
    if (header->sample_rate != I2S_SPK_SAMPLE_RATE) {
      i2s_set_clk(I2S_SPK_PORT, header->sample_rate, I2S_BITS_PER_SAMPLE_16BIT,
                  I2S_CHANNEL_STEREO);
    }
    size_t bytesWritten = 0;
    i2s_write(I2S_SPK_PORT, (const void *)pcmSamples, pcmBytes, &bytesWritten,
              portMAX_DELAY);
    if (header->sample_rate != I2S_SPK_SAMPLE_RATE) {
      i2s_set_clk(I2S_SPK_PORT, I2S_SPK_SAMPLE_RATE, I2S_BITS_PER_SAMPLE_16BIT,
                  I2S_CHANNEL_STEREO);
    }
  }
}

void AudioManager::streamPcmChunk(const uint8_t *pcmChunk, size_t chunkSize) {
  if (!_speakerInitialized || !pcmChunk || chunkSize == 0)
    return;

  size_t sampleCount = chunkSize / sizeof(int16_t);
  const int16_t *inSamples = (const int16_t *)pcmChunk;
  const size_t BATCH_SIZE = 128;
  int16_t stereoBuf[BATCH_SIZE * 2];
  float volScale = ((float)_volume / 100.0f) * 0.85f;

  size_t processed = 0;
  while (processed < sampleCount) {
    size_t toProcess = (sampleCount - processed > BATCH_SIZE)
                           ? BATCH_SIZE
                           : (sampleCount - processed);
    for (size_t i = 0; i < toProcess; i++) {
      float rawFloat = (float)inSamples[processed + i] * volScale;
      if (rawFloat > 32000.0f)
        rawFloat = 32000.0f;
      if (rawFloat < -32000.0f)
        rawFloat = -32000.0f;

      int16_t s = (int16_t)rawFloat;
      stereoBuf[i * 2] = s;     // Left
      stereoBuf[i * 2 + 1] = s; // Right
    }
    size_t bytesWritten = 0;
    i2s_write(I2S_SPK_PORT, (const void *)stereoBuf,
              toProcess * 2 * sizeof(int16_t), &bytesWritten, portMAX_DELAY);
    processed += toProcess;
  }
}

void AudioManager::stopPlayback() {
  if (_speakerInitialized) {
    i2s_zero_dma_buffer(I2S_SPK_PORT);
  }
}

void AudioManager::runSpeakerDiagnostic() {
  if (!_speakerInitialized) {
    Serial.println("[SPEAKER DIAGNOSTIC] ERROR: MAX98357A I2S Speaker driver not initialized.");
    return;
  }

  Serial.println();
  Serial.println("==================================================");
  Serial.println("  MAX98357A I2S SPEAKER LIVE HARDWARE TEST (SPK_TEST)");
  Serial.printf("  Sampling Rate: %d Hz | Pins: DIN=GPIO%d(D0), BCLK=GPIO%d(D1), LRC=GPIO%d(D2)\n",
                I2S_SPK_SAMPLE_RATE, I2S_SPK_DATA, I2S_SPK_BCLK, I2S_SPK_LRCLK);
  Serial.printf("  Volume: %u%%\n", _volume);
  Serial.println("==================================================");

  Serial.println("  [1/4] Playing 440 Hz Sine Tone (Concert A) for 500ms...");
  playTone(440, 500);
  delay(150);

  Serial.println("  [2/4] Playing 880 Hz Sine Tone (High A) for 500ms...");
  playTone(880, 500);
  delay(150);

  Serial.println("  [3/4] Playing Wake-up Chime...");
  playSound(SoundEffect::SOUND_WAKE);
  delay(250);

  Serial.println("  [4/4] Playing AI Response Chime...");
  playSound(SoundEffect::SOUND_AI_RESPONSE);
  delay(200);

  Serial.println("--------------------------------------------------");
  Serial.println("  [PASS] MAX98357A Speaker Hardware Test Complete!");
  Serial.println("==================================================");
  Serial.println();
}

void AudioManager::runFullAudioDiagnostic() {
  runSpeakerDiagnostic();
  delay(300);
  runMicrophoneDiagnostic(3000);
}

// -----------------------------------------------------------------------------
// Voice Wake, Push-To-Talk & Audio Processing Loop
// -----------------------------------------------------------------------------

void AudioManager::triggerVoiceWakeSession() {
  if (_speechActive) return;
  _speechActive = true;
  _speechStartTime = millis();
  _lastSpeechTime = millis();
  _consecutiveVoiceFrames = 2;
  _audioFrameCount = 0;
  _lastLiveVuTime = millis();
  playSound(SoundEffect::SOUND_PTT_START);
  Serial.println();
  Serial.println("==================================================");
  Serial.println("[VAD] >>> VOICE ACTIVITY DETECTED: Listening...");
  Serial.println("[VAD] >>> Streaming audio to Mobile Phone (TALK_START)");
  Serial.println("==================================================");
  BleManager::getInstance().sendEvent("TALK_START");
}

void AudioManager::stopVoiceWakeSession() {
  if (!_speechActive) return;
  _speechActive = false;
  _consecutiveVoiceFrames = 0;
  playSound(SoundEffect::SOUND_PTT_STOP);
  Serial.println();
  Serial.println("==================================================");
  Serial.printf("[VAD] <<< SILENCE DETECTED: Speech Ended -> Sent TALK_STOP (%u frames, %lums)\n",
                _audioFrameCount, millis() - _speechStartTime);
  Serial.println("==================================================");
  BleManager::getInstance().sendEvent("TALK_STOP");
}

void AudioManager::update() {
  if (!_micInitialized)
    return;

  // Real-time audio frame acquisition: 240 samples (15ms @ 16kHz)
  int16_t chunk[240];
  size_t samples = readMicrophone(chunk, 240);
  if (samples == 0)
    return;

  // Calculate RMS energy and peak amplitude for this frame
  double sumSq = 0.0;
  int16_t peak = 0;
  for (size_t i = 0; i < samples; i++) {
    double v = (double)chunk[i];
    if (abs(chunk[i]) > peak) peak = abs(chunk[i]);
    sumSq += v * v;
  }
  float rms = (float)sqrt(sumSq / (double)samples);
  _lastRms = rms;

  // 1. Physical Push-To-Talk Button override (if user holds physical button)
  if (_isRecording) {
    _audioFrameCount++;
    if (millis() - _lastLiveVuTime >= 150) {
      _lastLiveVuTime = millis();
      int bars = (int)(rms / 60.0f);
      if (bars > 14) bars = 14;
      String vu = "";
      for (int b = 0; b < 14; b++) vu += (b < bars) ? "#" : ".";
      Serial.printf("[MIC PTT] [%s] RMS:%5.0f | Peak:%5d | Frame:%u\n",
                    vu.c_str(), rms, peak, _audioFrameCount);
    }
    BleManager::getInstance().sendAudioChunk((const uint8_t *)chunk, samples * sizeof(int16_t));
    return;
  }

  // 2. Automatic Hands-Free Voice Activity Detection (VAD)
  if (_vadEnabled) {
    // Dynamic noise floor tracking when quiet (moving average)
    if (!_speechActive && rms < 200.0f) {
      _noiseFloor = (_noiseFloor * 0.96f) + (rms * 0.04f);
      if (_noiseFloor < 20.0f) _noiseFloor = 20.0f;
    }

    const float SPEECH_THRESHOLD = (_noiseFloor * 2.2f > 220.0f) ? (_noiseFloor * 2.2f) : 220.0f;
    const float SILENCE_THRESHOLD = (_noiseFloor * 1.3f > 90.0f) ? (_noiseFloor * 1.3f) : 90.0f;
    const uint32_t SILENCE_TIMEOUT_MS = 1100;
    const uint32_t MAX_SPEECH_MS = 8000;

    if (!_speechActive) {
      // Check for speech trigger (2 consecutive frames above speech threshold)
      if (rms >= SPEECH_THRESHOLD) {
        _consecutiveVoiceFrames++;
        if (_consecutiveVoiceFrames >= 2) {
          triggerVoiceWakeSession();
        }
      } else {
        _consecutiveVoiceFrames = 0;
      }
    } else {
      // Speech session is active -> Stream audio frames
      _audioFrameCount++;
      if (rms >= SILENCE_THRESHOLD) {
        _lastSpeechTime = millis();
      }

      // Stream audio chunk to companion app over BLE
      BleManager::getInstance().sendAudioChunk((const uint8_t *)chunk, samples * sizeof(int16_t));

      // Live VU meter visualizer during speech
      if (millis() - _lastLiveVuTime >= 150) {
        _lastLiveVuTime = millis();
        int bars = (int)(rms / 60.0f);
        if (bars > 14) bars = 14;
        String vu = "";
        for (int b = 0; b < 14; b++) vu += (b < bars) ? "#" : ".";
        Serial.printf("[VAD LIVE] [%s] RMS:%5.0f | Peak:%5d | Speech:%lums\n",
                      vu.c_str(), rms, peak, millis() - _speechStartTime);
      }

      // Check for silence timeout or maximum speech cutoff
      if ((millis() - _lastSpeechTime > SILENCE_TIMEOUT_MS) ||
          (millis() - _speechStartTime > MAX_SPEECH_MS)) {
        stopVoiceWakeSession();
      }
    }
  }
}

// -----------------------------------------------------------------------------
// Direct WAV Recording Helper (for offline / diagnostic testing)
// -----------------------------------------------------------------------------

bool AudioManager::recordWavAudio(uint32_t durationMs, uint8_t **outWavBuffer,
                                  size_t *outWavSize) {
  if (!_micInitialized || outWavBuffer == nullptr || outWavSize == nullptr)
    return false;

  size_t totalPcmSamples = (I2S_MIC_SAMPLE_RATE * durationMs) / 1000;
  size_t pcmDataBytes = totalPcmSamples * sizeof(int16_t);
  size_t totalWavBytes = sizeof(WavHeader) + pcmDataBytes;

  uint8_t *buffer = (uint8_t *)(psramFound() ? ps_malloc(totalWavBytes)
                                             : malloc(totalWavBytes));
  if (!buffer) {
    Serial.println("[AUDIO] ERROR: Insufficient RAM for audio recording buffer.");
    return false;
  }

  WavHeader *header = (WavHeader *)buffer;
  memcpy(header->riff_tag, "RIFF", 4);
  header->riff_size = totalWavBytes - 8;
  memcpy(header->wave_tag, "WAVE", 4);
  memcpy(header->fmt_tag, "fmt ", 4);
  header->fmt_size = 16;
  header->audio_format = 1; // PCM
  header->num_channels = 1; // Mono
  header->sample_rate = I2S_MIC_SAMPLE_RATE;
  header->bits_per_sample = 16;
  header->byte_rate = I2S_MIC_SAMPLE_RATE * 1 * (16 / 8);
  header->block_align = 1 * (16 / 8);
  memcpy(header->data_tag, "data", 4);
  header->data_size = pcmDataBytes;

  int16_t *pcmDst = (int16_t *)(buffer + sizeof(WavHeader));
  size_t samplesRecorded = 0;
  const size_t BATCH = 128;

  uint32_t recStart = millis();
  while (samplesRecorded < totalPcmSamples &&
         (millis() - recStart < durationMs + 500)) {
    size_t toRead = (totalPcmSamples - samplesRecorded > BATCH)
                        ? BATCH
                        : (totalPcmSamples - samplesRecorded);
    size_t got = readMicrophone(pcmDst + samplesRecorded, toRead);
    if (got > 0) {
      samplesRecorded += got;
    }
    delay(4);
  }

  *outWavBuffer = buffer;
  *outWavSize = sizeof(WavHeader) + (samplesRecorded * sizeof(int16_t));
  header->riff_size = (uint32_t)(*outWavSize - 8);
  header->data_size = (uint32_t)(samplesRecorded * sizeof(int16_t));

  return true;
}

void AudioManager::releaseWavBuffer(uint8_t *wavBuffer) {
  if (wavBuffer) {
    free(wavBuffer);
  }
}
