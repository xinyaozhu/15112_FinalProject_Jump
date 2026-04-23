from random import random
from cmu_graphics import *
import cv2

def drawGhost(cx, cy):
    drawCircle(cx, cy - 20, 20, fill='white')
    drawRect(cx - 20, cy - 20, 40, 40, fill='white')

    drawCircle(cx - 12, cy + 20, 8, fill='white')
    drawCircle(cx, cy + 20, 8, fill='white')
    drawCircle(cx + 12, cy + 20, 8, fill='white')

    drawCircle(cx - 6, cy - 20, 4, fill='black')
    drawCircle(cx + 6, cy - 20, 4, fill='black')

    mx = cx + 10
    my = cy + 8

    drawRect(mx - 2, my + 2, 4, 6, fill='beige', border='black', borderWidth=0.5)

    drawCircle(mx, my, 4.5, fill='red', border='black', borderWidth=0.5)

    drawCircle(mx - 2, my - 2, 1, fill='beige')
    drawCircle(mx + 2, my - 2, 1, fill='beige')
    drawCircle(mx, my + 1, 1, fill='beige')

    drawCircle(cx - 3, cy - 48, 3, fill='green')
    drawCircle(cx + 3, cy - 48, 3, fill='green')
    drawLine(cx, cy - 40, cx, cy - 48, fill='green', lineWidth=2)

def drawBox(x, y, w, h):
    # top of the box
    drawRect(x, y, w, h, fill='sienna', border='black')

    # front side to make it look thicker
    drawRect(x, y + h, w, 10, fill='peru', border='black')

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

    # --- Platforms ---
    first = (70, 330, 100, 18)
    p2 = (220, 280, 100, 18)
    p3 = (90, 220, 100, 18)
    app.platforms = [first, p2, p3]

    # Horizontal movement
    app.isCharging = False
    app.maxSquatDepth = 0
    app.isJumping = False
    app.playerVY = 0
    app.playerVX = 0
    app.currentPlatformIndex = 0
    app.gameOver = False
    app.jumpDirection = 1
    app.jumpYScale = 0.9
    app.jumpXScale = 0.4

    # --- Player ---
    # Place the ghost on the first platform
    app.playerX = first[0] + first[2] // 2
    app.playerY = first[1] - 25

    app.maxSquatDepth = 0

    # this is the y-value where the ghost stands on the first box
    first = app.platforms[0]
    app.groundY = first[1] - 25
    app.playerY = app.groundY
    

def generateNextPlatform(prev):
    (x, y, w, h) = prev

    newWidth = int(random() * 60) + 50
    gap = int(random() * 60) + 100
    heightDiff = int(random() * 80) - 30

    newX = x + w + gap
    newY = y - heightDiff

    # keep the platform in a reasonable vertical range
    newY = max(180, min(360, newY))

    # keep x on screen for now
    if newX > 300:
        newX = 220

    return (newX, newY, newWidth, h)

def onKeyPress(app, key):
    if key == 'left':
        app.jumpDirection = -1
    elif key == 'right':
        app.jumpDirection = 1

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

        # Start charging when squat is deep enough.
        if app.squatDepth > 8 and not app.isJumping:
            app.isCharging = True
            app.maxSquatDepth = max(app.maxSquatDepth, app.squatDepth)

        # If the player was charging and then stands up again,
        # trigger the jump.
        elif app.isCharging and app.squatDepth < 15 and not app.isJumping:
            app.isCharging = False
            app.isJumping = True

            app.playerVY = -max(6, app.maxSquatDepth * 0.6 * app.jumpYScale)

            speed = max(2, app.maxSquatDepth * 0.25 * app.jumpXScale)
            app.playerVX = app.jumpDirection * speed

            app.maxSquatDepth = 0

        if app.isJumping:
            prevBottom = app.playerY + 20

            app.playerX += app.playerVX
            app.playerY += app.playerVY
            app.playerVY += 1   # gravity

            ghostBottom = app.playerY + 20

            # only check landing while falling downward
            if app.playerVY > 0:
                for i in range(len(app.platforms)):
                    x, y, w, h = app.platforms[i]

                    withinX = (x <= app.playerX <= x + w)
                    crossedTop = (prevBottom <= y and ghostBottom >= y)

                    if withinX and crossedTop:
                        print("landed on", i) 
                        app.currentPlatformIndex = i

                        app.playerY = y - 20
                        app.playerVY = 0
                        app.playerVX = 0
                        app.isJumping = False
                        app.isCharging = False
                        app.groundY = y - 25
                        break

                    # if the ghost falls below the screen, game over
                    if app.playerY > app.height + 50:
                        app.gameOver = True
                        app.isJumping = False
                        app.playerVX = 0
                        app.playerVY = 0

                    # # Land back on the current platform for now.
                    # if app.playerY >= app.groundY:
                    #     app.playerY = app.groundY
                    #     app.playerVY = 0
                    #     app.isJumping = False
        # if (not app.isJumping) and app.currentPlatformIndex == 1:
        #                 oldSecond = app.platforms[1]
        #                 newPlatform = generateNextPlatform(oldSecond)

        #                 app.platforms.pop(0)
        #                 app.platforms.append(newPlatform)

        #                 app.currentPlatformIndex = 0     

    # --- TEST CONNECTION ---
    # Move player based on squatDepth
    # app.playerY = int(300 + app.squatDepth)

def redrawAll(app):
    # Background
    drawRect(0, 0, app.width, app.height, fill='lightblue')

    # Platforms
    for (x, y, w, h) in app.platforms:
        drawBox(x, y, w, h)

    # Debug text
    drawLabel(f"squatDepth: {int(app.squatDepth)}", app.width // 2, 50, size=20)
    drawLabel(f"baselineY: {app.baselineY}", app.width // 2, 80, size=16)

    # Ghost player
    drawGhost(app.playerX, app.playerY)

    drawLabel(f"squatDepth: {int(app.squatDepth)}", app.width//2, 50, size=20)
    drawLabel(f"isJumping: {app.isJumping}", app.width//2, 100, size=16)
    drawLabel(f"maxSquat: {int(app.maxSquatDepth)}", app.width//2, 120, size=16)
    drawLabel(f"playerVY: {int(app.playerVY)}", app.width//2, 140, size=16)
    drawLabel(f"isCharging: {app.isCharging}", app.width//2, 160, size=16)
    drawLabel(f"playerVX: {app.playerVX:.1f}", app.width//2, 180, size=16)

    if app.gameOver:
        drawLabel("Game Over", app.width // 2, app.height // 2,
                size=32, fill='red', bold=True)


runApp(width=400, height=600)