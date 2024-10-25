import mss
import cv2
import numpy
import easyocr
import time

try:
    import Image
except ImportError:
    from PIL import Image

# EasyOCR Config
reader = easyocr.Reader(['en'])

# For Debug
debug = 1
frame_count = 0
fps_display_interval = 1  # Update FPS every 1 second
fps_last_update_time = time.time()


def main():
    # Add Exit

    fire_solution = FireSolution()
    while True:

        fire_solution.get_distance()
        if debug:
            global frame_count
            global fps_display_interval
            global fps_last_update_time
            frame_count += 1
            calculate_fps(frame_count, fps_display_interval, fps_last_update_time)

        cv2.waitKey(1)  # do i need this?
    cv2.destroyAllWindows()


class FireSolution:
    # initialization
    velocity_squared = 12100  # velocity squared of mortar we should add more for other input
    gravity = 0.1020408  # for multiplication
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    radian_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                 "left": 530, "width": 60, "height": 110}

    # value[1] for the second number only if detected
    # value[x][0] list of coordinates starting from index[0] = top left and proceeding clockwise
    # value[x][1] Detected Number
    # value[x][2] Probability

    def __init__(self):
        if debug:
            print("Initializing FireSolution Class")
            # this function will call the getheight which will have look into get_approximate_radian with a few second delay to get the average
            # self.average_height = self.get_height() #this must return a list
            print("Getting Bearing")
        while True:
            self.bearing = self.get_bearing()
            if self.bearing:
                print(f"Bearing is: {self.bearing}")
                break

        if debug:
            print("Getting Radian")
        # Variables for radians
        self.radian_monochrome = None
        self.radian_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_mills = 5

        while True:
            self.radian = self.get_radian()
            if self.radian:
                print(f"Radian is: {self.radian}")
                break

    def get_distance(self):
        bearing = self.get_bearing()
        radian = self.get_radian() * 0.001
        distance = self.velocity_squared * numpy.sin(radian * 2) * self.gravity
        print(f"distance is: {distance}m")

    def get_radian_ocr_results(self):  # this will return easyocr results for radian
        # we should follow get_bearing_ocr_results for consistency
        with mss.mss() as sct:
            screenshot = sct.grab(self.radian_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            cv2.imshow("Radian Gray Screen Capture", img_gray)
            (thresh, self.radian_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)
            cv2.imshow("Radian Monochrome Screen Capture", self.radian_monochrome)

            return reader.readtext(self.radian_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                   low_text=0.2, link_threshold=0.2)

    def get_bearing_ocr_results(self):
        with mss.mss() as sct:
            screenshot = sct.grab(self.bearing_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            (thresh, self.img_monochrome) = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)
            cv2.imshow("Bearing Screen Capture", self.img_monochrome)

            return reader.readtext(self.img_monochrome, allowlist=".0123456789", detail=0)

    def get_radian(self):

        self.radian_results = self.get_radian_ocr_results()

        if self.radian_results:
            for index, number in enumerate(self.radian_results):
                # compute box height
                top_left_y_axis = number[0][0][1]
                bot_left_y_axis = number[0][3][1]
                screen_edge = self.radian_screen_coordinates["height"]
                tolerance = 1  # number tolerance for pixel

                # check if the box is on edge or not
                if top_left_y_axis != 0 and bot_left_y_axis != screen_edge:
                    self.box_height[index] = int(bot_left_y_axis - top_left_y_axis)

                # get box position
                if self.box_height[index] != 0:
                    self.box_position[index] = bot_left_y_axis - (self.box_height[index] * 0.5)

                if index == 1:
                    self.box_difference = self.box_position[1] - self.box_position[0]
                    self.pixel_per_mills = self.box_difference * 0.1

                    # add a way to track if it jumping or not
                if index == 0:
                    radian = 0
                    if number[2] >= 0.8:
                        radian = int(number[1]) + int((self.box_position[0] - 50) / self.pixel_per_mills)
                        # print(f"Radian is: {radian}")

            if debug:
                if self.radian_results:
                    boxnumber = 1
                    for item in self.radian_results:
                        points = numpy.array([item[0][0], item[0][1], item[0][2], item[0][3]],
                                             dtype=numpy.float32)
                        # Get the minimum area rectangle
                        rect = cv2.minAreaRect(points)

                        # Get the four corner points of the rectangle
                        box = cv2.boxPoints(rect)
                        box = numpy.intp(box)  # Convert the points to integer
                        cv2.polylines(self.radian_monochrome, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                        cv2.imshow("Radian Boxed Monochrome Screen Capture", self.radian_monochrome)
                        boxnumber += 1

                # this should return the approximate radian calculated from the pixel difference and the radian detected
            if radian:
                return radian
            else:
                return 0

    def get_bearing(self):
        return self.get_bearing_ocr_results()


def calculate_fps(frame_count, fps_display_interval, last_time):
    if debug:
        current_time = time.time()
        elapsed_time = current_time - last_time
        if elapsed_time > fps_display_interval:
            fps = frame_count / elapsed_time
            ms_per_frame = (elapsed_time / frame_count) * 1000
            last_time = current_time
            frame_count = 0
            # print(f"FPS: {fps:.2f}, Frame Time: {ms_per_frame:.2f} ms")
        return last_time, frame_count


main()
