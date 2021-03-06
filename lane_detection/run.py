import cv2
from matplotlib import pyplot as plt
import numpy as np
from collections import deque
from moviepy.editor import VideoFileClip
import os


def convert_hls(image):
    return cv2.cvtColor(image, cv2.COLOR_RGB2HLS)


def gray_scale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)


def white_yellow(image):
    converted = convert_hls(image)
    # white color mask
    lower = np.uint8([0, 200,   0])
    upper = np.uint8([255, 255, 255])
    white_mask = cv2.inRange(converted, lower, upper)
    # yellow color mask
    lower = np.uint8([90,   80, 100])
    upper = np.uint8([110, 255, 255])
    yellow_mask = cv2.inRange(converted, lower, upper)
    # combine the mask
    mask = cv2.bitwise_or(white_mask, yellow_mask)
    return cv2.bitwise_and(image, image, mask=mask)


def gaussian_smoothing(img, kernel_size=15):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)


def canny_edges(img, low=50, high=150):
    return cv2.Canny(img, low, high)


def filter_region(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    return cv2.bitwise_and(img, mask)


def interest_region(img):
    rows, cols = img.shape
    bottom_left = [cols*0.1, rows*0.95]
    top_left = [cols*0.4, rows*0.6]
    bottom_right = [cols*0.9, rows*0.95]
    top_right = [cols*0.6, rows*0.6]
    vertices = np.array([[bottom_left, top_left, top_right,
                          bottom_right]], dtype=np.int32)
    return filter_region(img, vertices)


def hough_lines(img):
    return cv2.HoughLinesP(img, rho=1, theta=np.pi/180, threshold=20, minLineLength=20, maxLineGap=300)


def _average_lines(lines):
    left_lanes = []
    left_weights = []
    right_lanes = []
    right_weights = []

    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x1 == x2:
            # skip vertical lines
            continue

        slope = (y2 - y1)/(x2 - x1)
        y_intercept = y1 - slope * x1
        length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # y is reversed
        if slope > 0:
            right_lanes.append((slope, y_intercept))
            right_weights.append((length))
        else:
            left_lanes.append((slope, y_intercept))
            left_weights.append((length))

    left_lane = np.dot(left_weights, left_lanes) / np.sum(left_weights) if len(left_lanes) > 0 else None
    right_lane = np.dot(right_weights, right_lanes) / np.sum(right_weights) if len(right_lanes) > 0 else None
    return left_lane, right_lane


def lane_lines(img, lines):
    left_line, right_line = _average_lines(lines)

    y1 = img.shape[0] * 0.9
    y2 = y1 * 0.6
    print(left_line)
    if left_line is not None:
        # left line
        x1 = (y1 - left_line[1]) / left_line[0]
        x2 = (y2 - left_line[1]) / left_line[0]
        left_line = ((int(x1), int(y1)), (int(x2), int(y2)))
    if right_line is not None:
        # right line
        x1 = (y1 - right_line[1]) / right_line[0]
        x2 = (y2 - right_line[1]) / right_line[0]
        right_line = ((int(x1), int(y1)), (int(x2), int(y2)))

    return left_line, right_line

def draw_lines(img, lines):
    img_lines = np.zeros_like(img)
    for line in lines:
        cv2.line(img_lines, line[0], line[1], (0, 0, 255), 10)

    return cv2.addWeighted(img, 1, img_lines, 1, 0)

class LaneDetector():

    def __init__(self):
        self.left_lines = deque(maxlen=50)
        self.right_lines = deque(maxlen=50)

    def process(self, img):
        img_processed = white_yellow(img)
        
        img_processed = gray_scale(img_processed)
        img_processed = gaussian_smoothing(img_processed)
        img_processed = canny_edges(img_processed)
        img_processed = interest_region(img_processed)
        lines = hough_lines(img_processed)
        left_line, right_line = lane_lines(img_processed, lines)

        # store lines
        if left_line is not None:
            self.left_lines.append(left_line)
        if right_line is not None:
            self.right_lines.append(right_line)

        # mean lines
        if len(self.left_lines) > 0:
            left_line = tuple(
                map(tuple, np.mean(self.left_lines, axis=0, dtype=np.int32)))
        if len(self.right_lines) > 0:
            right_line = tuple(
                map(tuple, np.mean(self.right_lines, axis=0, dtype=np.int32)))

        final_img = draw_lines(img, [left_line, right_line])
        
        return final_img

    def process_video(self, input, output):
        clip = VideoFileClip(input)
        processed = clip.fl_image(detector.process)
        processed.write_videofile(output, audio=False)


if __name__ == "__main__":
    detector = LaneDetector()

    img_original = cv2.imread('./lane_detection/images/YellowWhite.jpg')  # rgb
    img = detector.process(img_original)
    
    # cv2.imshow('image', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    input_video = os.path.join(
        'lane_detection', 'videos', 'input', 'challenge.mp4')
    output_video = os.path.join(
        'lane_detection', 'videos', 'output', 'challenge-output.mp4')
    detector.process_video(input_video, output_video)
