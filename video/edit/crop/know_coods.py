# check the coordinates by clicking on the video frame
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.Crop import Crop
from moviepy.video.fx.Resize import Resize
import cv2

def click_and_know_coordinates_from_video(video_path):
    global ref_point, cropping
    ref_point = []
    cropping = False

    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Failed to read video frame.")
        return None

    clone = frame.copy()
    cv2.namedWindow("frame")
    cv2.setMouseCallback("frame", lambda event, x, y, flags, param: mouse_callback(event, x, y, flags, param, frame))

    print("Press 'r' to reset selection, 'c' to confirm selection.")
    while True:
        cv2.imshow("frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("r"):
            frame = clone.copy()
        elif key == ord("c"):
            break

    cv2.destroyAllWindows()

    if len(ref_point) == 2:
        x1, y1 = ref_point[0]
        x2, y2 = ref_point[1]
        print(f"upper: {min(y1,y2)}, lower: {max(y1,y2)}, left: {min(x1,x2)}, right: {max(x1,x2)}")
        return (min(y1,y2), max(y1,y2), min(x1,x2), max(x1,x2))
    else:
        print("No points selected.")
        return None

def mouse_callback(event, x, y, flags, param, image):
    global ref_point, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        ref_point = [(x, y)]
        cropping = True
    elif event == cv2.EVENT_LBUTTONUP:
        ref_point.append((x, y))
        cropping = False
        cv2.rectangle(image, ref_point[0], ref_point[1], (0, 255, 0), 2)
        cv2.imshow("frame", image)