# from cmu_cpcs_utils import *
# Done by ChatGPT
import cv2

# This creates a camera object.
# 0 usually means the default camera.
# On your Mac, you may need to change 0 to 1 if the wrong camera opens.
cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)
bgSubtractor = cv2.createBackgroundSubtractorMOG2()
# cap.isOpened() checks whether the camera opened successfully.
if not cap.isOpened():
    print("Camera failed to open")
    exit()

print("Camera opened successfully")
print("Press q to quit")

# This loop keeps running until we quit.
while True:
    # cap.read() tries to get one frame from the camera.
    # ret is True if it worked.
    # frame is the actual image from the camera.
    ret, frame = cap.read()
    fgMask = bgSubtractor.apply(frame)
    # If reading the frame failed, stop the program.
    if not ret:
        print("Failed to read frame")
        break

    # Show the current camera image in a window named "camera".
    cv2.imshow("camera", frame)
    cv2.imshow("mask", fgMask)

    contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.waitKey(1) waits a tiny bit for keyboard input.
    # If the key pressed is q, we exit the loop.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    # Find the contours in the foreground mask and tallest point which will be the head of the person.
    tallest_point = None
    for contour in contours:
        if cv2.contourArea(contour) < 500:  # Filter out small contours
            continue
        # (x, y): top-left corner of the bounding box, w: width, h: height
        x, y, w, h = cv2.boundingRect(contour)
        if tallest_point is None or y < tallest_point[1]:
            tallest_point = (x + w // 2, y)  # Get the center of the top edge of the bounding box

# Release the camera when we are done.
cap.release()

# Close all OpenCV windows.
cv2.destroyAllWindows()