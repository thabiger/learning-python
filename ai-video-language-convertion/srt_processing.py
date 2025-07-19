import os
import ollama
import textwrap
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class SRTSegment:
    idx: int
    start: float
    end: float
    text: str

def srt_time_to_seconds(srt_time: str) -> float:
    """
    Convert an SRT timestamp string to seconds.

    Args:
        srt_time (str): Timestamp in SRT format, e.g. "01:02:03,456".

    Returns:
        float: The total number of seconds represented by the timestamp.

    Example:
        srt_time_to_seconds("00:01:23,456")  # returns 83.456
    """
    h, m, s_ms = srt_time.split(':')
    s, ms = s_ms.split(',')
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000

def seconds_to_srt_time(seconds: float) -> str:
    """
    Convert a number of seconds to an SRT timestamp string.

    Args:
        seconds (float): The time in seconds.

    Returns:
        str: Timestamp in SRT format, e.g. "01:02:03,456".

    Example:
        seconds_to_srt_time(83.456)  # returns "00:01:23,456"
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def parse_srt(srt_path: str) -> List[SRTSegment]:
    import re
    segments = []
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = re.compile(r"(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.+?)(?=\n\d+\n|\Z)", re.DOTALL)
    for match in pattern.finditer(content):
        idx = int(match.group(1))
        start = srt_time_to_seconds(match.group(2))
        end = srt_time_to_seconds(match.group(3))
        text = match.group(4).replace('\n', ' ').strip()
        segments.append(SRTSegment(idx, start, end, text))
    return segments

def merge_srt_segments(segments, max_gap=0.5):
    merged = []
    buffer = []
    for i, seg in enumerate(segments):
        if not buffer:
            buffer.append(seg)
            continue
        prev = buffer[-1]
        # If gap is small and previous text doesn't end with .!?...
        if seg.start - prev.end <= max_gap and not prev.text.strip().endswith(('.', '!', '?', '…')):
            # Merge
            buffer[-1] = SRTSegment(
                idx=prev.idx,
                start=prev.start,
                end=seg.end,
                text=prev.text.rstrip() + ' ' + seg.text.lstrip()
            )
        else:
            merged.append(buffer[-1])
            buffer = [seg]
    if buffer:
        merged.append(buffer[-1])
    return merged

def get_broad_context(text: str) -> str:
    # Summarize the movie in 2-3 sentences using the LLM
    prompt = textwrap.dedent(f"""
        Summarize in 2-3 sentences what this movie is about based on the subtitles provided.
        Subtitles:
        {text}

        Summary:
    """)
    context =  ollama.call_api(prompt)
    ollama.stop_all_processes()  # Stop all Ollama processes to free memory
    return context.strip()

def get_context_segments(segments: List[SRTSegment], idx: int, window: float = 7.0) -> Tuple[List[SRTSegment], SRTSegment, List[SRTSegment]]:
    target = segments[idx]
    before, after = [], []
    # Collect segments within window before
    t = target.start
    for seg in reversed(segments[:idx]):
        if t - seg.end <= window:
            before.insert(0, seg)
        else:
            break
    # Collect segments within window after
    t = target.end
    for seg in segments[idx+1:]:
        if seg.start - t <= window:
            after.append(seg)
        else:
            break
    return before, target, after

def extend_w_llm(input_srt: str, output_srt: str | None = None, window: float = 7.0, language: str = "polish") -> str:

    # If output_srt is None, use input file name with 'llm_extended_' prefix
    if output_srt is None:
        base = os.path.basename(input_srt)
        dir_ = os.path.dirname(input_srt)
        output_srt = os.path.join(dir_, f"{base}_llm_extended")

    segments = merge_srt_segments(parse_srt(input_srt))
    broad_context = get_broad_context(segments)
    fixed_segments = []

    system_prompt = textwrap.dedent(f"""
        You are a subtitle corrector. Your only task is to minimally correct grammar, spelling, or clarity issues in the provided subtitle line, or align it to fit the surrounding context if necessary.
        Do not rewrite, embellish, or add creative language. Do not change the meaning or style. Do not add or remove information.
        If the line is already clear and grammatically correct, return it unchanged.
        All sentences must be grammatically correct and natural in the {language} language.
        Do not include any reasoning or analysis in your response. Only provide the corrected line without any additions.
    """)
    summary_prompt = f"Video summary is: {broad_context}"

    for idx, seg in enumerate(segments):
        before, target, after = get_context_segments(segments, idx, window)
        before_text = ' '.join([s.text for s in before])
        after_text = ' '.join([s.text for s in after])

        prompt = textwrap.dedent(f"""
            {system_prompt}
            {summary_prompt}

            Context before: {before_text}
            Line to correct: {target.text}
            Context after: {after_text}
        """)

        change_proposal = ollama.call_api(prompt)

        if change_proposal.strip() != target.text.strip():
            print(f"[CHANGED] #{target.idx} {seconds_to_srt_time(target.start)} --> {seconds_to_srt_time(target.end)}")
            print(f"  Original: {target.text}")
            print(f"  Changed:  {change_proposal}\n")
        else:
            print(f"  Unchanged: {target.text}")
        fixed_segments.append((target.idx, target.start, target.end, change_proposal))

    # Write fixed SRT
    with open(output_srt, 'w', encoding='utf-8') as f:
        for idx, start, end, text in fixed_segments:
            f.write(f"{idx}\n{seconds_to_srt_time(start)} --> {seconds_to_srt_time(end)}\n{text}\n\n")

    return output_srt