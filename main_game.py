from random import Random

from cmu_graphics import *
import cv2

def drawGhost(cx, cy):
    # ghost body
    drawCircle(cx, cy - 20, 20, fill='white')
    drawRect(cx - 20, cy - 20, 40, 40, fill='white')

    # bottom of ghost (wavy)
    drawCircle(cx - 12, cy + 20, 8, fill='white')
    drawCircle(cx, cy + 20, 8, fill='white')
    drawCircle(cx + 12, cy + 20, 8, fill='white')

    # eyes of ghost
    drawCircle(cx - 6, cy - 20, 4, fill='black')
    drawCircle(cx + 6, cy - 20, 4, fill='black')

    # mushroom position relative to ghost
    mx = cx + 10
    my = cy + 8

    # mushroom stem (with black border)
    drawRect(mx - 2, my + 2, 4, 6, fill='beige', border='black', borderWidth=0.5)

    # mushroom cap (with black border)
    drawCircle(mx, my, 4.5, fill='red', border='black', borderWidth=0.5)

    # white spots on mushroom (draw after to be on top)
    drawCircle(mx - 2, my - 2, 1, fill='beige')
    drawCircle(mx + 2, my - 2, 1, fill='beige')
    drawCircle(mx, my + 1, 1, fill='beige')

    # little leaves on stem
    drawCircle(cx - 3, cy - 48, 3, fill='green')
    drawCircle(cx + 3, cy - 48, 3, fill='green')
    drawLine(cx, cy - 40, cx, cy - 48, fill='green', lineWidth=2)

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
    app.playerX = app.width // 2
    app.playerY = app.height // 2

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
    drawRect(0, 0, app.width, app.height, fill='lightblue')

    # Player
    drawCircle(app.playerX, app.playerY, 20, fill='red')

    # Debug text
    drawLabel(f"squatDepth: {int(app.squatDepth)}", app.width // 2, 50, size=20)
    drawLabel(f"baselineY: {app.baselineY}", app.width // 2, 80, size=16)

    drawGhost(app.playerX, app.playerY)
    

runApp(width=400, height=600)
cmu.graphics.run()