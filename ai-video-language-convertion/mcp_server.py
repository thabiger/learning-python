import json
import datetime

from fastmcp import FastMCP
from transcribe import Transcription

mcp: FastMCP = FastMCP("audio-llm-pipeline")
LOG_FILE = "/tmp/mcp_server_requests.log"

@mcp.tool
def transcribe(
    input_path,
    output_srt=None,
    preprocess_pipeline=None,
    skip_preprocessing_if_file_exists=False,
    external_vad=None,
    external_vad_params=None,
    model_name="large-v2",
    whisper_params=None,
    whisper_implementation=None
):
    """
    Transcribe audio or video to SRT subtitles using Whisper or WhisperX, with optional preprocessing and VAD.

    Args:
        input_path (str): Path to the input audio or video file.
        output_srt (str, optional): Path to the output SRT file. If None, saves as <input_file>.srt.
        preprocess_pipeline (list[tuple[str, dict]], optional): List of preprocessing steps. Each step is a tuple (processor_name, parameters_dict), where:
                processor_name (str): Name of the preprocessor in the format "module.function", e.g. "normalize.ffmpeg".
                parameters_dict (dict): Dictionary of keyword arguments for the preprocessor.
            Available preprocessors:
                - "normalize.ffmpeg":
                    - presets (list[str]): List of preset names, e.g. ["speach_filters"]
                    - output_format (str): Output audio format, e.g. "wav"
                    - custom (list[str], optional): Custom ffmpeg parameters, e.g. ["-ar", "16000", "-ac", "1"]; Use presets or custom, not both.
                    Exapmles:
                            ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
                            ("normalize.ffmpeg", {"custom": ["-ar", "16000", "-ac", "1"], "output_format": "wav"}),
                - "denoise_nr.reduce_noise":
                    - prop_decrease (float): Noise reduction strength, e.g. 1.0
                    - stationary (bool, optional): Use stationary noise reduction
        skip_preprocessing_if_file_exists (bool, optional): Skip preprocessing if output exists. Default: False.
        external_vad (callable, optional): Optional VAD function. Returns list of timestamp dicts.
        external_vad_params (dict, optional): Parameters for VAD. May include 'preprocess_pipeline' and 'align_pipeline'.
        model_name (str, optional): Whisper model name (e.g., "large-v2"). Default: "large-v2".
        whisper_implementation (str, optional): Backend: 'whisper', 'whisperx', or None (auto).
        whisper_params (dict, optional): Parameters for the backend. See below.

    whisper_params (dict):
        For Whisper (OpenAI):
            - language (str, default: "pl")
            - temperature (float or tuple, default: 0): Sampling temperature(s).
            - compression_ratio_threshold (float, default: 2.4)
            - logprob_threshold (float, default: -1.0)
            - no_speech_threshold (float, default: 0.6)
            - condition_on_previous_text (bool, default: False)
            - word_timestamps (bool, default: False)
            - initial_prompt (str, optional)
            - carry_initial_prompt (bool, default: False)
            - hallucination_silence_threshold (float, optional)
        For WhisperX:
            - asr (dict):
                - compute_type (str, default: "float16")
                - temperatures (list[float], optional): List of fallback temperatures.
                - best_of (int, default: 5)
                - beam_size (int, default: 5)
                - patience (float, default: 1.0)
                - length_penalty (float, default: 1.0)
                - condition_on_previous_text (bool, default: False)
                - fp16 (bool, default: True)
                - temperature_increment_on_fallback (float, default: 0.2)
                - compression_ratio_threshold (float, default: 2.4)
                - log_prob_threshold (float, default: -1.0)
                - no_speech_threshold (float, default: 0.6)
                - initial_prompt (str, optional)
            - language (str, default: "pl")
            - batch_size (int, default: 16)
            - print_progress (bool, default: False)

    Returns:
        str: The full transcribed text.

    Notes:
        - See README for available preprocessors and parameters.
        - Device (CUDA/CPU) is auto-detected.
        - Use `write_srt()` to save subtitles.
        - WhisperX requires `pip install whisperx`.
        - Alignment/diarization are not supported.
        - Backend is selected via `whisper_implementation`.
        - WhisperX is only imported if used.

    Example (Whisper):
        result = transcribe(
            input_path="example_video.mp4",
            preprocess_pipeline=[
                ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
                ("normalize.ffmpeg", {"custom": ["-af", "anlmdn=s=0.001,highpass=f=100,lowpass=f=8000,volume=1.2"], "output_format": "wav"})],
                ("denoise_nr.reduce_noise", {"prop_decrease": 1.0}),
            ],
            external_vad=None,
            external_vad_params={
                "align_pipeline": [("normalize.ffmpeg", {"presets": ["mono16k"], "output_format": "wav"})],
                "preprocess_pipeline": [("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"})],
            },
            skip_preprocessing_if_file_exists=True,
            whisper_params={
                "language": "pl",
                "temperature": 0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.0,
                "no_speech_threshold": 0.6,
                "condition_on_previous_text": False,
                "word_timestamps": False,
                "initial_prompt": "This is a technical lecture about AI."
            },
            model_name="large-v2",
            whisper_implementation="whisper"
        )
        print(result)

    Example (WhisperX):
        result = transcribe(
            input_path="example_video.mp4",
            preprocess_pipeline=[
                ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
                ("denoise_nr.reduce_noise", {"prop_decrease": 1.0}),
            ],
            external_vad=None,
            external_vad_params={
                "align_pipeline": [("normalize.ffmpeg", {"presets": ["mono16k"], "output_format": "wav"})],
                "preprocess_pipeline": [("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"})],
            },
            skip_preprocessing_if_file_exists=True,
            whisper_params={
                "asr": {
                    "beam_size": 5,
                    "patience": 1.0,
                    "length_penalty": 1.0,
                    "temperature": 0,
                    "best_of": 5,
                    "compression_ratio_threshold": 2.4,
                    "logprob_threshold": -1.0,
                    "no_speech_threshold": 0.6,
                    "fp16": True,
                    "temperature_increment_on_fallback": 0.2,
                    "condition_on_previous_text": False,
                    "initial_prompt": "This is a technical lecture about AI."
                },
                "language": "pl",
                "compute_type": "float16",
                "batch_size": 16,
                "print_progress": True
            },
            model_name="large-v2",
            whisper_implementation="whisperx"
        )
        print(result)
    """
    # Log the incoming request and payload
    log_entry = dict(
        timestamp=datetime.datetime.now().isoformat(),
        function="transcribe"
    )
    # Add parameters to log_entry from locals()
    for k in [
        "input_path", "output_srt", "preprocess_pipeline", "external_vad", "external_vad_params",
        "skip_preprocessing_if_file_exists", "whisper_params", "model_name", "whisper_implementation"
    ]:
        log_entry[k] = locals()[k]
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False, indent=2) + "\n")
    except Exception as e:
        print(f"[LOGGING ERROR] {e}")

    # LOCK_FILE = "/tmp/mcp_server.lock"
    # lock_fp = open(LOCK_FILE, "w")
    # try:
    #     fcntl.flock(lock_fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
    # except BlockingIOError:
    #     print("Another instance of MCP tool is already running. Please try again later.")
    #     return "[ERROR] Another instance of MCP server is already running. Please try again later."

    transcription = Transcription(
        input_file=input_path,
        output_srt=output_srt,
        preprocess_pipeline=preprocess_pipeline,
        external_vad=external_vad,
        external_vad_params=external_vad_params,
        skip_preprocessing_if_file_exists=skip_preprocessing_if_file_exists,
        whisper_params=whisper_params,
        model_name=model_name,
        whisper_implementation=whisper_implementation
    )
    transcription.write_srt()

    # Release the lock
    # fcntl.flock(lock_fp, fcntl.LOCK_UN)

    return transcription.full_text()


if __name__ == "__main__":
    mcp.run()


