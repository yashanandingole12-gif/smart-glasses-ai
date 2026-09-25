# Qualcomm® AI Hub & Snapdragon® NPU Technical Integration Guide

This guide describes how **EVA** interfaces with the **Qualcomm® AI Hub** and executes INT4/INT8 accelerated models on **Snapdragon®-powered HP PCs** via ONNX Runtime and Qualcomm AI Engine Direct (QNN SDK).

---

## 1. Prerequisites on Snapdragon-Powered HP PC

1. **Operating System:** Windows 11 on ARM64 (HP OmniBook X / HP EliteBook Ultra)
2. **Python:** Python 3.10+ (ARM64 native recommended)
3. **Qualcomm AI Hub CLI:**
   ```bash
   pip install qai-hub
   qai-hub configure --api_token <YOUR_QUALCOMM_AI_HUB_API_KEY>
   ```
4. **ONNX Runtime with QNN Execution Provider:**
   ```bash
   pip install onnxruntime-qnn
   ```

---

## 2. Qualcomm AI Hub Models Compilation Workflow

EVA utilizes pre-compiled Qualcomm AI Hub artifacts optimized for the **Qualcomm Hexagon NPU**:

```bash
# 1. Compile Whisper-Base Speech-to-Text for Hexagon NPU
qai-hub compile \
  --model "whisper_base_en" \
  --device "Snapdragon X Elite CRD" \
  --target_runtime "qnn_context_binary" \
  --output_path "models/whisper_base_qnn.bin"

# 2. Compile MobileNetV4 Vision Backbone
qai-hub compile \
  --model "mobilenet_v4_hybrid_large" \
  --device "Snapdragon X Elite CRD" \
  --target_runtime "qnn_context_binary" \
  --output_path "models/mobilenet_v4_qnn.bin"

# 3. Quantize and Compile Llama-3.2-1B-Instruct (INT4 W4A16)
qai-hub compile \
  --model "llama_v3_2_1b_instruct" \
  --device "Snapdragon X Elite CRD" \
  --options "--quantize_dtype int4 --activations_dtype int8" \
  --target_runtime "qnn_context_binary" \
  --output_path "models/llama3_2_1b_int4_qnn.bin"
```

---

## 3. Python Execution via QNN Execution Provider

In `backend/app/services/snapdragon_npu_engine.py`, ONNX Runtime initializes the Hexagon NPU session:

```python
import onnxruntime as ort

qnn_options = {
    "backend_path": "QnnHtp.dll",  # Qualcomm Hexagon Tensor Processor backend
    "htp_performance_mode": "burst", # Maximum 45 TOPS burst throughput
    "htp_graph_finalization_optimization_mode": "3",
    "enable_htp_fp16_precision": "1"
}

session = ort.InferenceSession(
    "models/whisper_base_qnn.onnx",
    providers=["QNNExecutionProvider", "CPUExecutionProvider"],
    provider_options=[qnn_options, {}]
)
```

---

## 4. API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/v1/snapdragon/status` | `GET` | Reports Hexagon NPU health, TOPS rating, and loaded models |
| `/api/v1/snapdragon/benchmarks` | `GET` | Compares latency and energy metrics (NPU vs CPU vs Cloud) |
| `/api/v1/snapdragon/infer/stt` | `POST` | Executes on-device Hexagon NPU Whisper speech recognition |
| `/api/v1/snapdragon/infer/vision` | `POST` | Executes on-device spatial object detection & OCR |
| `/api/v1/snapdragon/infer/llm` | `POST` | Executes on-device quantized INT4 LLM reasoning |

---

## 5. Verification & Acceptance Testing

Run the automated Snapdragon test suite:

```bash
python -m pytest backend/tests/test_snapdragon_npu_engine.py -v
```
