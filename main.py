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


def main():
    frame_count = 0
    fps_display_interval = 1  # Update FPS every 1 second
    fps_last_update_time = time.time()

    #Add Exit
    while True:

        getdistance()




        #CalculateRadian(radian[][][])

        calculate_fps(frame_count, fps_display_interval, fps_last_update_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break



def getdistance():
    screen_resolution = (1920, 1080)

    # create a function so that it scales with screen resolution
    bearing_screen_coordinates = {"top": 1050, "left": 940, "width": 41, "height": 16}

    radian_screen_coordinates = {"top": int(screen_resolution[1] / 2 - 100 / 2),
                                 "left": 530, "width": 60, "height": 100}

    #bearing = getbearing(bearing_screen_coordinates)
    radian = getradian(radian_screen_coordinates)

    # value[0][1] for second number detected
    # value[0][0][0] first coordinate of the first number top left
    # value[0][0][1] second coordinate top right
    # value[0][0][2] third coordinate bot right
    # value[0][0][3] third coordinate bot left
    if radian:
        # check if there is 2 numbers found
        print(f"radian: {radian[0]}")
        print(f"length: {len(radian[0])}")




def getbearing(bearingcoord):
    with mss.mss() as sct:
        screenshot = sct.grab(bearingcoord)
        img = numpy.asarray(screenshot, dtype=numpy.uint8)

        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

        # Convert to monochrome
        (thresh, img_monochrome) = cv2.threshold(img_gray, 170, 255, cv2.THRESH_BINARY)

        # Display the grayscale image
        cv2.imshow("Monochrome Screen Capture", img_monochrome)

        return reader.readtext(img_monochrome, allowlist="0,1,2,3,4,5,6,7,8,9")


def getradian(radiancoord):
    with mss.mss() as sct:
        screenshot = sct.grab(radiancoord)
        img = numpy.asarray(screenshot, dtype=numpy.uint8)

        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        cv2.imshow("Gray Image", img_gray)

        # Convert to monochrome
        (thresh, img_monochrome) = cv2.threshold(img_gray, 140, 255, cv2.THRESH_BINARY)

        # Display the grayscale image
        cv2.imshow("Monochrome Screen Capture", img_monochrome)
        value = reader.readtext(img_monochrome, allowlist="0,1,2,3,4,5,6,7,8,9", mag_ratio=2, text_threshold=0.80,
                                low_text=0.2, link_threshold=0.2)



        if value:
            points = numpy.array([value[0][0][0], value[0][0][1], value[0][0][2], value[0][0][3]], dtype=numpy.float32)


            # For Debug Purposes
            # Get the minimum area rectangle
            rect = cv2.minAreaRect(points)

            # Get the four corner points of the rectangle
            box = cv2.boxPoints(rect)
            box = numpy.intp(box)  # Convert the points to integer
            cv2.polylines(img_monochrome, [box], isClosed=True, color=(0, 255, 0), thickness=2)
            cv2.imshow("Monochrome Screen Capture", img_monochrome)

        return value


def calculate_fps(frame_count, fps_display_interval, last_time):
    current_time = time.time()
    if current_time - last_time > fps_display_interval:
        fps = frame_count / (current_time - last_time)
        last_time = current_time
        frame_count = 0
        # print(f"FPS: {fps:.2f}")
    return last_time, frame_count


main()
