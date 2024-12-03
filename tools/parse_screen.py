import mss
import cv2
import numpy
import easyocr
import time
from PIL import Image

# EasyOCR Config
reader = easyocr.Reader(['en'])


def parsescreen():
    fire_solution = FireSolution()
    while True:
        # call for bearing/radian
        cv2.waitKey(1)
    cv2.destroyAllWindows()
    pass


class FireSolution:
    # initialization
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    natomil_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                  "left": 530, "width": 60, "height": 110}

    # value[1] for the second number only if detected
    # value[origin_x][0] list of coordinates starting from index[0] = top left and proceeding clockwise
    # value[origin_x][1] Detected Number
    # value[origin_x][2] Probability

    def __init__(self):

        print("Initializing FireSolution Class")
        # this function will call the getheight which will have look into get_approximate_radian with a few second delay to get the average
        # self.average_height = self.get_height() #this must return a list
        print("Getting Bearing")
        while True:
            self.bearing = self.get_bearing()
            if self.bearing:
                print(f"Bearing is: {self.bearing}")
                break

        print("Getting Radian")
        # Variables for radians
        self.natomil_monochrome = None
        self.natomil_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_natomil = 5
        self.buffer_natomil = 0

        while True:

            test = self.get_natomil()
            print(f"Nato mil: {test}")

    def get_bearing(self):
        return self.get_bearing_ocr_results()

    def get_natomil(self):
        value = self.approximate_natomil()
        if value:

            if 800 <= int(value) <= 1580:
                self.buffer_natomil = value
                return value
            else:
                return 0
        return self.buffer_natomil

    def get_bearing_ocr_results(self):
        with mss.mss() as sct:
            screenshot = sct.grab(self.bearing_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            (thresh, self.img_monochrome) = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)
            cv2.imshow("Bearing Screen Capture", self.img_monochrome)

            return reader.readtext(self.img_monochrome, allowlist=".0123456789", detail=0)

    def get_natomil_ocr_results(self):  # this will return easyocr results for mil
        with mss.mss() as sct:
            screenshot = sct.grab(self.natomil_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            (thresh, self.natomil_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

            cv2.imshow("Radian Gray Screen Capture", img_gray)
            cv2.imshow("Radian Monochrome Screen Capture", self.natomil_monochrome)

            return reader.readtext(self.natomil_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                   low_text=0.2, link_threshold=0.2)

    def approximate_natomil(self):
        natomil_results = self.get_natomil_ocr_results()
        if natomil_results:
            for index, number in enumerate(natomil_results):
                boxnumber = 1
            # compute box height
            top_left_y_axis = number[0][0][1]
            bot_left_y_axis = number[0][3][1]
            screen_edge = self.natomil_screen_coordinates["height"]
            tolerance = 1  # number tolerance for pixel not used

            # check if the box is on edge or not
            if top_left_y_axis != 0 and bot_left_y_axis != screen_edge:
                self.box_height[index] = int(bot_left_y_axis - top_left_y_axis)

            # get box position
            if self.box_height[index] != 0:
                self.box_position[index] = bot_left_y_axis - (self.box_height[index] * 0.5)

            if index == 1:
                self.box_difference = self.box_position[1] - self.box_position[0]
                self.pixel_per_natomil = self.box_difference * 0.1

            if index == 0:
                if number[2] >= 0.8:  # if it goes to 800 it no longer goes over 0.8 confidence
                    natomil = int(number[1]) + int((self.box_position[0] - 50) / self.pixel_per_natomil)
                    # this should return the approximate mil calculated from the pixel difference and the mil detected

                    return natomil



if __name__ == "__main__":
    parsescreen()
