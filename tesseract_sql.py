from dataclasses import dataclass, field
import sqlite3


# Define a function to create a database connection
def create_connection(database):
    return sqlite3.connect(database)


@dataclass
class AspectCorrection:
    aspect_correction_id: int
    aspect: float

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)


@dataclass
class Image:
    image_id: int
    image: bytes

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

    @classmethod
    def from_sql_query(cls, query_result):
        return cls(*query_result)


# Define a class to manage the database
class DatabaseManager:
    def __init(self, database):
        self.conn = create_connection(database)

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
        cursor.execute("INSERT INTO images (image) VALUES (?)", (image.image,))
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
        cursor.execute("INSERT INTO subs_files (file_name, directory_name) VALUES (?, ?)",
                       (subs_files.file_name, subs_files.directory_name))
        self.conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        subs_files.sub_file_id = inserted_id
        return subs_files
