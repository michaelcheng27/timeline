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
FAILED_DIR = "/mnt/d/failed"
NOT_SUPPORTED_DIR = "/mnt/d/not_supported"

PLACE_HOLDER_FILE_NAME = "place_holder.md"
ENABLE_TS_FALLBACK_TO_LS_STAT = False


def is_format_not_supported(f):
    return f.name[-3:].lower() in ['png', 'aae']


def get_date_time_original_from_ffmpeg(f):
    stream = ffmpeg.probe(f)
    tags = stream.get('format', {}).get('tags', {})
    creation_time = tags.get(
        'creation_time', "2000-01-01T00:00:00.000000")
    if creation_time[-1] == 'Z':
        creation_time = creation_time[: -1]
    return datetime.strptime(f"{creation_time}", "%Y-%m-%dT%H:%M:%S.%f")


def is_video(f):
    return f.name[-3:] in ['mp4', 'MP4', 'MOV', 'mov']


def is_video_same(a, b):
    return get_date_time_original_from_ffmpeg(a) == get_date_time_original_from_ffmpeg(b)


def is_image_same(a, b):
    try:
        with Image.open(a) as image_a, Image.open(b) as image_b:
            return get_date_time_original(image_a) == get_date_time_original(image_b)
    except Exception as e:
        print(
            f"[ERROR] is_image_same met error when processing image, error = {e}")
        return False


def get_date_time_original(image):
    if isinstance(image, TiffImageFile):
        date_time = image.tag_v2.get(DATE_TIME)
        return date_time, 0
    exif = image.getexif()
    raw_ts = exif.get(EXIF_TIME_TAG)
    sub_sec = int(exif.get(EXIF_SUB_SEC_TIME_TAG, 1))
    return raw_ts, sub_sec


def get_taken_time(f):
    try:
        if is_video(f):
            return get_date_time_original_from_ffmpeg(f)
        with Image.open(f) as im:
            raw_ts, sub_sec = get_date_time_original(im)
            return get_date_time_from_time_taken(raw_ts, sub_sec)
    except Exception as e:
        if ENABLE_TS_FALLBACK_TO_LS_STAT:
            lstats = Path(f).lstat()
            if lstats and lstats.st_mtime:
                print(f"Fallback to lsstat for {f}")
                return datetime.fromtimestamp(round(float(lstats.st_mtime)))
        print(f"met error when processing {f}, error = {e}")
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


def is_media_same(a, b):
    if is_video(a):
        return is_video_same(a, b)
    return is_image_same(a, b)


def move_file(taken_datetime, f):
    # make sure dest_dir exist
    dest_dir = FAILED_DIR
    format_not_supported = is_format_not_supported(f)
    if format_not_supported:
        dest_dir = NOT_SUPPORTED_DIR
    if taken_datetime:
        dest_dir = get_dest_dir(taken_datetime)
    new_file_path = f"{dest_dir}/{f.name}"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    if file_exist(new_file_path, f):
        if format_not_supported or not is_media_same(f, new_file_path):
            print(
                f"Image is not same or not supported {f} and {new_file_path}, rename and then move")
            new_file_path = f"{dest_dir}/1-{f.name}"
        else:
            print(
                f"[ERORR]: File exists, skip moving. new_file_path = {new_file_path}")
            return
    print(f"Moving {f} to {new_file_path}")
    f.rename(new_file_path)


def remove_empty_folder(parent):
    childs = list(parent.iterdir())
    if len(childs) == 0:
        print(f"Removing {parent} since it's empty")
        parent.rmdir()
    for child in childs:
        if child.is_dir():
            remove_empty_folder(child)


print("Hello world")
p = Path(SOURCE)
for f in p.glob("**/*.*"):
    if f.name == PLACE_HOLDER_FILE_NAME:
        continue
    taken_datetime = get_taken_time(f)
    move_file(taken_datetime, f)

# remove empty directory
remove_empty_folder(p)
print(f"=================Complete=================")
