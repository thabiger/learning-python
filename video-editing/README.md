# Video Project Generator

A Python tool to programmatically create video editor project files for Linux video editors like OpenShot, Shotcut, and Kdenlive.

## Features

- **Multiple Editor Support**: Generate project files for OpenShot (.osp), Shotcut (.mlt), and Kdenlive (.kdenlive)
- **Automatic Transcription Loading**: Automatically loads transcriptions from .txt files with matching names
- **Batch Processing**: Load all video files from a directory
- **Flexible API**: Add clips manually or load from directories
- **Timeline Arrangement**: Automatically arranges clips in sequence on the timeline

## Installation

1. Clone or download this repository
2. Make sure you have Python 3.6+ installed
3. No additional dependencies required - uses only Python standard library

## Quick Start

### Command Line Usage

```bash
# Generate only for specific method
python3 ./video_project_generator.py --project-name TestProject  --method shotcut_timeline  --config /home/thabiger/Zonos/output_audio/alignment_data.json  /path/to/mediafiles
```

## Project File Details

### OpenShot (.osp)
- JSON format
- Includes full timeline with clips arranged sequentially
- Preserves transcriptions as clip metadata
- Compatible with OpenShot 2.6+

### Shotcut (.mlt)
- MLT XML format
- Creates timeline with video track
- Includes transcriptions in clip comments
- Compatible with Shotcut (all recent versions)

### Kdenlive (.kdenlive)
- MLT XML format (Kdenlive variant)
- Creates main timeline with clips
- Includes transcriptions in clip names
- Compatible with Kdenlive (recent versions)

## Command Line Options

```
usage: video_project_generator.py [-h] [--input_dir INPUT_DIR] [--editor {openshot,shotcut,kdenlive,all}]
                                  [--project-name PROJECT_NAME] [--output-dir OUTPUT_DIR]
                                  [--extensions EXTENSIONS [EXTENSIONS ...]] [--config CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  --input_dir INPUT_DIR
                        Directory containing video files
  --editor {openshot,shotcut,kdenlive,all}
                        Target video editor (default: all)
  --project-name PROJECT_NAME
                        Name of the project (default: Generated Project)
  --output-dir OUTPUT_DIR
                        Output directory for project files (default: .)
  --extensions EXTENSIONS [EXTENSIONS ...]
                        Video file extensions to include
  --config CONFIG
                        Project config file (JSON)
```

## Examples

### Python Script Example
```python
#!/usr/bin/env python3
"""
Demo script to create sample video project files
This creates demo projects without requiring actual video files
"""

from video_project_generator import VideoProjectGenerator

def create_demo_projects():
    """Create demo project files with sample data"""
    
    print("Video Project Generator Demo")
    print("=" * 40)
    
    # Create generator
    generator = VideoProjectGenerator()
    generator.project_name = "Demo Video Project"
    
    # Add some sample clips (these paths don't need to exist for demo)
    sample_clips = [
        {
            "filepath": "sample_videos1/15.mp4",
            "start_time": "00:00:02.000",
        },
        {
            "filepath": "sample_videos1/120.mp4", 
            "start_time": "00:10:00.000",
        },
        {
            "filepath": "sample_videos1/90.mp4",
            "start_time": "00:20:00.000",
        },
        {
            "filepath": "sample_videos1/45.mp4",
            "start_time": "00:30:00.000",
        }
    ]
    generator.load_clips(sample_clips)

    # Generate project files for different editors
    generator.generate(method='shotcut_playlist')


if __name__ == "__main__":
    create_demo_projects()

```