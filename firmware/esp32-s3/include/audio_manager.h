#pragma once

#include "board_config.h"
#include <Arduino.h>

enum class SoundEffect {
  SOUND_WAKE,
  SOUND_AI_RESPONSE,
  SOUND_MESSAGE_ALERT,
  SOUND_CALL_INCOMING,
  SOUND_SUCCESS,
  SOUND_ERROR,
  SOUND_DEVICE_CONNECTED,
  SOUND_DEVICE_DISCONNECTED,
  SOUND_PTT_START,
  SOUND_PTT_STOP
};

class AudioManager {
public:
  static AudioManager &getInstance() {
    static AudioManager instance;
    return instance;
  }

  bool init();
  bool initMicrophone();
  bool initSpeaker();

  // Microphone Recording & Live Diagnostics
  void startMicrophone();
  void stopMicrophone();
  size_t readMicrophone(int16_t *buffer, size_t maxSamples);
  float getAudioLevelRMS();
  void runMicrophoneDiagnostic(uint32_t durationMs = 3000);
  void runVoiceLoopbackTest(uint32_t durationMs = 3500);

  // Direct WAV Audio Recording from ESP32 Digital Mic (INMP441)
  bool recordWavAudio(uint32_t durationMs, uint8_t **outWavBuffer,
                      size_t *outWavSize);
  void releaseWavBuffer(uint8_t *wavBuffer);

  // Speaker Playback & Audio Stream Receiving (MAX98357A)
  void playTone(uint16_t freqHz, uint32_t durationMs);
  void playMelody(const uint16_t *freqs, const uint16_t *durationsMs,
                  size_t count);
  void playSound(SoundEffect effect);
  void playPcmAudio(const int16_t *samples, size_t sampleCount,
                    uint32_t sampleRate = I2S_SPK_SAMPLE_RATE);
  void playWavAudio(const uint8_t *wavBytes, size_t wavLength);
  void streamPcmChunk(const uint8_t *pcmChunk, size_t chunkSize);
  void stopPlayback();
  void runSpeakerDiagnostic();
  void runFullAudioDiagnostic();

  // Volume Control (0 - 100%)
  void setVolume(uint8_t volumePercent);
  uint8_t getVolume() const { return _volume; }

  void update();
  bool isRecording() const { return _isRecording; }
  bool isInitialized() const { return _micInitialized; }
  bool isSpeakerInitialized() const { return _speakerInitialized; }
  float getLastRms() const { return _lastRms; }

  // Push-To-Talk & Voice Wake Session Controls
  void setVadEnabled(bool enabled) { _vadEnabled = enabled; }
  bool isVadEnabled() const { return _vadEnabled; }
  void triggerVoiceWakeSession();
  void stopVoiceWakeSession();

private:
  AudioManager();
  bool _micInitialized = false;
  bool _speakerInitialized = false;
  bool _isRecording = false;
  uint8_t _volume = 85; // Default 85% volume for clear loudness
  uint32_t _lastDiagnosticTime = 0;
  uint32_t _audioFrameCount = 0;
  uint32_t _lastLiveVuTime = 0;
  float _lastRms = 0.0f;

  // Hands-free VAD (Enabled by default for hands-free voice operation)
  bool _vadEnabled = true;
  bool _speechActive = false;
  float _noiseFloor = 80.0f;
  uint32_t _speechStartTime = 0;
  uint32_t _lastSpeechTime = 0;
  uint8_t _consecutiveVoiceFrames = 0;
};
