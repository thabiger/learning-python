
import xml.etree.ElementTree as ET
import xml.dom.minidom
from pathlib import Path
def generate_shotcut_project(self, output_path=None):
    """Generate Shotcut project file (.mlt) - basic playlist version"""
    if output_path is None:
        output_path = self.output_dir / f"{self.project_name}_shotcut.mlt"

    mlt = ET.Element('mlt')
    mlt.set('LC_NUMERIC', 'C')
    mlt.set('version', '7.0.1')
    mlt.set('title', self.project_name)
    mlt.set('producer', 'main_bin')

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

    main_bin = ET.SubElement(mlt, 'producer')
    main_bin.set('id', 'main_bin')
    main_bin.set('in', '0')
    main_bin.set('out', '-1')
    property_elem = ET.SubElement(main_bin, 'property')
    property_elem.set('name', 'xml')
    property_elem.text = 'was here'

    for i, clip in enumerate(self.clips):
        producer = ET.SubElement(mlt, 'producer')
        producer.set('id', f'producer{i}')
        producer.set('in', '0')
        producer.set('out', str(int((clip.duration or 10.0) * 30 - 1)))
        resource_prop = ET.SubElement(producer, 'property')
        resource_prop.set('name', 'resource')
        resource_prop.text = clip.filepath
        if clip.transcription:
            meta_prop = ET.SubElement(producer, 'property')
            meta_prop.set('name', 'meta.attr.comment.markup')
            meta_prop.text = clip.transcription

    playlist = ET.SubElement(mlt, 'playlist')
    playlist.set('id', 'playlist0')
    current_frame = 0
    for i, clip in enumerate(self.clips):
        entry = ET.SubElement(playlist, 'entry')
        entry.set('producer', f'producer{i}')
        entry.set('in', '0')
        duration_frames = int((clip.duration or 10.0) * 30)
        entry.set('out', str(duration_frames - 1))
        current_frame += duration_frames

    tractor = ET.SubElement(mlt, 'tractor')
    tractor.set('id', 'tractor0')
    tractor.set('in', '0')
    tractor.set('out', str(current_frame - 1))
    track = ET.SubElement(tractor, 'track')
    track.set('producer', 'playlist0')

    rough_string = ET.tostring(mlt, 'unicode')
    reparsed = xml.dom.minidom.parseString(rough_string)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(reparsed.toprettyxml(indent="  "))
    return str(output_path)
