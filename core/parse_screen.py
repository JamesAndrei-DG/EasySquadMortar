import mss
import cv2
import numpy as np
import easyocr


class ParseScreen:
    SCREEN_RESOLUTION = (1920, 1080)
    AZIMUTH_SCREEN_COORDS = {"top": 1050, "left": 940, "width": 41, "height": 16}
    NATOMIL_SCREEN_COORDS = {"top": int(SCREEN_RESOLUTION[1] / 2 - 100 / 2),
                             "left": 530, "width": 60, "height": 110}

    reader = easyocr.Reader(['en'])

    def __init__(self):
        self.natomil_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_natomil = 5
        self.buffer_natomil = 0
        self.buffer_azimuth = 0
        print(f"Initializing Screen OCR with EasyOCR model")

    def get_azimuth(self) -> float:
        azimuth = self.get_azimuth_ocr_results()
        if azimuth:
            self.buffer_azimuth = azimuth
            return azimuth
        return self.buffer_azimuth

    def get_natomil(self) -> int:
        value = self.approximate_natomil()
        if value:

            if 800 <= int(value) <= 1580:
                self.buffer_natomil = value
                return value
            else:
                return 0
        return self.buffer_natomil

    def get_azimuth_ocr_results(self) -> float:
        with mss.mss() as sct:
            screenshot = sct.grab(self.AZIMUTH_SCREEN_COORDS)
            img_gray = cv2.cvtColor(np.asarray(screenshot, dtype=np.uint8), cv2.COLOR_BGRA2GRAY)
            thresh, azimuth_monochrome = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)

            # For Visualization
            # cv2.imshow("Azimuth Screen Capture", img_monochrome)

            return self.reader.readtext(azimuth_monochrome, allowlist=".0123456789", detail=0)

    def get_natomil_ocr_results(self) -> list:  # this will return easyocr results for mil
        with mss.mss() as sct:
            screenshot = sct.grab(self.NATOMIL_SCREEN_COORDS)
            img_gray = cv2.cvtColor(np.asarray(screenshot, dtype=np.uint8), cv2.COLOR_BGRA2GRAY)
            thresh, natomil_monochrome = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

            # For Visualization
            # cv2.imshow("Radian Monochrome Screen Capture", natomil_monochrome)

            return self.reader.readtext(natomil_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                        low_text=0.2, link_threshold=0.2)

    def approximate_natomil(self) -> int:
        try:
            natomil_results = self.get_natomil_ocr_results()
            for index, number in enumerate(natomil_results):
                top_left_y_axis = number[0][0][1]
                bot_left_y_axis = number[0][3][1]
                screen_lookup_bottom_edge = self.NATOMIL_SCREEN_COORDS["height"]

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
            return 0
        except ValueError as error:
            print(f"Value Error Encountered: {error}")
            return 0
        except Exception as error:
            print(f"Error Encountered: {error}")
            raise Exception(f"Error Encountered: {error}")
