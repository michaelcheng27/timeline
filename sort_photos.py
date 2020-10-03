from pathlib import Path
from datetime import datetime

from media import Photo, Video


DESTINATION = "/mnt/d/sorted_photos"
VIDEO_DESTINATION = "/mnt/d/sorted_videos"
SOURCE = '/mnt/d/sorted_videos_old'
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


def is_video(f):
    return f.name[-3:] in ['mp4', 'MP4', 'MOV', 'mov', 'm4v']


def get_dest_dir(taken_datetime, f):
    year, month = taken_datetime.year, taken_datetime.month
    quarter = int((month - 1) / 3) + 1
    destination_dir = VIDEO_DESTINATION if is_video(f) else DESTINATION
    return f"{destination_dir}/{year}-Q{quarter}"


def file_exist(new_file_path, f):
    return Path(new_file_path).exists()


def move_file(taken_datetime, f, media):
    # make sure dest_dir exist
    if media and media.is_existing:
        print(f"media {media.uuid} already exists, skip moving")
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
        file_name = media.uuid
    new_file_path = f"{dest_dir}/{file_name}.{file_type}"
    Path(dest_dir).mkdir(parents=True, exist_ok=True)

    if file_exist(new_file_path, f):
        new_file_path_media = create_media_node(new_file_path)
        is_same = new_file_path_media.media_type == media.media_type and new_file_path_media.uuid == media.uuid

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


def create_media_node(f):
    if is_video(f):
        return Video(f)
    return Photo(f)


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
    media = create_media_node(f)
    taken_time = media.created_time
    if TEST_MODE:
        print("test mode, skip move file")
        continue
    move_file(taken_time, f, media)

# remove empty directory
remove_empty_folder(p)
print(f"=================Complete=================")
