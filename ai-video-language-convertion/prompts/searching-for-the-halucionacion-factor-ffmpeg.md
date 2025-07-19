
## Objective

Systematically determine the optimal FFmpeg audio preprocessing parameters to identify which audio file properties cause Whisper unpredictability. This is to be achieved by running multiple transcription attempts using the transcribe MCP tool, assigning scores to each attempt, and analyzing the results.

## General Rules

- **Input file:** `Wideo/VID20250619100726_cfr_rotated.mp4`
- You may perform up to **200 transcription executions** to find the best solution.

## Constraints

- Follow all instructions in this document precisely. No deviations from the specified rules or workflow are permitted under any circumstances.
- The following MCP arguments must never be changed:
    - `language="pl"`
    - `model="large-v2"`
    - `skip_if_exists=True`
    - `second_pass=False`
    - `external_vad=None`
    - `whisper_params`:
        ```json
        {
            "temperature": [0.1, 0.3, 0.5, 0.7],
            "compression_ratio_threshold": 2.1,
            "logprob_threshold": -0.85,
            "no_speech_threshold": 0.45
        }
        ```
- If the MCP server does not return an explicit error, assume the operation was successful, regardless of the output.

## Scoring

Each transcription attempt should be scored from **0 to 100** based on:

1. The overall number of errors in the transcription.
2. Whether the lines follow the broad context of the text and make sense.
3. The absence of hallucinations and repetitions.

## Logging and Output

Each parameter set test case must follow these rules for logging and storing results:

- Store all results in a separate folder named `Wideo/test-{date}-{time}`.
- For each test case:
    - Assign a unique attempt number and name.
    - Save the resulting SRT files along with a corresponding `.info` file containing:
        - The parameters used.
        - The average score and predictability of the method.
        - The full JSON object with parameters passed to the transcribe tool.
- Log all parameter sets and their results in a common log file, updating it after finishing testing each case.

## Workflow

### Stage 1: Media Analysis

- Gather information about the input media file to avoid unnecessary preprocessing that could degrade its original properties (e.g., sampling rate).

### Stage 2: Baseline Test

- Perform five consecutive baseline transcription attempts using only the minimal required parameters to establish a reference point.
- Record the score for each attempt and calculate the average score and predictability.
- Save all baseline results and logs according to the procedures described in the Logging and Output section.

### Stage 3: Audio Quality Optimization Test

1. Construct parameter sets by experimenting with various FFmpeg preprocessing options, such as filtering, bandpass, resampling, and converting to mono. Prioritize custom FFmpeg settings designed to enhance speech audio quality; do not use any preprocessors other than FFmpeg.
2. For each parameter set, perform five consecutive transcription attempts, assign a score to each, and calculate the consistency as a percentage predictability metric.
3. Log the summarized (average) results for each parameter set as specified in the Logging and Output section.

### Stage 4: Combined Optimizations

- Test and reveal the best combinations of FFmpeg settings identified in previous steps.

**Note:**  
Do not proceed to a later stage until the previous stage is complete.

## Testing Strategy

- Use the scores to guide further testing, focusing on combinations that yield better results and avoiding those that perform poorly.

