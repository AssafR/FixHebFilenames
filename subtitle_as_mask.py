import glob
import re
import sys
from subprocess import check_output
from pathlib import Path
import cv2 as cv
import sys

time_pattern = '(\d)_(\d{2})_(\d{2})_(\d{3})'
extra_pattern = '(\d{5})'
pixel_pattern = '(\d{5})'
regexp_pattern = f'{time_pattern}__{time_pattern}_{extra_pattern}{pixel_pattern}{pixel_pattern}{pixel_pattern}{pixel_pattern}'
regexp = re.compile(regexp_pattern)


def display_file(imgfile):
    img = cv.imread(imgfile)
    if img is None:
        sys.exit("Could not read the image.")

    win_name = 'main_window'
    X = 0
    Y = 0
    width = 1280
    height = 1024

    # Create a Named Window
    cv.namedWindow(win_name, cv.WINDOW_NORMAL)

    # Move it to (X,Y)
    cv.moveWindow(win_name, X, Y)

    # Show the Image in the Window
    cv.imshow(win_name, img)

    # Resize the Window
    cv.resizeWindow(win_name, width, height)

    # cv.imshow("Display window", img)
    k = cv.waitKey(0)


def parse_filename(filename):
    # Example filename: 0_00_05_920__0_00_07_719_0087800000019200108001920
    m = regexp.match(filename)
    subtitle_params = [int(m.group(i)) for i in range(1, m.lastindex + 1)]
    return subtitle_params


def main():
    jpeg_location = sys.argv[1]
    print(jpeg_location)
    txt_location = sys.argv[2]
    txt_path = Path(txt_location)
    # args is a list of the command line args
    jpgfiles = glob.glob(jpeg_location + '/*.jpeg')
    print(len(jpgfiles))

    for jpgfile in jpgfiles:
        print(jpgfile)
        filename = Path(jpgfile).stem
        subtitle_params = parse_filename(filename)
        display_file(jpgfile)
        break


if __name__ == '__main__':
    main()
