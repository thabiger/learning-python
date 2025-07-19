import sys
from typing import Any

import ollama
from transcribe import Transcription
from srt_processing import extend_w_llm
from translate import translate_srt

ollama.OLLAMA_API_URL = "http://localhost:11434/api"
ollama.OLLAMA_MODEL = "deepseek-r1:14b"

PREPROCESSING_PIPELINE: list[tuple[Any, dict]] = [
    ("normalize.ffmpeg", {"output_format": "wav", "custom": ["-af", "highpass=f=50,lowpass=f=10000,volume=1.2,anlmdn=s=0.001:p=0.003:r=0.01"]})
    #("normalize.ffmpeg", {"presets": ["mono16knorm"], "output_format": "wav"}), 
    # this presets is actually: "-ar 16000 -ac 1 -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:apcm_s16le
]

WHISPER_PARAMS = {
    'WHISPER': {
        "temperature": [0.1, 0.3, 0.5, 0.7],
        "compression_ratio_threshold": 2.1,
        "logprob_threshold": -0.85,
        "no_speech_threshold": 0.45,
        "condition_on_previous_text": False,
        "word_timestamps": False # or True if you want word-level timing
                },
    'WHISPERX': {
        "print_progress": True,
        "asr": {
            "beam_size": 15,
            "patience": 1.5,
            "compression_ratio_threshold": 2.4,
            "log_prob_threshold": -1,
            "no_speech_threshold": 0.6
        }
    }
}

def main():

    whisper_implementation = "whisperx"  # or "whisper" for OpenAI Whisper

    t = Transcription(
        movie_file,
        second_pass=True,
        skip_preprocessing_if_file_exists=True,
        whisper_implementation=whisper_implementation,
        whisper_params=WHISPER_PARAMS.get(whisper_implementation.upper(), WHISPER_PARAMS['WHISPER']),
        preprocess_pipeline=PREPROCESSING_PIPELINE,
    )
    t.write_srt()

    # Correct the SRT file with LLM context
    llm_extended_srt = extend_w_llm(t.output_srt, window=7.0, language="polish")
    # Translate the SRT file
    translate_srt(llm_extended_srt, method='marian')
    

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <movie_file> [output_srt]")
    else:
        movie_file = sys.argv[1]
        output_srt = sys.argv[2] if len(sys.argv) > 2 else None

    main()