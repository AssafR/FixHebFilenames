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

    hImg, wImg, _ = img.shape
    ratio = 1024.0 / wImg;

    img = cv2.resize(img, (int(ratio * wImg), int(ratio * hImg)))

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
    # string_boxes = pytesseract.image_to_boxes(img, lang="heb",output_type=pytesseract.Output.DICT)#.splitlines() #, output_type=pytesseract.Output.DICT
    string_boxes = pytesseract.image_to_data(img, lang="heb",
                                             output_type=pytesseract.Output.DICT)  # .splitlines() #, output_type=pytesseract.Output.DICT

    for index in range(len(string_boxes['left'])):
        # print(row)
        # b = row.split(' ')
        # char, x, y, w, h, page = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])
        # detected_char, left, top, right, bottom = \
        #     string_boxes['char'][index],string_boxes['left'][index],string_boxes['top'][index],string_boxes['right'][index],string_boxes['bottom'][index]
        detected_word, left, top, width, height = \
            string_boxes['text'][index], string_boxes['left'][index], string_boxes['top'][index], string_boxes['width'][
                index], string_boxes['height'][index]
        # (x1,y1), (x2,y2)
        # cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (255, 0, 0), 2)
        if detected_word:
            word_rect_img = img[top-2:top + height+4, left-2:left + width+4]
            char_boxes = pytesseract.image_to_boxes(word_rect_img, lang="heb",
                                                    output_type=pytesseract.Output.DICT)  # .splitlines() #, output_type=pytesseract.Output.DICT
            # cv2.imshow('img', word_rect_img)
            # cv2.waitKey(0)
            for index_char in range(len(char_boxes['left'])):
                detected_char, left, top, right, bottom = \
                    string_boxes['char'][index], string_boxes['left'][index], string_boxes['top'][index], \
                    string_boxes['right'][index], string_boxes['bottom'][index]
                # cv2.putText(img, str(detected_word), (left, top + 13), cv2.QT_FONT_BLACK, 0.4, (50, 205, 50), 1)
                cv2.rectangle(img, (left, top), (right, bottom), (50, 0, 50), 2)

    img_resized = cv2.resize(img, (int(ratio * wImg), int(ratio * hImg)))

    cv2.imshow('img', img_resized)
    cv2.waitKey(0)

    return None


if __name__ == '__main__':
    main()
