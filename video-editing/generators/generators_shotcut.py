import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path
def generate_shotcut_timeline_project(self, output_path=None):
    """Generate a Shotcut .mlt file with a real timeline (chains, playlists, tractor)"""
    if output_path is None:
        output_path = self.output_dir / f"{self.project_name}_shotcut_timeline.mlt"

    mlt = ET.Element('mlt')
    mlt.set('LC_NUMERIC', 'C')
    mlt.set('version', '7.0.1')
    mlt.set('title', self.project_name)
    mlt.set('producer', 'main_bin')

    # Profile (use 720p 30fps as default)
    profile = ET.SubElement(mlt, 'profile')
    profile.set('description', 'HD 720p 30 fps')
    profile.set('width', '1280')
    profile.set('height', '720')
    profile.set('progressive', '1')
    profile.set('sample_aspect_num', '1')
    profile.set('sample_aspect_den', '1')
    profile.set('display_aspect_num', '16')
    profile.set('display_aspect_den', '9')
    profile.set('frame_rate_num', '30')
    profile.set('frame_rate_den', '1')
    profile.set('colorspace', '709')

    # Create a chain for each clip
    chains = []
    for i, clip in enumerate(self.clips):
        chain = ET.SubElement(mlt, 'chain')
        chain.set('id', f'chain{i}')
        fps = 30
        out_time = f"00:00:{int((clip.duration or 10.0)):02d}.000"
        chain.set('out', out_time)

        prop_length = ET.SubElement(chain, 'property')
        prop_length.set('name', 'length')
        prop_length.text = out_time

        prop_eof = ET.SubElement(chain, 'property')
        prop_eof.set('name', 'eof')
        prop_eof.text = 'pause'

        prop_resource = ET.SubElement(chain, 'property')
        prop_resource.set('name', 'resource')
        prop_resource.text = clip.filepath

        prop_service = ET.SubElement(chain, 'property')
        prop_service.set('name', 'mlt_service')
        prop_service.text = 'avformat-novalidate'

        if clip.transcription:
            prop_caption = ET.SubElement(chain, 'property')
            prop_caption.set('name', 'shotcut:caption')
            prop_caption.text = clip.transcription[:100]

        chains.append((chain, out_time, i))

    # Create a playlist for the timeline (V1)
    playlist = ET.SubElement(mlt, 'playlist')
    playlist.set('id', 'playlist0')
    prop_video = ET.SubElement(playlist, 'property')
    prop_video.set('name', 'shotcut:video')
    prop_video.text = '1'
    prop_name = ET.SubElement(playlist, 'property')
    prop_name.set('name', 'shotcut:name')
    prop_name.text = 'V1'

    # Helper to parse start_time (accepts float seconds or HH:MM:SS.mmm string)
    def parse_time(t):
        if isinstance(t, (int, float)):
            return float(t)
        if isinstance(t, str):
            parts = t.split(":")
            if len(parts) == 3:
                h, m, s = parts
                s, *ms = s.split(",")
                ms = int(ms[0]) if ms else 0
                return int(h)*3600 + int(m)*60 + int(s) + ms/1000
            elif len(parts) == 2:
                m, s = parts
                s, *ms = s.split(",")
                ms = int(ms[0]) if ms else 0
                return int(m)*60 + int(s) + ms/1000
            else:
                return float(t)
        return 0.0
    def fmt_time(seconds):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        ms = int(round((seconds - int(seconds)) * 1000))
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

    # Sort clips by start_time
    clips_sorted = sorted(self.clips, key=lambda c: parse_time(getattr(c, 'start_time', 0.0)))
    current_time = 0.0
    for i, clip in enumerate(clips_sorted):
        st = parse_time(getattr(clip, 'start_time', 0.0))
        if st > current_time:
            gap = st - current_time
            blank = ET.SubElement(playlist, 'blank')
            blank.set('length', fmt_time(gap))
            current_time = st
        entry = ET.SubElement(playlist, 'entry')
        entry.set('producer', f'chain{i}')
        entry.set('in', fmt_time(0.0))
        entry.set('out', fmt_time(clip.duration or 10.0))
        current_time += clip.duration or 10.0

    # Add a black background track (optional, for completeness)
    black = ET.SubElement(mlt, 'producer')
    black.set('id', 'black')
    black.set('in', '00:00:00.000')
    total_duration = sum((clip.duration or 10.0) for clip in self.clips)
    total_out = f"00:00:{int(total_duration):02d}.000"
    black.set('out', total_out)
    prop_length = ET.SubElement(black, 'property')
    prop_length.set('name', 'length')
    prop_length.text = total_out
    prop_eof = ET.SubElement(black, 'property')
    prop_eof.set('name', 'eof')
    prop_eof.text = 'pause'
    prop_resource = ET.SubElement(black, 'property')
    prop_resource.set('name', 'resource')
    prop_resource.text = '0'
    prop_aspect = ET.SubElement(black, 'property')
    prop_aspect.set('name', 'aspect_ratio')
    prop_aspect.text = '1'
    prop_service = ET.SubElement(black, 'property')
    prop_service.set('name', 'mlt_service')
    prop_service.text = 'color'
    prop_imgfmt = ET.SubElement(black, 'property')
    prop_imgfmt.set('name', 'mlt_image_format')
    prop_imgfmt.text = 'rgba'
    prop_audio = ET.SubElement(black, 'property')
    prop_audio.set('name', 'set.test_audio')
    prop_audio.text = '0'

    # Background playlist
    background = ET.SubElement(mlt, 'playlist')
    background.set('id', 'background')
    entry_bg = ET.SubElement(background, 'entry')
    entry_bg.set('producer', 'black')
    entry_bg.set('in', '00:00:00.000')
    entry_bg.set('out', total_out)

    # Tractor (timeline)
    tractor = ET.SubElement(mlt, 'tractor')
    tractor.set('id', 'tractor0')
    tractor.set('title', self.project_name)
    tractor.set('in', '00:00:00.000')
    tractor.set('out', total_out)
    prop_shotcut = ET.SubElement(tractor, 'property')
    prop_shotcut.set('name', 'shotcut')
    prop_shotcut.text = '1'
    prop_audioch = ET.SubElement(tractor, 'property')
    prop_audioch.set('name', 'shotcut:projectAudioChannels')
    prop_audioch.text = '2'
    prop_folder = ET.SubElement(tractor, 'property')
    prop_folder.set('name', 'shotcut:projectFolder')
    prop_folder.text = '0'
    track_bg = ET.SubElement(tractor, 'track')
    track_bg.set('producer', 'background')
    track_v1 = ET.SubElement(tractor, 'track')
    track_v1.set('producer', 'playlist0')

    rough_string = ET.tostring(mlt, 'unicode')
    reparsed = xml.dom.minidom.parseString(rough_string)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))
    return str(output_path)
