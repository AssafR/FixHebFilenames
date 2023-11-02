--
-- File generated with SQLiteStudio v3.4.4 on ???�? ??? 2 18:03:25 2023
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: aspect_corrections
DROP TABLE IF EXISTS aspect_corrections;

CREATE TABLE IF NOT EXISTS aspect_corrections (
    aspect_correction_id      PRIMARY KEY,
    aspect               REAL NOT NULL
);


-- Table: images
DROP TABLE IF EXISTS images;

CREATE TABLE IF NOT EXISTS images (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image    BLOB
);


-- Table: subs_decoded
DROP TABLE IF EXISTS subs_decoded;

CREATE TABLE IF NOT EXISTS subs_decoded (
    subs_decoded_id INTEGER PRIMARY KEY,
    sub_file_fk             REFERENCES subs_files (sub_file_id) 
                            NOT NULL,
    image_id_fk     INTEGER REFERENCES images (image_id) 
                            NOT NULL,
    detected_char   TEXT,
    [left]          INTEGER NOT NULL,
    [right]         INTEGER NOT NULL,
    top             INTEGER NOT NULL,
    bottom          INTEGER NOT NULL,
    page            INTEGER NOT NULL
);


-- Table: subs_files
DROP TABLE IF EXISTS subs_files;

CREATE TABLE IF NOT EXISTS subs_files (
    sub_file_id    INTEGER PRIMARY KEY,
    file_name      TEXT    CONSTRAINT sub_files_NotNull NOT NULL,
    directory_name TEXT
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
