import requests
import re

OLLAMA_API_URL = "http://localhost:11434/api"
OLLAMA_MODEL = "qwen2.5"

def clean_llm_response(text):
    # Remove everything before and including the last </think> (case-insensitive)
    text = re.sub(r'(?is)^.*</think>', '', text)
    text = text.strip()
    # Remove leading 'Final Answer:', 'Answer:', etc. (case-insensitive, with optional quotes/whitespace)
    text = re.sub(r'^(final answer|answer)\s*:\s*["\']?', '', text, flags=re.IGNORECASE)
    # Remove Markdown bold/italic markers (**, *, __, _)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*(.*?)\*', r'\1', text)        # *italic*
    text = re.sub(r'__(.*?)__', r'\1', text)         # __bold__
    text = re.sub(r'_(.*?)_', r'\1', text)           # _italic_
    # Remove wrapping quotes if present
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    # Collapse multiple blank lines
    text = re.sub(r'\n\s*\n', '\n', text)
    return text.strip()

def call_api(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 600) -> str:
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL + "/generate", json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        summary = result.get("response", "")
        summary = clean_llm_response(summary)
        print(f"[Ollama] Response: {summary}")
        if not summary:
            raise RuntimeError("Ollama API returned an empty response.")
        return summary
    except Exception as e:
        print(f"[Ollama error] {e}")
        raise

def call_chat(messages, model: str = OLLAMA_MODEL, timeout: int = 600) -> str:
    """
    Call Ollama API in chat mode. `messages` should be a list of dicts with 'role' and 'content'.
    Example:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarize this text..."}
        ]
    """
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL + "/chat", json=payload, timeout=timeout)
        response.raise_for_status()
        result = response.json()
        summary = result['message']['content']
        summary = clean_llm_response(summary)
        if not summary:
            raise RuntimeError("Ollama API (chat mode) returned an empty response.")
        print(f"[Ollama] Response: {summary}")
        return summary
    except Exception as e:
        print(f"[Ollama chat error] {e}")
        raise

def stop_all_processes():
    """
    Gracefully stop all running Ollama models using `ollama ps` and `ollama stop`.
    Requires Ollama CLI in PATH.
    """
    import subprocess
    try:
        # Get list of running models
        result = subprocess.run(["ollama", "ps"], capture_output=True, text=True, check=True)
        lines = result.stdout.splitlines()
        model_names = []
        for line in lines[1:]: # Skip the first line (header)
            if line.strip():
                model = line.split()[0]
                model_names.append(model)
        if not model_names:
            print("[Ollama] No running models found.")
            return
        print(f"[Ollama] Stopping models: {model_names}")
        for model in model_names:
            try:
                subprocess.run(["ollama", "stop", model], check=True)
                print(f"[Ollama] Stopped model: {model}")
            except Exception as e:
                print(f"[Ollama] Error stopping model {model}: {e}")
    except Exception as e:
        print(f"[Ollama] Error listing or stopping models: {e}")

