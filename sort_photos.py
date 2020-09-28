from PIL import Image
from PIL.ExifTags import TAGS
from PIL.TiffImagePlugin import TiffImageFile, DATE_TIME
from pathlib import Path
from datetime import datetime
import ffmpeg

EXIF_TIME_TAG = 0x9003  # DateTimeOriginal
EXIF_SUB_SEC_TIME_TAG = 0x9291  # SubsecTimeOriginal

DESTINATION = "/mnt/d/sorted_photo"
SOURCE = '/mnt/d/imac_photo'
# DESTINATION = "/mnt/d/ws/sorted_photo"
# SOURCE = '/mnt/d/ws/timeline/test'


def get_image_uuid(exif):
    return None


def get_taken_time(f):
    try:
        if f.name[-3:] == 'mp4':
            stream = ffmpeg.probe(f)
            tags = stream.get('format', {}).get('tags', {})
            creation_time = tags.get(
                'creation_time', "2000-01-01T00:00:00.000000")
            if creation_time[-1] == 'Z':
                creation_time = creation_time[: -1]
            return datetime.strptime(f"{creation_time}", "%Y-%m-%dT%H:%M:%S.%f")
        with Image.open(f) as im:
            if isinstance(im, TiffImageFile):
                date_time = im.tag_v2.get(DATE_TIME)
                return get_date_time_from_time_taken(date_time, 0)
            exif = im.getexif()
            raw_ts = exif.get(EXIF_TIME_TAG)
            sub_sec = int(exif.get(EXIF_SUB_SEC_TIME_TAG, 1))
            return get_date_time_from_time_taken(raw_ts, sub_sec)
    except Exception as e:
        print(f"met error when processing image, error = {e}")
        return None


def get_date_time_from_time_taken(taken_time, sub_sec):
    try:
        if sub_sec < 1000:
            # pad right
            sub_sec *= 1000
        return datetime.strptime(f"{taken_time}.{sub_sec:06}", "%Y:%m:%d %H:%M:%S.%f")
    except:
        return datetime.strptime(f"{taken_time}.{sub_sec:06}", "%Y-%m-%d %H:%M:%S.%f")


def get_dest_dir(taken_datetime):
    year, month = taken_datetime.year, taken_datetime.month
    quarter = int((month - 1) / 3) + 1
    return f"{DESTINATION}/{year}-Q{quarter}"


def file_exist(new_file_path, f):
    return Path(new_file_path).exists()


def move_file(taken_datetime, f):
    # make sure dest_dir exist
    dest_dir = get_dest_dir(taken_datetime)
    new_file_path = f"{dest_dir}/{f.name}"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    if file_exist(new_file_path, f):
        print(
            f"[ERORR]: File exists, skip moving. new_file_path = {new_file_path}")
        return
    f.rename(new_file_path)


print("Hello world")
p = Path(SOURCE)
for f in p.glob("**/*.*"):
    print(f"Moving {f.name}")
    taken_datetime = get_taken_time(f)
    if taken_datetime is None:
        continue
    move_file(taken_datetime, f)
