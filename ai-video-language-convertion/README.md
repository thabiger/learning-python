### Transcribing

The most simple usage is to transcrie the movie without eny extra processing with OpenAI Whisper.

transcribe_movie(movie_file)

You can add some extra audio preprocessing that will enhence the audio before transcribing. You can define pipelines using different preprocessors like this:

PREPROCESSING_PIPELINE: list[tuple[Any, dict]] = [
    ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
    ("denoise_sox", {'noise_profile_seconds': 0.5, 'reduction_amount': 0.21}),

]

and than use it:

transcribe_movie(movie_file, 
                    output_srt, 
                    preprocess_pipeline=PREPROCESSING_PIPELINE,
                    skip_if_exists=True
                )

Transcribe method supports external VADs as well. This lets to split original audio into smaller segments and process them separately. It may be useful when trying to process larger files with AI models with tools like speechbrain, that won't fit in memory otherwise:

transcribe_movie(movie_file, 
                    output_srt, 
                    preprocess_pipeline=PREPROCESSING_PIPELINE,
                    external_vad="vad_silero.get_speach_timestamps,
                    external_vad_args={
                        'min_speech_duration_ms': 500,
                        'min_silence_duration_ms': 500,
                        'speech_pad_ms': 250
                    },
                    external_vad_preprocess_pipeline=VAD_PREPROCESSING_PIPELINE,
                    skip_if_exists=True)

The main role of an external VAD is to detect and mark speech segments with a timestamps. Since VAD mah have certain requirements to the audio input (like silero that reuires it to be 16k mono), you may want to process the audio file only for the sake of VAD processing and use timestamps to cut the original audio without loosing it's quality. Therefere additional external_vad_preprocess_pipeline argument exists, that appliese only to the VAD stage.

Whisper params

You can also pass whipser parameter to adjust the work of whipser:

    transcribe_movie(movie_file, 
                     whisper_params={
                        "temperature": 0.0,
                        "compression_ratio_threshold": 2.0,
                        "logprob_threshold": -0.5,
                        "no_speech_threshold": 0.2,
                        "condition_on_previous_text": False,
                        "word_timestamps": False # or True if you want word-level timing
                        })

Full example:

    transcribe_video(movie_file, 
                     output_srt, 
                     preprocess_pipeline=PREPROCESSING_PIPELINE_2,
                     external_vad=preprocessors.vad_silero.get_speach_timestamps,
                     external_vad_args={
                        'min_speech_duration_ms': 500,
                        'min_silence_duration_ms': 500,
                        'speech_pad_ms': 250
                     },
                     external_vad_preprocess_pipeline=PREPROCESSING_PIPELINE_7,
                     skip_if_exists=True,
                     whisper_params={
                        "temperature": 0.0,
                        "compression_ratio_threshold": 2.0,
                        "logprob_threshold": -0.5,
                        "no_speech_threshold": 0.2,
                        "condition_on_previous_text": False,
                        "word_timestamps": False # or True if you want word-level timing
                        })

#### Preprocessors

The following preprocessors are available to use in the pipelines at this moment:

- **normalize.ffmpeg**: Flexible normalization and resampling using ffmpeg. Supports presets for mono 16kHz, 44.1kHz, and speech filtering (bandpass, loudness normalization).
- **denoise_sox**: Classical denoising using SoX's noisered effect. Requires a noise profile from the start of the file.
- **denoise_nr.reduce_noise**: Non-AI spectral gating denoising using the noisereduce library (stationary and non-stationary noise supported).
- **denoise_nr.torchgate**: PyTorch-based spectral gating denoising (TorchGate, GPU-accelerated if available).
- **extract_vocals_demucs**: AI-based vocal extraction using Demucs (requires stereo 44.1kHz input).
- **restore_voicefixer**: AI-based speech restoration using VoiceFixer (removes artifacts, enhances clarity).
- **speechbrain.enhance_speech**: AI-based speech enhancement (denoising, dereverberation) using SpeechBrain (requires mono 16kHz input).
- **speechbrain.separate_speech**: AI-based source separation (speech from background) using SpeechBrain (requires mono 8kHz input).
- **vad_silero**: Voice Activity Detection (VAD) using Silero VAD, returns speech segment timestamps (requires mono 16kHz input, parameters adjustable).

Each preprocessor can be used standalone or as part of a pipeline. See below for example pipelines and usage.

#### Examples

These are some basic examples of different pipelines:

    PREPROCESSING_PIPELINE_1: list[tuple[Any, dict]] = [
        ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
        ("denoise_sox", {'noise_profile_seconds': 0.5, 'reduction_amount': 0.21}),
    ]

    PREPROCESSING_PIPELINE_2: list[tuple[Any, dict]] = [
        ("normalize.ffmpeg", {"presets": ["speach_filters", "mono16k"], "output_format": "wav"}),
        ("denoise_nr.reduce_noise", {'stationary': False}),
    ]

    PREPROCESSING_PIPELINE_3: list[tuple[Any, dict]] = [
        ("normalize.ffmpeg", {"presets": ["speach_filters", "mono16k"], "output_format": "wav"}),
        ("denoise_nr.torchgate", {'nonstationary': True}),
    ]

    PREPROCESSING_PIPELINE_4: list[tuple[Any, dict]] = [
        ("normalize.ffmpeg", {"presets": ["speach_filters", "44k1"], "output_format": "wav"}),
        ("extract_vocals_demucs", {}),
    ]

    PREPROCESSING_PIPELINE_5: list[tuple[Any, dict]] = [
        ("normalize.ffmpeg", {"presets": ["speach_filters"], "output_format": "wav"}),
        ("restore_voicefixer", {'mode': 0}),
    ]

    PREPROCESSING_PIPELINE_6: list[tuple[Any, dict]] = [
        ("speechbrain.enhance_speech", {}),
        ("speechbrain.separate_speech", {}),
    ]
