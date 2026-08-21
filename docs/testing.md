# Smart Glasses AI Assistant - Testing & Verification

## Running Automated Test Suite
From the repository root (`smart-glasses-ai/`):

```bash
pytest -v tests/
```

### Test Coverage
- `tests/test_context_engine.py`: Validates diurnal period calculation, time formatting, location merging, and calendar integration.
- `tests/test_tool_registry.py`: Validates parameter introspection, tool registration, execution, and confirmation flags.
- `tests/test_llm_service.py`: Tests LLM provider abstraction, fallback responses, and tool call generation.
- `tests/test_langgraph_agent.py`: Validates LangGraph state machine, tool resolution cycles, and conversational memory across turns.
- `tests/test_fastapi_endpoints.py`: Validates `/health`, `/session`, `/agent/message`, `/vision/analyze`, and latency tracking.
- `tests/test_end_to_end.py`: Tests full push-to-talk voice flow simulation:
  `Button Press -> STT -> Context Engine -> LangGraph Agent -> Response -> TTS`.
