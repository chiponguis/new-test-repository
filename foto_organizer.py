import os
import shutil
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata

SOURCE_DIR = 'Fotos'
DEST_DIR = 'Fotos by date'

# Supported extensions for images, RAWs, and videos
SUPPORTED_EXTS = {
    '.jpg', '.jpeg', '.png', '.heic',  # Photos
    '.cr2', '.nef', '.arw', '.rw2',    # RAW formats
    '.mp4', '.mov', '.avi', '.mkv'     # Videos
}

def get_image_date(image_path):
    """Try to get date from image EXIF data using Pillow."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag == 'DateTimeOriginal':
                        return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception:
        pass
    return None

def get_file_metadata_date(file_path):
    """Fallback using hachoir to get creation date from video/RAW files."""
    try:
        parser = createParser(file_path)
        if parser:
            with parser:
                metadata = extractMetadata(parser)
                if metadata:
                    date = metadata.get('creation_date')
                    if date:
                        return date
    except Exception:
        pass
    return None

def get_capture_date(path):
    """Try EXIF, then hachoir, then file mod time."""
    ext = os.path.splitext(path)[1].lower()

    # Try EXIF for images
    if ext in {'.jpg', '.jpeg', '.png', '.heic'}:
        date = get_image_date(path)
        if date:
            return date

    # Try metadata (videos, RAWs)
    date = get_file_metadata_date(path)
    if date:
        return date

    # Fallback to file modification time
    return datetime.fromtimestamp(os.path.getmtime(path))

def ensure_unique_filename(directory, filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(os.path.join(directory, new_filename)):
        new_filename = f"{base}_{counter:02d}{ext}"
        counter += 1
    return new_filename

def organize_photos():
    for root, _, files in os.walk(SOURCE_DIR):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in SUPPORTED_EXTS:
                source_path = os.path.join(root, file)
                date = get_capture_date(source_path)
                year = date.strftime('%Y')
                dest_folder = os.path.join(DEST_DIR, year)
                os.makedirs(dest_folder, exist_ok=True)

                unique_filename = ensure_unique_filename(dest_folder, file)
                dest_path = os.path.join(dest_folder, unique_filename)

                shutil.copy2(source_path, dest_path)
                print(f"Copied: {source_path} -> {dest_path}")

if __name__ == '__main__':
    organize_photos()
