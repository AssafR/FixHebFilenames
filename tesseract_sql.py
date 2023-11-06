import datetime
import pathlib
from dataclasses import dataclass, field
import sqlite3
import numpy as np
import io

from tesseract_hebrew_utils import get_file_attributes

# Define a function to create a database connection
def create_connection(database):
    return sqlite3.connect(database,
                           detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES  # For parsing datetypes
                           )

@dataclass
class AspectCorrection:
    aspect_correction_id: int
    aspect: float

    def __init__(self, aspect, aspect_correction_id=None):
        self.aspect = aspect
        self.aspect_correction_id = aspect_correction_id

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)


@dataclass
class Image:
    image_id: int
    image_text: str
    image: bytes

    def __init__(self, text, img):
        self.image_id = None
        self.image_text = text
        self.image = img

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)


@dataclass
class SubsDecoded:
    subs_decoded_id: int
    sub_file_fk: int
    image_id_fk: int
    detected_char: str
    left: int
    right: int
    top: int
    bottom: int
    page: int

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)


@dataclass
class SubsFiles:
    sub_file_id: int
    file_name: str
    directory_name: str
    file_date: datetime.datetime

    def __init__(self, full_file_name):
        self.sub_file_id = None
        self.file_name, self.directory_name, self.file_date = get_file_attributes(full_file_name)

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)

    def full_file_name(self):  # Manual addition
        return pathlib.Path(self.directory_name).joinpath(self.file_name).as_posix()


# Define a class to manage the database
class DatabaseManager:
    def __init__(self, database):
        self.conn = create_connection(database)
        # Converts np.array to TEXT when inserting
        sqlite3.register_adapter(np.ndarray, adapt_array)

        # Converts TEXT to np.array when selecting
        # sqlite3.register_converter("array", convert_array)
        sqlite3.register_converter("array", lambda x: np.load(io.BytesIO(x)))

    def read_aspect_corrections(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM aspect_corrections")
        results = cursor.fetchall()
        cursor.close()
        return [AspectCorrection.from_sql_query(row) for row in results]

    def read_images(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM images")
        results = cursor.fetchall()
        cursor.close()
        return [Image.from_sql_query(row) for row in results]

    def read_subs_decoded(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subs_decoded")
        results = cursor.fetchall()
        cursor.close()
        return [SubsDecoded.from_sql_query(row) for row in results]

    def read_subs_files(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM subs_files")
        results = cursor.fetchall()
        cursor.close()
        return [SubsFiles.from_sql_query(row) for row in results]

    def insert_aspect_correction(self, aspect_correction):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO aspect_corrections (aspect) VALUES (?)", (aspect_correction.aspect,))
        self.conn.commit()
        cursor.execute("SELECT aspect_correction_id FROM aspect_corrections WHERE aspect = ?",
                       (aspect_correction.aspect,))
        result = cursor.fetchone()
        cursor.close()
        if result:
            aspect_correction.aspect_correction_id = result[0]
            return aspect_correction
        return None

    def insert_image(self, image):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO images (image_text,image) VALUES (?, ?)", (image.image, image.image_text))
        self.conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        image.image_id = inserted_id
        return image

    def insert_subs_decoded(self, subs_decoded):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO subs_decoded (sub_file_fk, image_id_fk, detected_char, [left], [right], top, bottom, page) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (subs_decoded.sub_file_fk, subs_decoded.image_id_fk, subs_decoded.detected_char, subs_decoded.left,
             subs_decoded.right, subs_decoded.top, subs_decoded.bottom, subs_decoded.page))
        self.conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        subs_decoded.subs_decoded_id = inserted_id
        return subs_decoded

    def insert_subs_files(self, subs_files):
        cursor = self.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO subs_files (file_name, directory_name, file_date) VALUES (?, ?, ?)",
                       (subs_files.file_name, subs_files.directory_name, subs_files.file_date))
        self.conn.commit()
        cursor.execute(
            "SELECT sub_file_id FROM subs_files WHERE file_name = ? AND directory_name = ? AND file_date = ?",
            (subs_files.file_name, subs_files.directory_name, subs_files.file_date))
        result = cursor.fetchone()
        cursor.close()
        if result:
            subs_files.sub_file_id = result[0]
            return subs_files
        return None


def adapt_array(arr):
    """
    http://stackoverflow.com/a/31312102/190597 (SoulNibbler)
    """
    out = io.BytesIO()
    np.save(out, arr)
    out.seek(0)
    return sqlite3.Binary(out.getvalue())


def convert_array(text):
    out = io.BytesIO(text)
    out.seek(0)
    return np.load(out)
