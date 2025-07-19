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


def get_video_duration(filepath):

    import subprocess
    
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries",
                "format=duration", "-of",
                "default=noprint_wrappers=1:nokey=1", filepath
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        return float(result.stdout)
    except Exception:
        return 0.0