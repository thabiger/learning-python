from preprocessors.base import audio_preprocessor
import torch
import torchaudio
from speechbrain.pretrained import SepformerSeparation as separator
from speechbrain.pretrained import SpectralMaskEnhancement

def check_mono_16k(waveform, sample_rate, context="SpeechBrain enhancement"):
    """Check if the audio is mono and has a sample rate of 16kHz."""
    if waveform.shape[0] != 1:
        raise ValueError(f"Input audio must be mono (1 channel) for {context}.")
    if sample_rate != 16000:
        raise ValueError(f"Input audio must have a sample rate of 16kHz for {context}.")

@audio_preprocessor
def enhance_speech(input_path, output_path, output_format, **kwargs):
    """Enhance speech using SpeechBrain's speech enhancement model"""
    print(f"Enhancing speech with SpeechBrain: {input_path}")
    
    # Load the speech enhancement model
    enhance_model = SpectralMaskEnhancement.from_hparams(
        source="speechbrain/metricgan-plus-voicebank",
        savedir="pretrained_models/metricgan-plus-voicebank",
        run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
    )
    
    # Load audio with torchaudio (SpeechBrain prefers this)
    waveform, sample_rate = torchaudio.load(input_path)
    
    # Check if audio is mono and has a sample rate of 16kHz
    check_mono_16k(waveform, sample_rate)

    # Enhance the speech
    enhanced_waveform = enhance_model.enhance_batch(waveform, lengths=torch.tensor([1.0]))
    
    # Save enhanced audio
    torchaudio.save(output_path, enhanced_waveform.cpu(), sample_rate)
    print(f"Enhanced speech saved to: {output_path}")

    return output_path

@audio_preprocessor
def separate_speech(input_path, output_path, output_format, **kwargs):
    """Separate speech from background using SpeechBrain's source separation"""
    print(f"Separating speech with SpeechBrain: {input_path}")
    
    # Load the source separation model
    model = separator.from_hparams(
        source="speechbrain/sepformer-wham",
        savedir="pretrained_models/sepformer-wham",
        run_opts={"device": "cuda" if torch.cuda.is_available() else "cpu"}
    )
    
    # Load and process audio
    waveform, sample_rate = torchaudio.load(input_path)
    
    # Check if audio is mono and has a sample rate of 16kHz
    check_mono_16k(waveform, sample_rate)
    
    # Separate sources
    est_sources = model.separate_batch(waveform)
    
    # Take the first separated source (usually the cleanest speech)
    separated_speech = est_sources[:, :, 0]
    
    # Save separated speech
    torchaudio.save(output_path, separated_speech.cpu(), sample_rate)
    print(f"Separated speech saved to: {output_path}")

    return output_path