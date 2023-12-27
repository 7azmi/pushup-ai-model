import os

import cv2
import math
from cvzone.PoseModule import PoseDetector
from memory_profiler import memory_usage
import time
import requests
import tempfile

# Constants
VIDEO_PATH = 'samples/vid14.mp4'
TRACK_CONFIDENCE = 0.50
DETECTION_CONFIDENCE = 0.9
FRAME_SKIP = 3
CIRCLE_RADIUS = 10
CIRCLE_THICKNESS = 5
LINE_THICKNESS = 6
HUD_FONT = cv2.FONT_HERSHEY_SIMPLEX
HUD_COLOR = (0, 255, 0)
HUD_SCALE = 1.0

# Initialize variables
counter = 0
direction = 0
frame_count = 0

# Set up video capture and pose detector
# cap = cv2.VideoCapture(VIDEO_PATH)
# if not cap.isOpened():
#    raise IOError("Cannot open video file")
pd = PoseDetector(trackCon=TRACK_CONFIDENCE, detectionCon=DETECTION_CONFIDENCE)


def get_video_cap_from_path(path):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise IOError("Cannot open video file")
    return cap


def draw_pose_points_and_lines(img, points, drawpoints):
    if drawpoints:
        for i in range(0, len(points), 2):
            cv2.circle(img, points[i], CIRCLE_RADIUS, (255, 0, 255), CIRCLE_THICKNESS)
            cv2.circle(img, points[i], CIRCLE_RADIUS + 5, (0, 255, 0), CIRCLE_THICKNESS)
            if i + 1 < len(points):
                cv2.line(img, points[i], points[i + 1], (0, 0, 255), LINE_THICKNESS)


def calculate_angle(p1, p2, p3):
    angle = math.degrees(math.atan2(p3[1] - p2[1], p3[0] - p2[0]) -
                         math.atan2(p1[1] - p2[1], p1[0] - p2[0]))
    return angle


def update_counter(left_angle, right_angle, global_counter, global_direction):
    direction = global_direction
    counter = global_counter
    if left_angle >= 70 and right_angle >= 70 and direction == 0:
        counter += 0.5
        direction = 1
    elif left_angle <= 70 and right_angle <= 70 and direction == 1:
        counter += 0.5
        direction = 0
    return counter, direction


def angles(img, lmlist, points_indices, drawpoints):
    global counter, direction
    if lmlist:
        points = [lmlist[i][0:2] for i in points_indices]
        draw_pose_points_and_lines(img, points, drawpoints)
        lefthand_angle = calculate_angle(*points[:3])
        righthand_angle = calculate_angle(*points[3:])
        counter, direction = update_counter(lefthand_angle, righthand_angle, counter, direction)
        display_hud(img, counter)


def display_hud(img, counter):
    cv2.putText(img, f'Count: {int(counter)}', (30, 30), HUD_FONT, HUD_SCALE, HUD_COLOR, 2)


def process_frame(img, drawpoints):
    global frame_count
    if frame_count % FRAME_SKIP != 0:
        return img  # Return the unprocessed frame

    # Convert image to UMat to process on GPU
    gpu_img = cv2.UMat(img)

    # Resize using GPU
    gpu_img = cv2.resize(gpu_img, (900, 900))

    img = cv2.resize(img, (900, 900))
    pd.findPose(img, draw=False)
    lmlist, _ = pd.findPosition(img, draw=False)
    angles(img, lmlist, [11, 13, 15, 12, 14, 16], drawpoints)
    #if drawpoints:
    #    display_hud(img, counter)
    #return img  # Return the annotated frame
    result_img = gpu_img.get() if drawpoints else img

    return result_img


# for testing
def calculate_pushups():
    cap = get_video_cap_from_path(VIDEO_PATH)
    global counter, frame_count
    counter = 0
    frame_count = 0
    while True:
        ret, img = cap.read()
        frame_count += 1
        if not ret:
            break
        process_frame(img, drawpoints=False)
    cap.release()
    return int(counter)


def calculate_pushups_from_stream(video_stream):
    global counter, frame_count
    counter = 0
    frame_count = 0
    while True:
        ret, img = video_stream.read()
        frame_count += 1
        if not ret:
            break
        process_frame(img, drawpoints=False)
    return int(counter)


# doesn't work yet
def calculate_and_annotate_pushups(video_stream):
    global counter, frame_count
    counter = 0
    frame_count = 0
    annotated_frames = []
    while True:
        ret, img = video_stream.read()
        frame_count += 1
        if not ret:
            break
        annotated_frame = process_frame(img, drawpoints=True)
        annotated_frames.append(annotated_frame)
    return int(counter), annotated_frames

def download_video(url):
    response = requests.get(url)
    if response.status_code == 200:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        temp_file.write(response.content)
        temp_file.close()
        return temp_file.name
    return None

def count_pushups(videourl):
    video_path = download_video(videourl)
    if video_path:
        # Here you can integrate your existing pose detection and pushup counting logic
        # For example:
        pushup_counter = calculate_pushups_from_stream(cv2.VideoCapture(video_path))
        os.unlink(video_path)  # delete the temporary file
        return pushup_counter
    else:
        return "Error downloading video"



def testing_wrapper():
    global pushups
    pushups = calculate_pushups()
    print('pushups: ' + str(pushups))


# Measuring CPU Time & Memory
def measure():
    start_time = time.time()
    mem_usage = memory_usage(testing_wrapper)
    end_time = time.time()
    cpu_time = end_time - start_time

    # Output
    print(f"CPU Time: {cpu_time} seconds")
    print(f"Peak Memory Usage: {max(mem_usage)} MiB")


#video_url = "https://api.telegram.org/file/bot6088899662:AAGP8lQ9GixY3UVjmMwK4idtZBnCY030lSE/videos/file_3.MP4"
#print(count_pushups(video_url))

#measure()
#pushups = calculate_pushups()
#print(pushups)
#pushups = calculate_pushups()
#pushups = calculate_pushups_from_stream(get_video_cap_from_path(VIDEO_PATH))
#print(pushups)
# count, frames = calculate_and_annotate_pushups(get_video_cap_from_path(VIDEO_PATH))
# count = calculate_pushups_from_stream(get_video_cap_from_path(VIDEO_PATH))
# print(count)
# print(frames)
# pushups = calculate_pushups()
# print(pushups)
# testing
#
# while True:
#     ret, img = cap.read()
#     frame_count += 1
#
#     if not ret:
#         break
#
#     if frame_count % FRAME_SKIP != 0:
#         continue  # Skip frame
#
#     img = cv2.resize(img, (900, 900))  # Lower resolution for efficiency
#     pd.findPose(img, draw=False)
#     lmlist, _ = pd.findPosition(img, draw=False)
#
#     angles(lmlist, [11, 13, 15, 12, 14, 16], drawpoints=True)
#
#     cv2.imshow('AI Push Up Counter', img)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# cap.release()
# cv2.destroyAllWindows()
