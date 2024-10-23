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

    fire_solution = FireSolution
    while True:
        # Velocity is 110m/s for mortars
        get_distance.getdistance

        if debug:
            global frame_count
            global fps_display_interval
            global fps_last_update_time
            frame_count += 1
            calculate_fps(frame_count, fps_display_interval, fps_last_update_time)

        cv2.waitKey(1)
    cv2.destroyAllWindows()

class FireSolution:
    #initalization
    screen_resolution = (1920, 1080)
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}
    radian_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                 "left": 530, "width": 60, "height": 100}

    # value[1] for the second number only if detected
    # value[x][0] list of coordinates starting from index[0] = top left and proceeding clockwise
    # value[x][1] Detected Number
    # value[x][2] Probability

    def __init__(self):
        # this function will call the getheight which will look into the values of getradian
        self.


    def main_get_radian():
        # bearing = getbearing(bearing_screen_coordinates)
        radian = getradian(radian_screen_coordinates)


    def get_distance():


        # bearing = getbearing(bearing_screen_coordinates)
        radian = getradian(radian_screen_coordinates)

        # value[1] for the second number only if detected
        # value[x][0] list of coordinates starting from index[0] = top left and proceeding clockwise
        # value[x][1] Detected Number
        # value[x][2] Probability
        # if radian:
        # if radian[0][0][4]:
        # print(f"probability is: {radian[0][0][5]}")
        # degree = angle/360

        return 1







    pass



def main_get_bearing(screencoordinates):
    with mss.mss() as sct:
        screenshot = sct.grab(screencoordinates)
        img = numpy.asarray(screenshot, dtype=numpy.uint8)

        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # Convert to monochrome
        (thresh, img_monochrome) = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)

        # Display the grayscale image
        cv2.imshow("Monochrome Screen Capture", img_monochrome)

        return reader.readtext(img_monochrome, allowlist="0,1,2,3,4,5,6,7,8,9")


def getradian(screencoordinates):
    initialized = False

    with mss.mss() as sct:
        screenshot = sct.grab(screencoordinates)
        img = numpy.asarray(screenshot, dtype=numpy.uint8)

        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        cv2.imshow("Gray Image", img_gray)

        # Convert to monochrome
        (thresh, img_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

        # Display the grayscale image
        cv2.imshow("Monochrome Screen Capture", img_monochrome)
        value = reader.readtext(img_monochrome, allowlist="0123456789", mag_ratio=2, text_threshold=0.80,
                                low_text=0.2, link_threshold=0.2)

        # check if value is divisible by 50 as it is height > 25 usually 37

        # first check if the height of the first point (top left) is less than half of the total height of screen coordinate

        # create input where it will find the number of pixel space between 2 milliradian (can i use opencv again?) for my screen 6 pixels between

        #create algo that will surely check the box height
        #boxheight = [35,25]

        BearingInit()


        for item in value:
            if item[0][0][1] == 0: #for numbers that are on the top edge
                big = False


            number = int(item[1])
            #item[0][2]-item[0][0]

            if number % 50 == 0:
                big = True
                # early return








        if debug:
            if value:
                boxnumber = 1
                for item in value:
                    points = numpy.array([item[0][0], item[0][1], item[0][2], item[0][3]],
                                         dtype=numpy.float32)

                    boxheight = int(item[0][2][1]-item[0][0][1])
                    print(f"box#{boxnumber} height: {boxheight}")


                    # Get the minimum area rectangle
                    rect = cv2.minAreaRect(points)

                    # Get the four corner points of the rectangle
                    box = cv2.boxPoints(rect)
                    box = numpy.intp(box)  # Convert the points to integer
                    cv2.polylines(img_monochrome, [box], isClosed=True, color=(0, 255, 0), thickness=2)
                    cv2.imshow("Monochrome Screen Capture", img_monochrome)
                    boxnumber += 1

        return value


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
