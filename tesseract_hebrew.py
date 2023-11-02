import glob
import sys
from subprocess import check_output
from pathlib import Path
import cv2
import pytesseract
from pytesseract import Output, run_and_get_output
from pathlib import Path
import tesseract_sql

# INSERT OR IGNORE INTO aspect_corrections(aspect) VALUES(4.0);



tesseract_exe = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

##########
# Source: https://stackoverflow.com/questions/54246492/pytesseract-difference-between-image-to-string-and-image-to-boxes
# Modification

COLOR_GREEN = (0, 255, 0)


def image_to_boxes_keep_same(
        image,
        lang=None,
        config='',
        nice=0,
        output_type=pytesseract.Output.STRING,
        timeout=0,
):
    """
    Returns string containing recognized characters and their box boundaries
    """
    config = f'{config.strip()} makebox'
    args = [image, 'box', lang, config, nice, timeout]

    return {
        Output.BYTES: lambda: run_and_get_output(*(args + [True])),
        Output.STRING: lambda: run_and_get_output(*args),
    }[output_type]()


def new_image_to_boxes(image, lang, output_type, config=None):  # .splitlines() #, output_type=pytesseract.Output.DICT
    return image_to_boxes_keep_same(image, lang, output_type)


##########

def main():
    print('|'.join(sys.argv))
    jpeg_location = sys.argv[1]
    txt_location = sys.argv[2]
    letters_location = sys.argv[3]



    print(jpeg_location)
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
        perform_ocr_api(jpgfile, txt_filename, letters_location)


def perform_ocr_commandline(jpgfile, txt_filename):
    cmd = f'"{tesseract_exe}" -l heb "{jpgfile}" "{txt_filename}"'
    print(f'Running\n{cmd}\n\n')
    output = check_output(cmd, shell=True).decode()
    print(output)
    print('----------')


def hconcat_resize_max(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = max(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)

def new_char_filename(original_filename,letters_location,description_row):
    path = Path(original_filename)
    b = description_row.split()
    hex_str = b[0].encode("utf-8").hex()
    b[0] = hex_str + 'h_'
    new_filename = '_'.join(b)
    new_filename_full = path.with_stem(new_filename + '__' + path.stem).with_suffix('.png')
    new_filename_full = Path(letters_location).joinpath(new_filename_full.name)
    return new_filename_full.as_posix()

def perform_ocr_api(jpgfile, txt_filename, letters_location):
    full_img = cv2.imread(jpgfile)

    char_boxes = {}

    hImg, wImg, _ = full_img.shape
    aspect_ratio_correction = 2.0
    full_img = cv2.resize(full_img, (int(aspect_ratio_correction * wImg), int(hImg)))
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
        b = row.split(' ')
        detected_char, left, top, right, bottom, page = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])
        # detected_char, left, top, right, bottom = \
        #     string_boxes['char'][index],string_boxes['left'][index],string_boxes['top'][index],string_boxes['right'][index],string_boxes['bottom'][index]
        # detected_word, left, top, width, height = \
        #     string_boxes['text'][index], string_boxes['left'][index], string_boxes['top'][index], string_boxes['width'][
        #         index], string_boxes['height'][index]
        # (x1,y1), (x2,y2)
        # cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (255, 0, 0), 2)

        print(f"\n** {detected_char} **")
        print(b[1:]) # Row of numbers

        tmp_img = full_img.copy()
        calc_img_bottom = hImg - bottom
        calc_img_top = hImg - top

        char_box, char_box_enlarged = extract_box(full_img, left, right, calc_img_top, calc_img_bottom, 1.2)
        # cv2.rectangle(tmp_img, (left, calc_img_top), (right, calc_img_bottom), COLOR_GREEN, 3)

        Path(detected_box_file_name).parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(detected_box_file_name, char_box)
        char_boxes[detected_char] = char_boxes.get(detected_char, []) + [char_box_enlarged]

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


def extract_box(img, left, right, top, bottom, enlarge_factor=1.0):
    width = (right - left)
    height = (top - bottom)
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    new_width = width * enlarge_factor
    new_height = height * enlarge_factor

    # Hope it's okay, didn't test edge cases yet
    new_left = max(int(center_x - new_width / 2), 0)
    new_right = min(int(center_x + new_width / 2), img.shape[1])
    new_top = min(int(center_y + new_height / 2), img.shape[0])
    new_bottom = max(int(center_y - new_height / 2), 0)

    char_box_original = img[bottom:top, left:right].copy()
    char_box_enlarged = img[new_bottom:new_top, new_left:new_right].copy()
    return char_box_original, char_box_enlarged


if __name__ == '__main__':
    main()
