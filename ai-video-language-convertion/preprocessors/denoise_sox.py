from preprocessors.base import audio_preprocessor
import subprocess
import os
import tempfile

@audio_preprocessor
def denoise_sox(input_path, output_path, output_format, **kwargs):
    """
    Denoise audio using SoX's noisered effect.
    - noise_profile_sec: seconds from start to use as noise profile (default 0.5)
    - reduction_amount: amount of noise reduction (default 0.21)
    """
    noise_profile_sec = kwargs.get('noise_profile_sec', 0.5)
    reduction_amount = kwargs.get('reduction_amount', 0.21)
    
    func_name = denoise_sox.__name__
    
    with tempfile.TemporaryDirectory() as tmpdir:
        noise_profile_wav = os.path.join(tmpdir, f"{func_name}_noise_profile.wav")
        noise_prof = os.path.join(tmpdir, f"{func_name}_noise.prof")
        # Extract noise profile segment
        cmd1 = [
            "sox", input_path, noise_profile_wav, "trim", "0", str(noise_profile_sec)
        ]
        subprocess.run(cmd1, check=True)
        # Generate noise profile
        cmd2 = [
            "sox", noise_profile_wav, "-n", "noiseprof", noise_prof
        ]
        subprocess.run(cmd2, check=True)
        # Apply noise reduction
        cmd3 = [
            "sox", input_path, output_path, "noisered", noise_prof, str(reduction_amount)
        ]
        subprocess.run(cmd3, check=True)

        return output_path
