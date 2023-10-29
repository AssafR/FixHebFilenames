import glob
import sys
from subprocess import check_output
from pathlib import Path
import cv2
import pytesseract

tesseract_exe = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def main():
    print('|'.join(sys.argv))
    jpeg_location = sys.argv[1]
    print(jpeg_location)
    txt_location = sys.argv[2]
    txt_path = Path(txt_location)
    # args is a list of the command line args
    jpgfiles = glob.glob(jpeg_location + '/*.jpeg')
    print(len(jpgfiles))
    print(jpgfiles)

    pytesseract.pytesseract.tesseract_cmd = tesseract_exe

    for jpgfile in jpgfiles:
        filename = Path(jpgfile).stem
        txt_filename = txt_path.joinpath(filename)
        # perform_ocr_commandline(jpgfile, txt_filename)
        perform_ocr_api(jpgfile, txt_filename)


def perform_ocr_commandline(jpgfile, txt_filename):
    cmd = f'"{tesseract_exe}" -l heb "{jpgfile}" "{txt_filename}"'
    print(f'Running\n{cmd}\n\n')
    output = check_output(cmd, shell=True).decode()
    print(output)
    print('----------')


def perform_ocr_api(jpgfile, txt_filename):
    img = cv2.imread(jpgfile)

    # Adding custom options
    custom_config = r'--oem 3 --psm 6 -l heb'
    txt = pytesseract.image_to_string(img, config=custom_config)
    print(txt)
    print('----------')
    # d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    # n_boxes = len(d['level'])
    # for i in range(n_boxes):
    #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    string_boxes = pytesseract.image_to_boxes(img, lang="heb").splitlines() #, output_type=pytesseract.Output.DICT
    for row in string_boxes:
        print(row)
        b = row.split(' ')
        char, x, y, w, h, page = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])
        cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (50, 50, 255), 1)





    return None

    cv2.imshow('img', img)
    cv2.waitKey(0)


if __name__ == '__main__':
    main()