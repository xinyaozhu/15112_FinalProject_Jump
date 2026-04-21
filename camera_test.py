import cv2

# Open the camera.
# Change 1 to 0 or 2 if needed on your computer.
cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

# This loads OpenCV's built-in face detector.
# It is an XML file that comes with OpenCV.
faceCascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# Make sure the camera opened correctly.
if not cap.isOpened():
    print("Camera failed to open")
    exit()

# Make sure the face detector loaded correctly.
if faceCascade.empty():
    print("Face cascade failed to load")
    exit()

print("Camera opened successfully")
print("Press q to quit")

while True:
    # Read one frame from the camera.
    ret, frame = cap.read()

    # If reading the frame failed, stop the program.
    if not ret:
        print("Failed to read frame")
        break

    # Convert the color image to grayscale.
    # Face detection usually works better on grayscale images.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image.
    # scaleFactor and minNeighbors control how the detector works.
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    # We will track the largest detected face.
    biggestFace = None
    biggestArea = 0

    # Look through every detected face.
    for (x, y, w, h) in faces:
        area = w * h

        # Keep the largest face.
        # This is usually the person's face closest to the camera.
        if area > biggestArea:
            biggestArea = area
            biggestFace = (x, y, w, h)

    # If a face was found, draw it.
    if biggestFace is not None:
        x, y, w, h = biggestFace

        # Draw a green rectangle around the face.
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Find the center of the face box.
        faceCenterX = x + w // 2
        faceCenterY = y + h // 2

        # Draw a red dot at the center of the face.
        cv2.circle(frame, (faceCenterX, faceCenterY), 8, (0, 0, 255), -1)

        # Show the face center Y value on the screen.
        cv2.putText(
            frame,
            f"faceCenterY = {faceCenterY}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

        # Optional debug print
        print("faceCenterY =", faceCenterY)

    else:
        # If no face is found, show a message.
        cv2.putText(
            frame,
            "No face found",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2
        )

    # Show the camera image.
    cv2.imshow("camera", frame)

    # Quit when q is pressed.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up when finished.
cap.release()
cv2.destroyAllWindows()