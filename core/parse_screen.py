from __future__ import annotations
import ctypes
import sys
import time
from multiprocessing.sharedctypes import Synchronized
import cv2
import mss
import numpy as np


def parse_my_screen(azimuth: Synchronized[ctypes.c_float], natomil: Synchronized[ctypes.c_uint16]):
    """
    Retrieves and updates azimuth and natomil values in a loop.

    This function continuously processes data using a ParseScreen
    instance to fetch updated values of azimuth and natomil and assigns
    them to shared Synchronized objects for inter-process communication.

    Parameters:
        azimuth (Synchronized[ctypes.c_float]): A synchronized float variable
        that will be updated with the azimuth value fetched from the parser.

        natomil (Synchronized[ctypes.c_uint16]): A synchronized unsigned 16-bit
        integer variable that will be updated with the natomil value fetched
        from the parser.
    """
    print("Creating EasyOCR Instance")
    parser = ParseScreen()
    while True:
        azimuth.value = parser.get_azimuth()
        natomil.value = parser.get_natomil()


class ParseScreen:

    def __init__(self):

        import easyocr
        self.SCREEN_RESOLUTION = None
        self.check_resolution()
        self.AZIMUTH_SCREEN_COORDS = {"top": 1050, "left": 940, "width": 41, "height": 16}
        self.NATOMIL_SCREEN_COORDS = {"top": int(self.SCREEN_RESOLUTION[1] / 2 - 100 / 2),
                                      "left": 530, "width": 60, "height": 110}

        self.reader = easyocr.Reader(['en'], gpu=False)
        self.natomil_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_natomil = 5
        print(f"Initializing EasyOCR")

    def check_resolution(self) -> None:
        print("Checking Resolution")
        try:
            from PySide6.QtGui import QGuiApplication
            app = QGuiApplication(sys.argv)
            width, height = app.primaryScreen().size().toTuple()
            self.SCREEN_RESOLUTION = (width, height)
        except Exception as error:
            raise Exception(f"Error Occured {error}")
        finally:
            del app

    def get_azimuth(self) -> float:
        """
        Retrieves the azimuth value using easyocr from game output. 
        It returns the retrieved azimuth value as a float.
        
        Returns:
            float: The azimuth angle acquired from the OCR results.
        """
        azimuth = self._get_azimuth_ocr_results()
        try:
            return float(azimuth[0])
        except IndexError:
            print("Make sure squad game is in focus")
            time.sleep(2)
            return -1
        except TypeError:
            print("Make sure squad game is in focus")
            time.sleep(2)
            return -1
        except Exception as error:
            raise Exception(f"Error Encountered in get_azimuth:\n{error}")

    def get_natomil(self) -> int:
        """
        Retrieves the Natomil value using easyocr from game output.

        This function calculates the 'Natomil' value by calling the
        `approximate_natomil` method. It validates the result to ensure
        it falls within the expected range.

        Returns:
            int: The natomil value acquired from the OCR results.

        """
        value = self._approximate_natomil()
        try:
            if 800 <= int(value) <= 1580:
                return int(value)
            else:
                return 0
        except IndexError:
            return 0
        except TypeError:
            return 0
        except Exception as error:
            raise Exception(f"Error Encountered in get_natomil:\n{error}")

    def _get_azimuth_ocr_results(self) -> list:
        """
        Captures the azimuth section of the screen and processes it using EasyOCR 
        to detect numerical values representing the NatoMil.
        
        This method uses the specified screen coordinates to capture the screen 
        region where azimuth information is displayed. The captured image is 
        converted to grayscale, threshold to create a binary image, and then 
        passed to EasyOCR for text recognition. 

        Returns:
            list: A list of detected numeric text strings from the processed screen region.

        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.AZIMUTH_SCREEN_COORDS)
            img_gray = cv2.cvtColor(np.asarray(screenshot, dtype=np.uint8), cv2.COLOR_BGRA2GRAY)
            thresh, azimuth_monochrome = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)

            # For Visualization
            # cv2.imshow("Azimuth Screen Capture", azimuth_monochrome)

            return self.reader.readtext(azimuth_monochrome, allowlist=".0123456789", detail=0)

    def _get_natomil_ocr_results(self) -> list:
        """
        Captures the NatoMil section of the screen and processes it using EasyOCR 
        to detect numerical values representing the NatoMil.
        
        This method uses the specified screen coordinates to capture the screen 
        region where azimuth information is displayed. The captured image is 
        converted to grayscale, threshold to create a binary image, and then 
        passed to EasyOCR for text recognition. 
        
        Returns:
            list: A list of detected text elements from EasyOCR, where each element 
                  is a list containing bounding box coordinates, detected text, 
                  and detection confidence.
        """
        with mss.mss() as sct:
            screenshot = sct.grab(self.NATOMIL_SCREEN_COORDS)
            img_gray = cv2.cvtColor(np.asarray(screenshot, dtype=np.uint8), cv2.COLOR_BGRA2GRAY)
            thresh, natomil_monochrome = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

            # For Visualization
            # cv2.imshow("Radian Monochrome Screen Capture", natomil_monochrome)

            return self.reader.readtext(natomil_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                        low_text=0.2, link_threshold=0.2)

    def _approximate_natomil(self) -> int:
        """
         Approximates the NatoMil value from OCR results.

         This function processes detected bounding boxes and their attributes from OCR results
         to calculate the NatoMil value. It uses differences in box positions and a calibration
         factor (pixels per NatoMil) for approximation.

         Returns:
             int: The approximated NatoMil value or 0 if an error occurs.
         """
        try:
            natomil_results = self._get_natomil_ocr_results()
            if not natomil_results:
                time.sleep(1)
                raise ValueError("natomil is empty")

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
                    if not self.box_difference == 0:
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
            raise Exception(f"Error Encountered: {error}")


if __name__ == "__main__":
    pass
