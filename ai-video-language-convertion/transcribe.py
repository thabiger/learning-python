import os
import preprocessors
from typing import Any
import torch

from av_preprocessing import preprocess_w_pipeline
from srt_processing import seconds_to_srt_time, get_broad_context

class Transcription():
    """
    High-level transcription interface for audio/video to SRT subtitles using Whisper or WhisperX.

    This class provides an object-oriented interface for transcribing audio or video files to SRT subtitles, supporting both OpenAI Whisper and WhisperX backends. All parameters accepted by `transcribe_video` can be passed to this class.

    Args:
        input_file (str): Path to the input audio or video file to be transcribed.
        output_srt (str | None, optional): Path to the output SRT file. If None, the output will be saved as <input_file>.srt.
        second_pass (bool, optional): If True, enables a second pass using LLM-based context correction. Default is False.
        preprocess_pipeline (list[tuple[str, dict]] or None, optional): List of preprocessing steps to apply before transcription.
            Each step is a tuple of (processor_name, parameters_dict), where:
                processor_name (str): Name of the preprocessor in the format "module.function", e.g. "normalize.ffmpeg".
                parameters_dict (dict): Dictionary of keyword arguments for the preprocessor.
            See the "Preprocessors" section in the README for more details and available options.
        skip_preprocessing_if_file_exists (bool, optional): If True, skips adio preprocessing steps if an audio output file already exists. Default is False.
        external_vad (callable or None, optional): Optional external Voice Activity Detection function. If provided, it should return a list of timestamp dicts with 'start' and 'end' keys.
        external_vad_params (dict or None, optional): Dictionary of parameters for the external VAD function. May include:
            - Any keyword arguments required by your VAD function.
            - preprocess_pipeline (list[tuple[str, dict]], optional): Preprocessing pipeline to apply to each VAD-detected segment before transcription.
            - align_pipeline (list[tuple[str, dict]], optional): Preprocessing pipeline to align audio for VAD (e.g., resampling).
        model_name (str, optional): Name of the Whisper model to use (e.g., "large-v2", "base", etc.). Default is "large-v2". The device (CUDA or CPU) is detected automatically.
        whisper_params (dict or None, optional): Additional parameters to pass to the Whisper or WhisperX implementation's transcribe method. See below for details.
        whisper_implementation (str or None, optional): Which backend to use: 'whisper', 'whisperx', or None (auto-detect/default).

    Whisper Parameters(by implementation):
        whisper_params (dict):
            Whisper-specific options:
                language (str, optional): Language code for transcription (e.g., "pl" for Polish, "en" for English). Default is "pl".
                temperature (float | tuple[float, ...]): Sampling temperature(s). 0 for deterministic output.
                compression_ratio_threshold (float): If the gzip compression ratio is higher than this value, treat as hallucination.
                logprob_threshold (float): If the average log probability is lower than this value, treat as hallucination.
                no_speech_threshold (float): If the probability of no speech is higher than this value AND the average log probability is below logprob_threshold, consider segment as no-speech.
                condition_on_previous_text (bool): If True, provide the previous output as a prompt for the next window.
                word_timestamps (bool): If True, return word-level timestamps.
                initial_prompt (str): Optional text to provide as a prompt for the first window.
                carry_initial_prompt (bool): If True, `initial_prompt` is prepended to the prompt of each internal `decode()`.
                hallucination_silence_threshold (float): When word_timestamps is True, skip silent periods longer than this threshold (in seconds).
            WhisperX-specific options:
                asr (dict):
                    beam_size (int): Beam search size (default: 5)
                    patience (float): Beam search patience (default: 1.0)
                    length_penalty (float): Beam search length penalty (default: 1.0)
                    temperatures (list[float]): List of temperatures for fallback decoding.
                    compression_ratio_threshold (float): If the gzip compression ratio is higher than this value, treat as hallucination.
                    log_prob_threshold (float): If the average log probability is lower than this value, treat as hallucination.
                    no_speech_threshold (float): If the probability of no speech is higher than this value AND the average log probability is below log_prob_threshold, consider segment as no-speech.
                    condition_on_previous_text (bool): If True, provide the previous output as a prompt for the next window.
                    initial_prompt (str): Optional text to provide as a prompt for the first window.
                    suppress_tokens (list[int]): List of token IDs to suppress.
                    suppress_numerals (bool): Whether to suppress numerals.
                language (str, optional): Language code for transcription (e.g., "pl" for Polish, "en" for English). Default is "pl".
                batch_size (int, optional): Batch size for transcription (default: 16)
                compute_type (str, optional): Computation type ("float16", "int8", default: "float16")
                print_progress (bool, optional): Print progress during transcription (default: False)
                compute_type (str, optional): Computation type for WhisperX (e.g., "float16", "int8").

    Notes:
        - For a detailed description of available preprocessors and their parameters, see the "Preprocessors" section in the README.
        - The device (CUDA or CPU) is detected automatically.
        - Use `write_srt()` to save the subtitles to the output SRT file.
        - WhisperX support requires separate installation (`pip install whisperx`).
        - Alignment and diarization features have been removed; only transcription is supported.
        - The backend (Whisper or WhisperX) is selected via the `whisper_implementation` argument.
        - All imports for WhisperX are performed inside methods to avoid unnecessary dependencies unless used.

    Examples:

        # Example with standard OpenAI Whisper implementation

        result = Transcription(
            audio_path="example_video.mp4",
            preprocess_pipeline = [
                ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
                ("denoise_nr.reduce_noise", {"prop_decrease": 1.0}),
            ],
            preprocess_pipeline=preprocess_pipeline,
            external_vad=None,  # or your VAD function
            external_vad_params={
                align_pipeline: [("normalize.ffmpeg", {"presets": ["mono16k"], "output_format": "wav"})],
                preprocess_pipeline: [("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"})],
            skip_if_exists=True,
            whisper_params = {
                "language": "pl",
                "temperature": 0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.5,
                "no_speech_threshold": 0.5,
                "condition_on_previous_text": False,
                "word_timestamps": False,
                "initial_prompt": "This is a technical lecture about AI.",
            },
            model_name="large-v2"
        )
        
        # Example with WhisperX and asr_options

        result = Transcription(
            input_file="example_video.mp4",
            preprocess_pipeline=[
                ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
                ("denoise_nr.reduce_noise", {"prop_decrease": 1.0}),
            ],
            external_vad=None,  # or your VAD function
            external_vad_params={
                "align_pipeline": [("normalize.ffmpeg", {"presets": ["mono16k"], "output_format": "wav"})],
                "preprocess_pipeline": [("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"})],
            },
            skip_preprocessing_if_file_exists=True,
            whisper_params={
                "language": "pl",
                "temperature": 0,
                "compression_ratio_threshold": 2.4,
                "logprob_threshold": -1.5,
                "no_speech_threshold": 0.5,
                "condition_on_previous_text": False,
                "word_timestamps": False,
                "initial_prompt": "This is a technical lecture about AI.",
                "asr": {
                    "beam_size": 5,
                    "patience": 1.0,
                    "length_penalty": 1.0,
                    "temperatures": [0.0, 0.2, 0.4],
                    "compression_ratio_threshold": 2.4,
                    "log_prob_threshold": -1.5,
                    "no_speech_threshold": 0.5,
                    "condition_on_previous_text": False,
                    "initial_prompt": "This is a technical lecture about AI.",
                    "suppress_tokens": [1, 2, 3],
                    "suppress_numerals": False,
                },
                "compute_type": "float16",
                "batch_size": 16,
                "print_progress": True,
            },
            model_name="large-v2",
            whisper_implementation="whisperx"
        )
        result.write_srt()
    """

    def __init__(self,
        input_file: str,
        output_srt: str | None = None,
        second_pass: bool = False,
        preprocess_pipeline=None,
        skip_preprocessing_if_file_exists=False,
        external_vad=None,
        external_vad_params=None,
        model_name: str = "large-v2",
        whisper_params= None,
        whisper_implementation: str = None,  # 'whisper' or 'whisperx'
        ):

        self.input_file = input_file
        self.output_srt = output_srt
        self.second_pass = second_pass
        self.preprocess_pipeline = preprocess_pipeline or []
        self.skip_preprocessing_if_file_exists = skip_preprocessing_if_file_exists

        self.external_vad = external_vad
        self.external_vad_params = external_vad_params or {}
        
        self.data = None
        self.segments = None
        self.description = None

        # if path for srt not provided, make it after video file name
        if output_srt is None:
            base, _ = os.path.splitext(input_file)
            self.output_srt = base + ".srt"
        else:
            self.output_srt = output_srt

        # Pick the Whisper executor based on the implementation type
        whisper_executor = self.set_up_executor(whisper_implementation, model_name, whisper_params.copy())
        self.segments = self.transcribe(whisper_executor)
        del whisper_executor  # Clean up executor to free memory

        if second_pass:
            video_context = get_broad_context(self.full_text())
            initial_prompt = f"This video you're transcribing is about: {video_context}. Use this knowledge for accurate transcription, especially for names and key terms."

            if whisper_params.get("asr"):
                whisper_params["asr"]["initial_prompt"] = initial_prompt
                whisper_params["asr"]["condition_on_previous_text"] = True
            else:
                whisper_params["initial_prompt"] = initial_prompt
                whisper_params["condition_on_previous_text"] = True

            whisper_executor = self.set_up_executor(whisper_implementation, model_name, whisper_params.copy())
            self.segments = self.transcribe(whisper_executor, skip_preprocessing_if_file_exists=True)

    def full_text(self):
        return " ".join([text for (_, _, text) in self.segments])
    
    def write_srt(self):
        with open(self.output_srt, "w", encoding="utf-8") as srt_file:
            for i, (start, end, text) in enumerate(self.segments, start=1):
                srt_file.write(f"{i}\n{start} --> {end}\n{text}\n\n")
        print(f"✅ Transcription complete. Subtitles saved to: {self.output_srt}")

        return self.output_srt

    def transcribe(self, whisper_executor, skip_preprocessing_if_file_exists=None):
        """ Transcribes the input audio or video file using the provided Whisper executor."""

        if skip_preprocessing_if_file_exists is None:
            skip_preprocessing_if_file_exists = self.skip_preprocessing_if_file_exists
        else:
            skip_preprocessing_if_file_exists = skip_preprocessing_if_file_exists

        segments = []

        # run preprocessing pipeline if provided
        if self.preprocess_pipeline:
            self.processed_audio = preprocess_w_pipeline(self.input_file, self.preprocess_pipeline, skip_preprocessing_if_file_exists, {})
        else:
            self.processed_audio = self.input_file

        if self.external_vad:

            # im copying external vad params to modify them according to the process requirements
            external_vad_params = self.external_vad_params.copy()

            external_vad_preprocess_pipeline = external_vad_params.pop("preprocess_pipeline", None)
            external_vad_align_pipeline = external_vad_params.pop("align_pipeline", None)

            # if vad require some preprocessing to allign with it's reuirements, do it here
            # e.g. silero vad requires 16kHz mono audio
            # the reason for a separate process is to use it only to rcognize timestamps and not necessarily affect the audio quality
            # used for the further processing
            if external_vad_align_pipeline:
                timestamps = self.external_vad(preprocess_w_pipeline(self.processed_audio, external_vad_align_pipeline, self.skip_if_exists, {}), **external_vad_params)
            else:
                timestamps = self.external_vad(self.processed_audio, **external_vad_params)

            for ts in timestamps:
                # First, we need to cut the audio segment based on the VAD timestamps
                VAD_CUTTING_PIPELINE: list[tuple[Any, dict]] = [
                    (preprocessors.normalize.ffmpeg, {"custom": ["-ss", str(ts['start']), "-to", str(ts['end'])], "output_format": "wav"}),
                ]
                seg_path = preprocess_w_pipeline(self.processed_audio, VAD_CUTTING_PIPELINE, False, {})

                # Then we can apply any additional preprocessing if provided
                if external_vad_preprocess_pipeline:
                    seg_path = preprocess_w_pipeline(seg_path, external_vad_preprocess_pipeline, False, {})

                # Finally transcribe the segment and collect the results
                result = whisper_executor.transcribe(seg_path)
                if segments_found := get_transcribed_segments(result, ts['start']):
                    segments.extend(segments_found)
        else:
            result = whisper_executor.transcribe(self.processed_audio)
            segments = get_transcribed_segments(result)
        
        return segments
    
    def set_up_executor(self, whisper_implementation: str | None = None, model_name: str = "large-v2", whisper_params=None):
        """
        Returns the appropriate Whisper executor based on the implementation type.
        """

        whisper_params = whisper_params or {}

        match whisper_implementation:
            case "whisperx":
                return WhisperxExecutor(model_name=model_name, whisper_params=whisper_params)
            case _:
                return WhisperExecutor(model_name=model_name, whisper_params=whisper_params)

class Executor():

    def __init__(self, model_name: str = "large-v2", whisper_params=None):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self._whisper_params = whisper_params or {}

        self.model = self._init_model_implementation()

    def _init_model_implementation(self):
        pass
        
    def transcribe(self, audio_path, **whisper_params): 
        pass

class WhisperExecutor(Executor):

    def _init_model_implementation(self):
        import whisper  # type: ignore
        return whisper.load_model(self.model_name, device=self.device)

    def transcribe(self, audio_path, **whisper_params):
        args = whisper_params or self._whisper_params
        return self.model.transcribe(audio_path, **args)

class WhisperxExecutor(Executor):

    def _init_model_implementation(self):
        import whisperx  # type: ignore
        self.load_audio = whisperx.load_audio  # type: ignore
        return whisperx.load_model(
            self.model_name,
            self.device,
            compute_type=self._whisper_params.pop("compute_type", "float16"),
            asr_options=self._whisper_params.pop("asr", {})
        )

    def transcribe(self, audio_path, **whisper_params):
        args = whisper_params or self._whisper_params
        audio = self.load_audio(audio_path)
        return self.model.transcribe(audio, **args)

    def __del__(self):
        # Clean up model and GPU memory if needed
        if hasattr(self, 'model'):
            del self.model
        import gc
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

def get_transcribed_segments(r, seg_start = 0):
    entries = []
    for segment in r["segments"]:
        start = seconds_to_srt_time(segment["start"] + seg_start)
        end = seconds_to_srt_time(segment["end"] + seg_start)
        text = segment["text"].strip()
        entries.append((start, end, text))
    return entries