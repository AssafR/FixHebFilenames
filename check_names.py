import os
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import eyed3

def convert_encode(string):
    try:
        result = string.encode('iso-8859-1').decode('iso-8859-8').encode('utf-16').decode('utf-16')
    except:
        result = string.encode('utf-16').decode('utf-16')
    return result


def check_id3(mp3_filename):
    mp3_info = MP3(mp3_filename, ID3=EasyID3)
    for k, v in mp3_info.items():
        print('key: ',k)
        for v_number,v_element in enumerate(v):
            print(f'   {v_number}: {v_element}')
            print(f'   {v_number}: {convert_encode(v_element)}')
    # mp3_info = eyed3.load(mp3_filename)
    print(mp3_info)


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


if __name__ == '__main__':
    # check_name('T:\mp3_\÷åøéï àìàì')
    ''
    check_id3('T:\mp3_\(דני סנדרסון - הטובים לטיס (נבחרת שירים\\07 - מה הדאווין שלך.mp3')