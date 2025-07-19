
import os
from pathlib import Path
from typing import List
from dataclasses import dataclass
import generators
from .common import srt_time_to_seconds, get_video_duration

@dataclass
class VideoClip:
    """Represents a video clip with metadata"""
    filepath: str
    transcription: str = ""
    duration: float = 0.0
    start_time: float = 0.0
    title: str = ""
    
    def __post_init__(self):
        if not self.title:
            self.title = Path(self.filepath).stem


class VideoProjectGenerator:

    """Main class for generating video editor project files"""
    def __init__(self):
        self.clips: List[VideoClip] = []
        self.project_name = "Generated Project"
        self.output_dir = Path.cwd()

    def generate(self, method: str):
        """Generate project files for the specified editors. Returns list of (Editor, OutputFile)"""
        method_map = {
            'openshot': ('OpenShot', self.generate_openshot_project),
            'shotcut_playlist': ('Shotcut Playlist', self.generate_shotcut_project),
            'shotcut_timeline': ('Shotcut Timeline', self.generate_shotcut_timeline_project),
            'kdenlive': ('Kdenlive', self.generate_kdenlive_project),
        }
        if method in method_map:
            _, method_func = method_map[method]
            return method_func()
        else:
            print(f"Unknown method: {method}")

    def add_clip(self, filepath: str, transcription: str = "", duration: float = 0.0, title: str = "", start_time: float = 0.0):
        clip = VideoClip(
            filepath=os.path.abspath(filepath),
            transcription=transcription,
            duration=duration,
            title=title or Path(filepath).stem,
            start_time=start_time
        )
        self.clips.append(clip)

    def load_clips_from_directory(self, directory: str, extensions: List[str] = None):
        if extensions is None:
            extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v']
        directory = Path(directory)
        for ext in extensions:
            for video_file in directory.glob(f"*{ext}"):
                transcription_file = video_file.with_suffix('.txt')
                transcription = ""
                if transcription_file.exists():
                    transcription = transcription_file.read_text(encoding='utf-8')
                self.add_clip(str(video_file), transcription)

    def load_clips(self, input_dir: str = None, data: list = None):

        if not data:
            print("No clips data provided!")
            return

        # Compute start_time for a continuous timeline
        start_pos = 0.0
        for clip_data in data:
            start_pos = start_pos + srt_time_to_seconds(clip_data["start_time"])
            filepath = os.path.join(input_dir, clip_data.get("filepath"))
            duration = clip_data.get("duration", get_video_duration(filepath)) + 1 # additional second, cause of rounding issues

            self.add_clip(
                filepath=filepath,
                transcription=clip_data.get("transcription", ""),
                duration=duration,
                title=clip_data.get("title", ""),
                start_time=clip_data.get("start_time", 0.0)
            )

            start_pos += duration
        
        print(f"Added {len(self.clips)} demo clips:")
        total_duration = 0.0
        for clip in self.clips:
            print(f"  - {clip.title} ({clip.duration}s)")
            print(f"    Transcription: {clip.transcription[:60]}...")
            total_duration += clip.duration
        
        print(f"\nTotal project duration: {total_duration} seconds ({total_duration/60:.1f} minutes)")
    
generators._register_generators(VideoProjectGenerator)