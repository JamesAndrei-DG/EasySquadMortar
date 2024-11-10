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
    fire_solution = FireSolution()
    while True:
        # fire_solution.get_distance()

        if debug:
            global frame_count
            global fps_display_interval
            global fps_last_update_time
            frame_count += 1
            calculate_fps(frame_count, fps_display_interval, fps_last_update_time)

        cv2.waitKey(1)
    cv2.destroyAllWindows()
    pass


class FireSolution:
    # initialization
    velocity_squared = 12100  # velocity squared of mortar we should add more for other input
    gravity = 0.1022495  # for multiplication
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    natomil_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
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
        self.natomil_monochrome = None
        self.natomil_results = None
        self.box_height = [0, 0]
        self.box_position = [0, 0]
        self.box_difference = None
        self.pixel_per_natomil = 5

        while True:
            self.mil = self.get_natomil()
            if self.mil:
                print(f"NATO mil is: {self.mil}")
                break

    def get_distance(self):
        # NATO mil to radian
        # https://en.wikipedia.org/wiki/Milliradian
        # 1 milliradian = 1.018592 NATO mil
        # 1 NATO mil = 0.981719 milliradian
        # edit distance so that we can create height map
        # then create our own parabola and find intersection between heigh map and parabola
        nato_mil = self.get_natomil()
        if nato_mil:
            radian = nato_mil * 0.981719 * 0.001
            distance = self.velocity_squared * numpy.sin(radian * 2) * self.gravity

        else:
            distance = 0
        print(f"distance is: {distance}m")

    def get_natomil_ocr_results(self):  # this will return easyocr results for mil
        with mss.mss() as sct:
            screenshot = sct.grab(self.natomil_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            cv2.imshow("Radian Gray Screen Capture", img_gray)
            (thresh, self.natomil_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)
            cv2.imshow("Radian Monochrome Screen Capture", self.natomil_monochrome)

            return reader.readtext(self.natomil_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                   low_text=0.2, link_threshold=0.2)

    def get_bearing_ocr_results(self):
        with mss.mss() as sct:
            screenshot = sct.grab(self.bearing_screen_coordinates)
            img = numpy.asarray(screenshot, dtype=numpy.uint8)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
            (thresh, self.img_monochrome) = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)
            cv2.imshow("Bearing Screen Capture", self.img_monochrome)

            return reader.readtext(self.img_monochrome, allowlist=".0123456789", detail=0)

    def get_natomil(self):

        self.natomil_results = self.get_natomil_ocr_results()

        if self.natomil_results:
            for index, number in enumerate(self.natomil_results):
                # FOR DEBUG
                if debug:
                    if self.natomil_results:
                        boxnumber = 1
                        for item in self.natomil_results:
                            points = numpy.array([item[0][0], item[0][1], item[0][2], item[0][3]],
                                                 dtype=numpy.float32)
                            # Get the minimum area rectangle
                            rect = cv2.minAreaRect(points)

                            # Get the four corner points of the rectangle
                            box = cv2.boxPoints(rect)
                            box = numpy.intp(box)  # Convert the points to integer
                            cv2.polylines(self.natomil_monochrome, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                            # cv2.imshow("Radian Boxed Monochrome Screen Capture", self.natomil_monochrome)
                            boxnumber += 1

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
                        print(f"NATO mil is: {natomil}")

                        # this should return the approximate mil calculated from the pixel difference and the mil detected
                        if natomil:
                            return natomil
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


if __name__ == "__main__":
    main()
