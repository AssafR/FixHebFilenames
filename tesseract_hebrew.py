import glob
import sys
from subprocess import check_output
from pathlib import Path
import cv2
import pytesseract
from pytesseract import Output, run_and_get_output

tesseract_exe = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


##########
# Source: https://stackoverflow.com/questions/54246492/pytesseract-difference-between-image-to-string-and-image-to-boxes
# Modification


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


def hconcat_resize_max(im_list, interpolation=cv2.INTER_CUBIC):
    h_min = max(im.shape[0] for im in im_list)
    im_list_resize = [cv2.resize(im, (int(im.shape[1] * h_min / im.shape[0]), h_min), interpolation=interpolation)
                      for im in im_list]
    return cv2.hconcat(im_list_resize)


def perform_ocr_api(jpgfile, txt_filename):
    img = cv2.imread(jpgfile)

    char_boxes = {}

    hImg, wImg, _ = img.shape
    ratio = 1024.0 / wImg;

    # img = cv2.resize(img, (int(ratio * wImg), int(ratio * hImg)))

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
    string_boxes = pytesseract.image_to_boxes(img, lang="heb",
                                              output_type=pytesseract.Output.STRING).splitlines()  # , output_type=pytesseract.Output.DICT
    # string_boxes = pytesseract.image_to_data(img, lang="heb",
    #                                          output_type=pytesseract.Output.DICT)  # .splitlines() #, output_type=pytesseract.Output.DICT

    for row in string_boxes:
        b = row.split(' ')
        detected_char, left, top, right, bottom, page = b[0], int(b[1]), int(b[2]), int(b[3]), int(b[4]), int(b[5])
        # detected_char, left, top, right, bottom = \
        #     string_boxes['char'][index],string_boxes['left'][index],string_boxes['top'][index],string_boxes['right'][index],string_boxes['bottom'][index]
        # detected_word, left, top, width, height = \
        #     string_boxes['text'][index], string_boxes['left'][index], string_boxes['top'][index], string_boxes['width'][
        #         index], string_boxes['height'][index]
        # (x1,y1), (x2,y2)
        # cv2.rectangle(img, (x, hImg - y), (w, hImg - h), (255, 0, 0), 2)

        print("\n** ", detected_char, " **")
        print(b[1:])

        tmp_img = img.copy()
        char_box = img[(hImg - bottom):(hImg - top), left:right].copy()
        cv2.rectangle(tmp_img, (left, hImg - top), (right, hImg - bottom), (0, 255, 0), 3)

        char_boxes[detected_char] = char_boxes.get(detected_char, []) + [char_box]

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
        for img in images:
            cv2.rectangle(img, (0, 0), (img.shape[1], img.shape[0]), (0, 255, 0), 3)
        all_images = hconcat_resize_max(images)  # cv2.hconcat(images)
        cv2.imshow('img', all_images)
        cv2.waitKey(0)

    img_resized = cv2.resize(img, (int(ratio * wImg), int(ratio * hImg)))

    cv2.imshow('img', img_resized)
    cv2.waitKey(0)

    return None


if __name__ == '__main__':
    main()
