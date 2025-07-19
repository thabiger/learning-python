import os
import json
import torch
import torchaudio
from collections import OrderedDict
from pydub import AudioSegment
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict

from srt_processing import parse_srt, merge_srt_segments, seconds_to_srt_time

device = "cuda" if torch.cuda.is_available() else "cpu"
model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)

def create_speaker_embedding(input_file: str):
    wav, sr = torchaudio.load(input_file)
    return model.make_speaker_embedding(wav, sr)

def synthesize_with_zonos_api(
    srt_file: str,
    reference_audio: str,
    output_dir: str,
    language: str = "en-us",
    emotion_vector: list = [1.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.5, 1.5],  # Default emotion vector,
    create_aligned_output: bool = False,
    create_alignement_data: bool = False

):
    """
    Synthesize audio from SRT file using Zonos API.
    """
    segments = merge_srt_segments(parse_srt(srt_file))
    # Create speaker embedding from reference audio
    spk_emb = create_speaker_embedding(reference_audio)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    for seg in segments:
        print(f"Generating segment {seg.idx}: '{seg.text[:50]}...' ({seg.start:.3f}s - {seg.end:.3f}s)")

        # Prepare conditioning dictionary
        cond = make_cond_dict(
            text=seg.text,
            language=language,
            speaker=spk_emb,
            emotion=emotion_vector
        )
        conditioning = model.prepare_conditioning(cond)
        codes = model.generate(conditioning)

        wavs = model.autoencoder.decode(codes).cpu()
        
        # Save with timestamp as filename for alignment
        output_filename = os.path.join(output_dir, f"{seg.start:.3f}.wav")
        torchaudio.save(output_filename, wavs[0], model.autoencoder.sampling_rate)
        print(f"Saved: {output_filename}")
    
    # Create timeline-aligned output using Pydub
    if create_aligned_output:
        create_pydub_aligned_output(segments, output_dir)
    
    if create_alignement_data:
        create_ve_alignement_data(segments, output_dir)


def create_ve_alignement_data(segments, output_dir, output_file: str = "alignment_data.json"):

    output_filepath = os.path.join(output_dir, output_file)

    data = []
    for seg in segments:
        entry = {
            "filepath": os.path.join(output_dir, f"{seg.start:.3f}.wav"),
            "trasncription": seg.text,
            "start_time": seconds_to_srt_time(seg.start)
        }
        data.append(entry)
    with open(output_filepath, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved JSON to {output_filepath}")

def create_pydub_aligned_output(segments, output_dir: str, output_file: str = "aligned_output.wav"):
    """Use Pydub to place audio segments at correct timestamps."""
    
    output_filepath = os.path.join(output_dir, output_file)

    # Get total duration in milliseconds
    total_duration_ms = int(segments[-1].end * 1000)
    
    # Create silent audio track
    final_audio = AudioSegment.silent(duration=total_duration_ms)
    
    for seg in segments:
        seg_file = f"{seg.start:.3f}.wav"
        seg_path = os.path.join(output_dir, seg_file)
        
        if os.path.exists(seg_path):
            try:
                # Load the audio segment
                audio_segment = AudioSegment.from_wav(seg_path)
                
                # Calculate position in milliseconds
                start_ms = int(seg.start * 1000)
                
                # Overlay the segment at the correct position
                final_audio = final_audio.overlay(audio_segment, position=start_ms)
                print(f"Placed segment at {seg.start:.3f}s")
                
            except Exception as e:
                print(f"Error processing {seg_path}: {e}")
        else:
            print(f"Warning: {seg_path} not found")
    
    # Export the final audio
    final_audio.export(output_file, format="wav")
    print(f"Pydub aligned audio saved to: {output_file}")
            
emotion_od = OrderedDict([
    ("happiness", 1.0),
    ("sadness",   0.0),
    ("disgust",   0.0),
    ("fear",      0.0),
    ("surprise",  0.5),
    ("anger",     0.0),
    ("other",     0.5),
    ("neutral",   1.5),
])
emotion_vector = list(emotion_od.values())

synthesize_with_zonos_api(
    srt_file="Wideo/VID20250619100726_cfr_rotated.srt_translated", 
    reference_audio="Wideo/l.wav", 
    output_dir="output_audio",
    emotion_vector=emotion_vector,
    create_aligned_output=True,
    create_alignement_data=True
)


