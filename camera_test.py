import cv2
cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

if not cap.isOpened():
    print("Camera failed to open")
    exit()

if faceCascade.empty():
    print("Face cascade failed to load")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    biggestFace = None
    biggestArea = 0

    for (x, y, w, h) in faces:
        area = w * h

        if area > biggestArea:
            biggestArea = area
            biggestFace = (x, y, w, h)

    if biggestFace is not None:
        x, y, w, h = biggestFace

        faceCenterX = x + w // 2
        faceCenterY = y + h // 2

        cv2.circle(frame, (faceCenterX, faceCenterY), 8, (0, 0, 255), -1)

        cv2.putText(
            frame,
            f"faceCenterY = {faceCenterY}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 0, 0),
            2
        )

    else:
        cv2.putText(frame, "No face found", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Show the camera image.
    cv2.imshow("The frame", frame)

    # Quit when q is pressed.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up when finished.
cap.release()
cv2.destroyAllWindows()