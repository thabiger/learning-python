from preprocessors.base import audio_preprocessor
import soundfile as sf
import torch
from demucs.apply import apply_model
from demucs.pretrained import get_model as get_demucs_model

@audio_preprocessor
def extract_vocals_demucs(input_path, output_path, output_format, **kwargs):
        
    # Demucs expects 44.1kHz, stereo
    wav, sr = sf.read(input_path)
    if wav.ndim != 2:
        raise ValueError(f"Demucs requires stereo audio (2 channels). Got shape: {wav.shape}")
    if sr != 44100:
        raise ValueError(f"Demucs requires 44.1kHz sample rate. Got: {sr}")
    
    # Convert to tensor with correct shape: (batch, channels, length)
    wav_tensor = torch.tensor(wav.T, dtype=torch.float32).unsqueeze(0)
    print(f"Tensor shape for Demucs: {wav_tensor.shape}")
    
    # Load model and separate sources
    model = get_demucs_model("htdemucs")
    with torch.no_grad():
        sources = apply_model(model, wav_tensor, device="cuda")
        vocals = sources[0][model.sources.index("vocals")].cpu().numpy()
    
    # Convert back to (time, channels) format
    vocals = vocals.T   
    sf.write(output_path, vocals, sr)
    return output_path