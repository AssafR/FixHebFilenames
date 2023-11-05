import glob
import sys
import cv2
import pytesseract
from pytesseract import Output, run_and_get_output
from pathlib import Path
import tesseract_sql
from tesseract_hebrew_utils import *

# INSERT OR IGNORE INTO aspect_corrections(aspect) VALUES(4.0);

sqlite_db = r'.\letters.sqlite'

COLOR_GREEN = (0, 255, 0)
ASPECT_RATIO_CORRECTION = 2.0


def new_image_to_boxes(image, lang, output_type, config=None):  # .splitlines() #, output_type=pytesseract.Output.DICT
    return image_to_boxes_keep_same(image, lang, output_type)


##########

def main_old():
    database = tesseract_sql.DatabaseManager(sqlite_db)
    # aspect = tesseract_sql.AspectCorrection(2.0)
    aspect = database.insert_aspect_correction(tesseract_sql.AspectCorrection(2.0))
    # aspect = database.insert_aspect_correction(tesseract_sql.AspectCorrection(4.0))
    # aspect = database.insert_aspect_correction(tesseract_sql.AspectCorrection(3.0))
    print(aspect)


def main():
    print('|'.join(sys.argv))
    jpeg_location = sys.argv[1]
    txt_location = sys.argv[2]
    letters_location = sys.argv[3]

    print(f'Jpeg Location: {jpeg_location}')
    txt_path = Path(txt_location)
    # args is a list of the command line args
    jpgfiles = glob.glob(jpeg_location + '/*.jpeg')
    print(len(jpgfiles))
    print(jpgfiles)

    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE

    for jpgfile in jpgfiles:
        filename = Path(jpgfile).stem
        txt_filename = txt_path.joinpath(filename)
        # perform_ocr_commandline(jpgfile, txt_filename)
        perform_ocr_api(jpgfile, txt_filename, letters_location)


def perform_ocr_api(jpgfile, txt_filename, letters_location, aspect_correction=1.0):
    full_img = cv2.imread(jpgfile)

    char_boxes = {}

    hImg, wImg, _ = full_img.shape
    full_img = cv2.resize(full_img, (int(aspect_correction * wImg), int(hImg)))
    hImg, wImg, _ = full_img.shape

    ratio = 1024.0 / wImg;

    # img = cv2.resize(img, (int(ratio * wImg), int(ratio * hImg)))

    # Adding custom options
    custom_config = r'--oem 3 --psm 6 -l heb'
    txt = pytesseract.image_to_string(full_img, config=custom_config)
    print(txt)
    print('----------')
    # d = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    # n_boxes = len(d['level'])
    # for i in range(n_boxes):
    #     (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
    #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
    string_boxes = pytesseract.image_to_boxes(full_img, lang="heb",
                                              output_type=pytesseract.Output.STRING).splitlines()  # , output_type=pytesseract.Output.DICT
    # string_boxes = pytesseract.image_to_data(img, lang="heb",
    #                                          output_type=pytesseract.Output.DICT)  # .splitlines() #, output_type=pytesseract.Output.DICT

    for row in string_boxes:
        detected_box_file_name = new_char_filename(jpgfile, letters_location, row)

        ocr_result = ocr_box_result(full_img, row)

        # detected_char, left, top, right, bottom = \
        #     string_boxes['char'][index],string_boxes['left'][index],string_boxes['top'][index],string_boxes['right'][index],string_boxes['bottom'][index]
        # detected_word, left, top, width, height = \
        #     string_boxes['text'][index], string_boxes['left'][index], string_boxes['top'][index], string_boxes['width'][
        #         index], string_boxes['height'][index]
        # (x1,y1), (x2,y2)
        # cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (255, 0, 0), 2)

        print(f"\n** {ocr_result.detected_char} **")
        # print(b[1:])  # Row of numbers

        tmp_img = full_img.copy()

        char_box, char_box_enlarged = ocr_result.extract_box_from_image(enlarge_factor = 1.2)
        # cv2.rectangle(tmp_img, (left, calc_img_top), (right, calc_img_bottom), COLOR_GREEN, 3)

        # Path(detected_box_file_name).parent.mkdir(parents=True, exist_ok=True)
        # cv2.imwrite(detected_box_file_name, char_box)
        # char_boxes[detected_char] = char_boxes.get(detected_char, []) + [char_box_enlarged]

        # img_resized = cv2.resize(tmp_img, (int(ratio * wImg), int(ratio * hImg)))

        # cv2.imshow('img', char_box)
        # cv2.waitKey(0)
        # print('-----')

        # if detected_word:
        #     word_rect_img = img[top - 2:top + height + 4, left - 2:left + width + 4]
        #     # char_boxes = pytesseract.image_to_boxes(word_rect_img, lang="heb",
        #     #                                         output_type=pytesseract.Output.DICT)  # .splitlines() #, output_type=pytesseract.Output.DICT
        #     char_boxes = new_image_to_boxes(word_rect_img, lang="heb",
        #                                     output_type=pytesseract.Output.STRING)  # .splitlines() #, output_type=pytesseract.Output.DICT
        #
        #     # cv2.imshow('img', word_rect_img)
        #     # cv2.waitKey(0)
        #     for index_char in range(len(char_boxes['left'])):
        #         detected_char, left, top, right, bottom = \
        #             string_boxes['char'][index], string_boxes['left'][index], string_boxes['top'][index], \
        #                 string_boxes['right'][index], string_boxes['bottom'][index]
        #         # cv2.putText(img, str(detected_word), (left, top + 13), cv2.QT_FONT_BLACK, 0.4, (50, 205, 50), 1)
        #         cv2.rectangle(img, (left, top), (right, bottom), (50, 0, 50), 2)

    for char, images in char_boxes.items():
        print(f'*** {char} ***')
        ocr_from_boxes = ''
        for img in images:
            re_ocr = pytesseract.image_to_string(img, lang='heb').strip()
            ocr_from_boxes += re_ocr
            cv2.rectangle(img, (0, 0), (img.shape[1], img.shape[0]), (0, 255, 0), 3)

        print(f"Re-interpreted: [{'|'.join(ocr_from_boxes)}]")
        # all_images = hconcat_resize_max(images)  # cv2.hconcat(images)
        # cv2.imshow('img', all_images)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    img_resized = cv2.resize(full_img, (int(ratio * wImg), int(ratio * hImg)))
    cv2.imshow('img', img_resized)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()

    return None


if __name__ == '__main__':
    main()
