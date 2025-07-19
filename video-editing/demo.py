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
