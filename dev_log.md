# GAIA Development Log

## 2025-07-19

### Issue: Segmentation Fault in `llama_cpp`

*   **Symptoms:** The application crashes with a `Segmentation fault` when running a prompt. The traceback points to `app/cognition/external_voice.py` and the `llama_cpp` library.
*   **Hypothesis:** The crash is caused by multi-threaded access to the `llama_cpp` library from the `ExternalVoice` class.
*   **Fix Applied:** Modified `app/cognition/external_voice.py` to remove the worker thread and queue, making the call to `create_chat_completion` a direct, single-threaded operation.
*   **Status:** `Pending Validation`

### Issue: JSON Decoding Error in `CognitiveDispatcher`

*   **Symptoms:** A `WARNING` message in the logs indicates that the 'lite' model is not returning a valid JSON object.
*   **Hypothesis:** The 'lite' model is not reliably following the instruction to return a JSON object, and the regex used to extract the JSON is not robust enough.
*   **Fix Applied:** Modified `app/cognition/cognitive_dispatcher.py` to use a more flexible regex that can handle cases where the JSON is embedded in other text.
*   **Status:** `Pending Validation`
