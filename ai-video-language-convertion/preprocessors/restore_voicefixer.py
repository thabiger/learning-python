from preprocessors.base import audio_preprocessor
from voicefixer import VoiceFixer

@audio_preprocessor
def restore_voicefixer(input_path, output_path, output_format, **kwargs):
    voicefixer = VoiceFixer()
    voicefixer.restore(input=input_path, output=output_path, cuda=True, **kwargs)

    return output_path