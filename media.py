
from dynamodb import DynamoDB
from datetime import datetime
from PIL import Image
import hashlib
from botocore.exceptions import ClientError
from PIL.TiffImagePlugin import TiffImageFile, DATE_TIME
from pathlib import Path

EXIF_TIME_TAG = 0x9003  # DateTimeOriginal
EXIF_SUB_SEC_TIME_TAG = 0x9291  # SubsecTimeOriginal

UUID_DATETIME_FORMAT = "%Y%m%d%H%M%S"

IMAGE_TABLE = DynamoDB('casa-ccc-photos')


class Photo:
    def __init__(self, file_path, skip_dedupe=False):
        self._file_path = file_path
        self._image_hash = None
        self._created_time = None
        self._is_existed = False
        self.process_image(file_path)
        self._image_uuid = f"{self.created_time.strftime(UUID_DATETIME_FORMAT)}-{self._image_hash[:10]}"
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

    def check_dedupe(self):
        try:
            IMAGE_TABLE.put_item({
                "image_uuid": self._image_uuid,
                "created_time": f"{self._created_time.timestamp()}",
            })
        except ClientError as err:
            print(
                f"Failed to insert image to table, image_hash = {self._image_uuid}, exception = {err}")
            self._is_existed = True

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

    @property
    def created_time(self):
        return self._created_time

    @property
    def is_existed(self):
        return self._is_existed

    @property
    def image_uuid(self):
        return self._image_uuid
