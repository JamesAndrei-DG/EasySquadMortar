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
        # Velocity is 110m/s for mortars

        fire_solution.get_bearing()
        fire_solution.get_radian()
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
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    radian_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                 "left": 530, "width": 60, "height": 100}

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
        self.radian_monochrome = None
        while True:
            self.radian = self.get_radian()
            if self.radian:
                print(f"Radian is: {self.radian}")
                break

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

        value = self.get_radian_ocr_results()
        # check if value is divisible by 50 as it is height > 25 usually 37
        # first check if the height of the first point (top left) is less than half of the total height of screen coordinate

        # create input where it will find the number of pixel space between 2 milliradian (can i use opencv again?) for my screen 6 pixels between

        # create algo that will surely check the box height
        # boxheight = [35,25]

        for item in value:
            if item[0][0][1] == 0:  # for numbers that are on the top edge
                big = False

            number = int(item[1])
            # item[0][2]-item[0][0]

            if number % 50 == 0:
                big = True
                # early return
        if debug:
            if value:
                boxnumber = 1
                for item in value:
                    points = numpy.array([item[0][0], item[0][1], item[0][2], item[0][3]],
                                         dtype=numpy.float32)

                    boxheight = int(item[0][2][1] - item[0][0][1])
                    print(f"box#{boxnumber} height: {boxheight}")

                    # Get the minimum area rectangle
                    rect = cv2.minAreaRect(points)

                    # Get the four corner points of the rectangle
                    box = cv2.boxPoints(rect)
                    box = numpy.intp(box)  # Convert the points to integer
                    cv2.polylines(self.radian_monochrome, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                    cv2.imshow("Radian Boxed Monochrome Screen Capture", self.radian_monochrome)
                    boxnumber += 1

        return value

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
            print(f"FPS: {fps:.2f}, Frame Time: {ms_per_frame:.2f} ms")
        return last_time, frame_count


main()
