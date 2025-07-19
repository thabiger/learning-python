

## Objective

By running subsequent transcription attempts and assigning scores, systematically determine the optimal parameters for the most accurate and error-free transcription of  
`Wideo/VID20250619100726_cfr_rotated.mp4`  
using the transcribe MCP. You may perform up to **200 transcription executions** to find the best configuration.

## Constraints

- Follow all instructions in this document precisely. No deviations from the specified rules or workflow are permitted under any circumstances.
- The following MCP arguments must never be changed:
    - `model="large-v2"`
    - `skip_if_exists=True`
    - `second_pass=False`
    - `external_vad=None`
    - `whisper_implementation=whisperx`
    - `whisper_params.language=pl`
    - `whisper.print_progress=False`
- Analyze the parameters that mcp tool can take; stick to the subset for ffmpeg and whipserx only. Please take into a careful consideration what parameters goes directly under whisper_params and what under asr subdictionary.
- If the MCP server does not return an explicit error, assume the operation was successful regardless of the output.

## Scoring

Each transcription attempt should be automatically scored from **0 to 100** based on:
1. The overall number of errors in the transcription.
2. Whether the lines follow the broad context of the text and make sense.
3. The absence of hallucinations and repetitions.
4. Perform scoring with great care to distinguish even the smallest nuances in the results.

## Logging and Output

Each parameter set test case must follow these rules for logging and storing results:

- Store all results in a separate folder named `Wideo/test-{date}-{time}`.
- For each test case:
    - Assign a unique attempt number and name.
    - Save the resulting SRT files along with a corresponding `.info` file containing:
        - The parameters used.
        - The assigned score.
        - The full JSON object with parameters passed to the transcribe tool.
- Log all parameter sets and their results in a common log file, updating it after finishing testing each case.

## Workflow

### Stage 1: Media Analysis
- Gather information about the input media file to avoid unnecessary preprocessing that could degrade its original properties (e.g., sampling rate).

### Stage 2: Baseline Test
- Run a baseline transcription with minimal parameters to establish a reference point.

### Stage 3: Audio Quality Optimization
- Experiment with various FFmpeg preprocessing options to enhance speech clarity.
- **Do not** use any preprocessors other than FFmpeg.
- Prefer custom FFmpeg settings to enhance speech audio quality, rather than relying on presets.
- Start with parameters that preserve the file's original quality (e.g., sample rate, bit rate), then try lower values.

### Stage 4: Whisper Parameter Tuning

Perform this stage in three steps:

1. Systematically perform transcription attempts with all available WhisperX parameters from the MCP tool documentation to observe their impact on transcription quality.
2. Run subsequent transcription attempts with iterative adjustments of individual parameters to gain deeper insight into their effects.
3. Use insights from previous tests to identify and select the parameter set that achieves the highest scores.
3. Note that for temperatures other than 0, you should use best_of parameter, while for temperatures = 0, you should play with beam_size and patience paremeters.

### Stage 5: Combined Optimizations
- Test and reveal the best combinations of FFmpeg and Whisper settings identified in previous steps.

**Note:**  
Do not proceed to a later stage until the previous stage is complete.

## Testing Strategy

- Use the scores to guide further testing, focusing on combinations that yield better results and avoiding those that perform poorly.
