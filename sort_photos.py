from pathlib import Path
from datetime import datetime
import ffmpeg

from media import Photo

EXIF_TIME_TAG = 0x9003  # DateTimeOriginal
EXIF_SUB_SEC_TIME_TAG = 0x9291  # SubsecTimeOriginal

DESTINATION = "/mnt/d/sorted_photos"
VIDEO_DESTINATION = "/mnt/d/sorted_videos"
SOURCE = '/mnt/d/sorted_photos_old'
# SOURCE = '/mnt/d/failed'
# DESTINATION = "/mnt/d/ws/sorted_photo"
# SOURCE = '/mnt/d/ws/timeline/test'
FAILED_DIR = "/mnt/d/failed"
NOT_SUPPORTED_DIR = "/mnt/d/not_supported"
DUPLICATED_DIR = "/mnt/d/duplicated"

PLACE_HOLDER_FILE_NAME = "place_holder.md"
ENABLE_TS_FALLBACK_TO_LS_STAT = False

TEST_MODE = False


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
    return f.name[-3:] in ['mp4', 'MP4', 'MOV', 'mov', 'm4v']


def is_video_same(a, b):
    return get_date_time_original_from_ffmpeg(a) == get_date_time_original_from_ffmpeg(b)


def get_taken_time(f):
    try:
        if is_video(f):
            return get_date_time_original_from_ffmpeg(f)
    except Exception as e:
        if ENABLE_TS_FALLBACK_TO_LS_STAT:
            lstats = Path(f).lstat()
            if lstats and lstats.st_mtime:
                print(f"Fallback to lsstat for {f}")
                return datetime.fromtimestamp(round(float(lstats.st_mtime)))
        print(f"met error when processing {f}, error = {e}")
        return None


def get_dest_dir(taken_datetime, f):
    year, month = taken_datetime.year, taken_datetime.month
    quarter = int((month - 1) / 3) + 1
    destination_dir = VIDEO_DESTINATION if is_video(f) else DESTINATION
    return f"{destination_dir}/{year}-Q{quarter}"


def file_exist(new_file_path, f):
    return Path(new_file_path).exists()


def move_file(taken_datetime, f, media):
    # make sure dest_dir exist
    if media and media.is_existed:
        print(f"media {media.image_uuid} already exists, skip moving")
        return
    dest_dir = FAILED_DIR
    format_not_supported = is_format_not_supported(f)
    if format_not_supported:
        dest_dir = NOT_SUPPORTED_DIR
    if taken_datetime:
        dest_dir = get_dest_dir(taken_datetime, f)
    file_type = f.name.split('.')[-1]
    file_name = f.name.split('.')[0]
    if media:
        file_name = media.image_uuid
    new_file_path = f"{dest_dir}/{file_name}.{file_type}"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    if file_exist(new_file_path, f):
        is_same = is_video_same(new_file_path, f) if is_video(f) else Photo(
            new_file_path).image_uuid == media.image_uuid

        if format_not_supported or not is_same:
            print(
                f"Image is not same or not supported {f} and {new_file_path}, rename and then move")
            new_file_path = f"{dest_dir}/1-{file_name}"
        else:
            Path(DUPLICATED_DIR).mkdir(parents=True, exist_ok=True)
            duplicated_path = f"{DUPLICATED_DIR}/{file_name}"
            print(
                f"[ERORR]: File exists, moving to duplicate folder. duplicated_path = {duplicated_path}, new_file_path = {new_file_path}")
            new_file_path = duplicated_path
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
total_file_count = len(list(p.glob("**/*.*")))
print(f"Start Processing {total_file_count} files")
progress = 0
processed = 0
for f in p.glob("**/*.*"):
    processed += 1
    new_progress = int(processed * 100.0 / total_file_count)
    if new_progress > progress:
        progress = new_progress
        print(f"====== PROGRESS {progress}% =======")
    if f.name == PLACE_HOLDER_FILE_NAME:
        continue
    media = None
    if is_video(f):
        taken_time = get_taken_time(f)
    else:
        media = Photo(f)
        taken_time = media.created_time
    if TEST_MODE:
        print("test mode, skip move file")
        continue
    move_file(taken_time, f, media)

# remove empty directory
remove_empty_folder(p)
print(f"=================Complete=================")
