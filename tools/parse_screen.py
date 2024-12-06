import mss
import cv2
import numpy
import easyocr

# EasyOCR Config
print(f"Loading EasyOcr model into Memory")
reader = easyocr.Reader(['en'])


def parsescreen():
    fire_solution = ScreenOCR()
    while True:
        # call for bearing/radian
        fire_solution.get_natomil()
        cv2.waitKey(100)
    cv2.destroyAllWindows()
    pass


class ScreenOCR:
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    natomil_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                  "left": 530, "width": 60, "height": 110}

    def __init__(self):
        # Variables for radians
        print(f"Initializing Screen OCR")
        self.natomil_monochrome = None
        self.natomil_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_natomil = 5
        self.buffer_natomil = 0

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
            # cv2.imshow("Bearing Screen Capture", self.img_monochrome)

            return reader.readtext(self.img_monochrome, allowlist=".0123456789", detail=0)

    def get_natomil_ocr_results(self):  # this will return easyocr results for mil
        with mss.mss() as sct:
            screenshot = sct.grab(self.natomil_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            (thresh, self.natomil_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

            # cv2.imshow("Radian Gray Screen Capture", img_gray)
            cv2.imshow("Radian Monochrome Screen Capture", self.natomil_monochrome)

            return reader.readtext(self.natomil_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                   low_text=0.2, link_threshold=0.2)

    def approximate_natomil(self):
        natomil_results = self.get_natomil_ocr_results()
        if natomil_results:
            try:
                for index, number in enumerate(natomil_results):
                    top_left_y_axis = number[0][0][1]
                    bot_left_y_axis = number[0][3][1]
                    screen_lookup_bottom_edge = self.natomil_screen_coordinates["height"]

                    # check if the box is on edge or not
                    if top_left_y_axis != 0 and bot_left_y_axis != screen_lookup_bottom_edge:
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
            except IndexError as error:
                print(f"Index Error Encountered: {error}")
                print(f"Make sure squad game is in focus")
            except Exception as error:
                print(f"Error Encountered: {error}")


if __name__ == "__main__":
    parsescreen()
