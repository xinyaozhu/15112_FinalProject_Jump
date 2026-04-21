from cmu_graphics import *
import cv2

def onAppStart(app):
    # --- Camera setup ---
    app.cap = cv2.VideoCapture(1, cv2.CAP_AVFOUNDATION)

    app.faceCascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )

    # --- Face tracking data ---
    app.faceCenterY = 0
    app.baselineY = None
    app.squatDepth = 0

    # --- Player ---
    app.playerX = 200
    app.playerY = 300

    # Smooth face
    app.smoothedFaceY = None

def onStep(app):
    ret, frame = app.cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = app.faceCascade.detectMultiScale(
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

        faceCenterY = y + h // 2
        app.faceCenterY = faceCenterY

        # Smooth the face y-value so it does not jump too much.
        if app.smoothedFaceY is None:
            app.smoothedFaceY = faceCenterY
        else:
            app.smoothedFaceY = 0.9 * app.smoothedFaceY + 0.1 * faceCenterY

        # Set baseline the first time
        if app.baselineY is None:
            app.baselineY = app.smoothedFaceY

        # Compute squat depth
        app.squatDepth = app.smoothedFaceY - app.baselineY

    # --- TEST CONNECTION ---
    # Move player based on squatDepth
    app.playerY = int(300 + app.squatDepth)

def redrawAll(app):
    # Background
    drawRect(0, 0, 400, 600, fill='lightblue')

    # Player
    drawCircle(app.playerX, app.playerY, 20, fill='red')

    # Debug text
    drawLabel(f"squatDepth: {int(app.squatDepth)}", 200, 50, size=20)
    drawLabel(f"baselineY: {app.baselineY}", 200, 80, size=16)

runApp(width=400, height=600)
cmu.graphics.run()