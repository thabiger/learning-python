from preprocessors.base import audio_preprocessor
import soundfile as sf
import noisereduce as nr
import torch
from noisereduce.torchgate import TorchGate as TG

@audio_preprocessor
def reduce_noise(input_path, output_path, output_format, **kwargs):

    skip_if_exists = kwargs.pop('skip_if_exists', False)

    audio, sr = sf.read(input_path)
    if audio.ndim > 1:
        raise ValueError("Only mono audio is supported.")
    reduced = nr.reduce_noise(y=audio, sr=sr, **kwargs)
    sf.write(output_path, reduced, sr)

    return output_path

@audio_preprocessor
def torchgate(input_path, output_path, output_format, **kwargs):
    import torch
    import numpy as np

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

    audio, sr = sf.read(input_path)
    if audio.ndim > 1:
        raise ValueError("Only mono audio is supported.")

    # Convert audio to torch tensor and add batch dimension
    audio_tensor = torch.from_numpy(audio).float().unsqueeze(0).to(device)  # shape: [1, samples]

    # Create TorchGate instance
    tg = TG(sr=sr, **kwargs).to(device)

    # Apply Spectral Gate to noisy speech signal
    with torch.no_grad():
        enhanced_tensor = tg(audio_tensor)

    # Remove batch dimension and convert back to numpy
    enhanced_audio = enhanced_tensor.squeeze(0).cpu().numpy()

    sf.write(output_path, enhanced_audio, sr)
    return output_path