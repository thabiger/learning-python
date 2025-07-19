from preprocessors.base import audio_preprocessor
import subprocess

@audio_preprocessor
def ffmpeg(input_path, output_path, output_format, **kwargs):

    args = []

    #ready made presets
    preset_settings = {
        'mono16k':        ["-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le"],
        'mono16knorm':    ["-ar", "16000", "-ac", "1", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "pcm_s16le"],
        '44k1':           ["-ar", "44100", "-c:a", "pcm_s16le"],
        'speach_filters_hq': ["-af", "highpass=f=80,lowpass=f=9000,loudnorm=I=-16:TP=-1.5:LRA=11"],
        'speach_filters': ["-ac", "1", "-af", "highpass=f=300,lowpass=f=3400,loudnorm=I=-16:TP=-1.5:LRA=11"]        
    }

    presets = kwargs.get('presets', {})

    for p in presets:
        args += preset_settings[p]

    if 'custom' in kwargs:
        args += kwargs['custom']

    cmd = ["ffmpeg", "-y", "-i", input_path] + args + [output_path]
    print(cmd)
    subprocess.run(cmd, check=True)

    return output_path