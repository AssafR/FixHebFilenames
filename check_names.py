import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import pathlib
import re
import shutil

import eyed3


def convert_encode(string):
    try:
        result = string.encode('iso-8859-1').decode('iso-8859-8').encode('utf-16').decode('utf-16')
    except:
        result = string.encode('utf-16').decode('utf-16')
    return result


def convert_list(lst):
    return [convert_encode(lst_item) for lst_item in lst]


def convert_id3(id3_data):
    for k, v in id3_data.items():
        id3_data[k] = convert_list(v)
    return id3_data


def fix_id3_for_file(mp3_filename):
    print(f'Filename: {mp3_filename}')
    mp3_info = MP3(mp3_filename, ID3=EasyID3)
    print('Before: ', mp3_info)
    mp3_info = convert_id3(mp3_info)
    print('After:  ', mp3_info)
    mp3_info.save(mp3_filename)


def check_name(name):
    print(f'Name        = {name}')
    print(f"Name encoded= {convert_encode(name)}")
    print(name == (convert_encode(name)))

    # os.chdir(name)
    # inside = os.listdir()[0]
    # # print(inside[0])
    # arr = bytes(inside, 'iso-8859-8')
    # for byte in arr:
    #     print(byte, end=' ')
    # print()
    # # print('Encoded: ', inside.encode('ascii').decode('iso-8859-8'))
    # print('Encoded: ', arr.decode('utf-8'))


def decide_and_rename(name):
    new_name = convert_encode(name)
    if name != new_name:
        new_name_no_ext = pathlib.Path(new_name).stem
        new_name_no_ext = re.sub('[0-9.\-\(\)]', '', new_name_no_ext)
        new_name_no_hebrew = re.sub('[א-ת]', '', new_name_no_ext)
        if length_conditions(new_name_no_ext, new_name_no_hebrew) or mix_condition(new_name_no_ext):
            return name
        else:
            return new_name
    return name


def traverse_directory(path):
    fname = []
    dname = []
    print("Root path: ", path)
    for root, d_names, f_names in os.walk(path):
        for d in d_names:
            full_name = os.path.join(root, d)
            fname.append(full_name)
            print(" Directory: ", full_name)
        for f in f_names:
            full_name = os.path.join(root, f)
            fname.append(full_name)
            print("  File: ", full_name)

    print("Final file names:", fname)
    print("Final dir  names:", dname)


def length_conditions(old, new):
    return len(new) > 0 and \
           ((len(old) - len(new)) / len(old) < 0.3)


def mix_condition(name):
    return re.search('[a-zA-z][א-ת][a-zA-Z]', name) is not None

def move_all_contents(srcdir,trgdir):
    for root, d_names, f_names in os.walk(srcdir):
        for f in f_names:
            full_src_file_name = os.path.join(srcdir, f)
            full_trg_file_name = os.path.join(trgdir, f)
            print(f"Moving file {full_src_file_name} to {full_trg_file_name}")
        for d in d_names:
            full_src_dir_name = os.path.join(srcdir, d)
            full_trg_dir_name = os.path.join(trgdir, d)
            print(f"Moving dir  {full_src_dir_name} to {full_trg_dir_name}")


def rename_files_demo(path):
    print("Root path: ", path)
    for root, d_names, f_names in os.walk(path):
        # for d in f_names:
        #     new_file_name = decide_and_rename(d)
        #     if new_file_name == d:
        #         print(f"**** No need to rename file {new_file_name}")
        #     else:
        #         print(f'Renaming file \r\n   {d}\r\n to\r\n    {new_file_name}\r\n***')
        for d in d_names:
            new_dir_name = decide_and_rename(d)
            full_dir_name = os.path.join(root, d)
            new_full_dir_name = os.path.join(root, new_dir_name)
            if new_dir_name == d:
                pass
                # print(f"**** No need to rename dir  {new_dir_name}")
            else:
                try:
                    os.rename(full_dir_name, new_full_dir_name)
                    print(f'Renaming dir  \r\n   {full_dir_name}\r\n to\r\n    {new_full_dir_name}\r\n***')
                except:
                    # print(f'** Cannot rename dir  \r\n   {full_dir_name}\r\n to\r\n    {new_full_dir_name}\r\n***')
                    move_all_contents(full_dir_name, new_full_dir_name)


if __name__ == '__main__':
    # check_name('T:\mp3_\÷åøéï àìàì')
    ''
    # fix_id3_for_file(r'T:\mp3_\(דני סנדרסון - הטובים לטיס (נבחרת שירים\08 - שיר רועים.mp3')
    # traverse_directory('T:\mp3_\A Flock Of Seagulls')
    # rename_files_demo(r'T:\mp3_\Transspot\mp3 on shaharnewlap\Isra\Celia Cruz\Siempre Celia Disc 2') #  r'T:\mp3_'
    rename_files_demo(r'T:\mp3_')
