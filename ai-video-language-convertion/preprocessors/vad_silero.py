from preprocessors.base import audio_preprocessor
import torch
import soundfile as sf
import silero_vad

def get_speach_timestamps(input_path, **kwargs):

    args = {
        'min_speech_duration_ms': 500,
        'min_silence_duration_ms': 500,
        'speech_pad_ms': 250,
        'return_seconds': True
    }
    args.update(kwargs)

    wav, sr = sf.read(input_path)
    wav_tensor = torch.tensor(wav, dtype=torch.float32)
    model = silero_vad.load_silero_vad()
    speech_timestamps = silero_vad.get_speech_timestamps(wav_tensor, model, sampling_rate=sr, **args)
    
    return speech_timestamps