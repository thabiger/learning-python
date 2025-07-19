#!/usr/bin/env python3
"""
Video Project Generator
A Python script to programmatically create video editor project files
Supports: OpenShot, Shotcut, and other Linux video editors
"""

import argparse
import json
from pathlib import Path
from generators.generator import VideoProjectGenerator


def main():
    parser = argparse.ArgumentParser(description='Generate video editor project files')
    parser.add_argument('input_dir', help='Directory containing video files')
    parser.add_argument('--method', choices=['openshot', 'shotcut_timeline', 'shotcut_playlist', 'kdenlive'], 
                       default='all', help='Target video editor')
    parser.add_argument('--project-name', default='Generated Project', 
                       help='Name of the project')
    parser.add_argument('--output-dir', default='.', 
                       help='Output directory for project files')
    parser.add_argument('--extensions', nargs='+', 
                       default=['.mp4', '.avi', '.mov', '.mkv', '.webm', '.m4v'],
                       help='Video file extensions to include')
    parser.add_argument('--config', required=False, default=None, help='Project config file')

    args = parser.parse_args()
    
    generator = VideoProjectGenerator()
    generator.project_name = args.project_name
    generator.output_dir = Path(args.output_dir)
    
    # Load clips
    if args.config:
        print("Loading project configuration...")
        # Load configuration logic here if needed
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
                generator.load_clips(input_dir=args.input_dir, data=config)
        except FileNotFoundError:
            print("No project configuration file found.")
            exit(1)
    else:
        print(f"Loading video clips from: {args.input_dir}")
        generator.load_clips_from_directory(args.input_dir, args.extensions)
    
    if not generator.clips:
        print("No video files found in the specified directory!")
        return
    
    print(f"Found {len(generator.clips)} video clips:")
    for clip in generator.clips:
        print(f"  - {clip.title} ({clip.filepath})")
        if clip.transcription:
            print(f"    Transcription: {clip.transcription[:100]}...")
    
    generator.generate(method=args.method)



if __name__ == '__main__':
    main()
