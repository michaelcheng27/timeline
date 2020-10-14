
from dynamodb import DynamoDB
from datetime import datetime
from PIL import Image
import hashlib
from botocore.exceptions import ClientError
from PIL.TiffImagePlugin import TiffImageFile, DATE_TIME
from pathlib import Path
from abc import ABCMeta, abstractmethod
import ffmpeg

EXIF_TIME_TAG = 0x9003  # DateTimeOriginal
EXIF_SUB_SEC_TIME_TAG = 0x9291  # SubsecTimeOriginal

UUID_DATETIME_FORMAT = "%Y%m%d%H%M%S"

PHOTO_TABLE = DynamoDB('casa-ccc-photos')


class Media(object, metaclass=ABCMeta):
    def __init__(self, file_path, skip_dedupe=False):
        self._file_path = file_path
        self._is_existing = False
        self._uuid = None
        self._created_time = None

    def check_dedupe(self):
        try:
            PHOTO_TABLE.put_item({
                "id": self.uuid,
                "created_time": f"{self.created_time.timestamp()}",
                "media_type": f"{self.media_type}"
            })
        except ClientError as err:
            print(
                f"Failed to insert photo to table, uuid = {self.uuid}, exception = {err}")
            self._is_existing = True

    @property
    def uuid(self):
        return self._uuid

    @property
    def created_time(self):
        return self._created_time

    @property
    def create_time_to_string(self):
        return self.created_time.strftime(UUID_DATETIME_FORMAT)

    @property
    @abstractmethod
    def media_type(self):
        pass

    @property
    def is_existing(self):
        return self._is_existing


class Video(Media):
    def __init__(self, file_path, skip_dedupe=False):
        super().__init__(file_path, skip_dedupe)
        self.process_video(file_path)
        if not skip_dedupe:
            self.check_dedupe()

    def process_video(self, f):
        stream = ffmpeg.probe(f)
        formats = stream.get('format', {})
        tags = formats.get('tags', {})
        file_name = formats.get('filename', 'unknown_file_name')
        file_name = file_name.split('/')[-1]
        file_name = file_name.split('.')[0]
        creation_time = tags.get(
            'creation_time', "2000-01-01T00:00:00.000000")
        if creation_time[-1] == 'Z':
            creation_time = creation_time[: -1]
        self._created_time = datetime.strptime(
            f"{creation_time}", "%Y-%m-%dT%H:%M:%S.%f")
        self._uuid = f"{self.create_time_to_string}-{file_name}"

    @property
    def media_type(self):
        return "video"


class Photo(Media):
    def __init__(self, file_path, skip_dedupe=False):
        super().__init__(file_path, skip_dedupe)
        self._image_hash = None
        self._created_time = None
        self._is_existing = False
        self.process_image(file_path)
        # safe guard if hash is not computed
        self._image_hash = self._image_hash or "notHashed"
        self._uuid = f"{self.create_time_to_string}-{self._image_hash[:10]}"
        if not skip_dedupe:
            self.check_dedupe()

    def process_image(self, f):
        try:
            with Image.open(f) as im:
                raw_ts, sub_sec = self._get_date_time_original(im)
                self._created_time = self._get_date_time_from_time_taken(
                    raw_ts, sub_sec)
                self._image_hash = self._get_image_hash(im)
        except Exception as e:
            lstats = Path(f).lstat()
            if lstats and lstats.st_mtime:
                print(f"Fallback to lsstat for {f}")
                self._created_time = datetime.fromtimestamp(
                    round(float(lstats.st_mtime)))
            print(f"met error when processing {f}, error = {e}")

    @property
    def media_type(self):
        return "image"

    def _get_image_hash(self, image):
        md5hash = hashlib.md5(image.tobytes())
        return md5hash.hexdigest()

    def _get_date_time_original(self, image):
        if isinstance(image, TiffImageFile):
            date_time = image.tag_v2.get(DATE_TIME)
            return date_time, 0
        exif = image.getexif()
        raw_ts = exif.get(EXIF_TIME_TAG)
        sub_sec = int(exif.get(EXIF_SUB_SEC_TIME_TAG, 1))
        return raw_ts, sub_sec

    def _get_date_time_from_time_taken(self, taken_time, sub_sec):
        try:
            if sub_sec < 1000:
                # pad right
                sub_sec *= 1000
            return datetime.strptime(f"{taken_time}.{sub_sec:06}", "%Y:%m:%d %H:%M:%S.%f")
        except:
            return datetime.strptime(f"{taken_time}.{sub_sec:06}", "%Y-%m-%d %H:%M:%S.%f")
