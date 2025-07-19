
## Objective

Systematically determine the optimal Whisper configuration to improve transcription quality and reduce unpredictability across multiple attempts. This will be achieved by running several transcription attempts using the transcribe MCP tool, assigning scores to each attempt, and analyzing the results.

## General Rules

- **Input file:** `Wideo/VID20250619100726_cfr_rotated.mp4`
- You may perform up to **200 transcription executions** to find the best solution.

## Constraints

- Follow all instructions in this document precisely. No deviations from the specified rules or workflow are permitted under any circumstances.
- The following MCP arguments must never be changed:
    - `model="large-v2"`
    - `skip_if_exists=True`
    - `second_pass=False`
    - `external_vad=None`
    - `preprocess_pipeline=None`
    - `whisper_implementation="whisperx"`
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

### Stage 3: Whisper Consistency and Predictability Test
1. For each parameter set (defined as a specific configuration of the `whisper_params` structure), perform five consecutive transcription attempts, as done during the baseline estimation.
2. Systematically experiment with various Whisper options in each parameter set, such as `temperatures`, `compression_ratio_threshold`, `no_speech_threshold`, `condition_on_previous_text` and any other that you can find in the documentation. Continue testing until all relevant options have been evaluated, and identify the most effective parameters.
3. Assign a score to each transcription attempt. Use these scores to calculate the average score and a consistency metric (predictability percentage) for a tested parameter set, as done during the baseline estimation.
4. Log the summarized (average) results for each parameter set as specified in the Logging and Output section.

### Stage 4: Combined Optimizations

- Test and reveal the best combinations of Whisper settings identified in previous steps.

**Note:**  
Do not proceed to a later stage until the previous stage is complete.

## Testing Strategy

- Use the scores to guide further testing, focusing on combinations that yield better results and avoiding those that perform poorly.

