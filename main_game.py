from random import random
from cmu_graphics import *
import cv2

def drawGhost(cx, cy, vy, isCharging, chargeAmount):
    # 默认比例
    scaleX = 1
    scaleY = 1

    # 蓄力时：压扁一点
    if isCharging:
        t = min(1, chargeAmount / 30)
        scaleX = 1 + 0.25 * t
        scaleY = 1 - 0.25 * t

    # 起跳时：拉长一点
    elif vy < 0:
        scaleX = 0.9
        scaleY = 1.15

    # 下落时：轻微压缩
    elif vy > 0:
        scaleX = 1.08
        scaleY = 0.92

    bodyTopR = 20
    bodyW = 40 * scaleX
    bodyH = 40 * scaleY

    # 头
    drawCircle(cx, cy - 20 * scaleY, bodyTopR * scaleY, fill='white')
    drawCircle(cx - 3, cy - 48 * scaleY, 3, fill='green')
    drawCircle(cx + 3, cy - 48 * scaleY, 3, fill='green')
    drawLine(cx, cy - 40 * scaleY, cx, cy - 48 * scaleY, fill='green', lineWidth=2)

    # 身体
    drawRect(cx - bodyW/2, cy - 20 * scaleY, bodyW, bodyH, fill='white')

    # 底部波浪
    drawCircle(cx - 12 * scaleX, cy + 20 * scaleY, 8 * scaleY, fill='white')
    drawCircle(cx,               cy + 20 * scaleY, 8 * scaleY, fill='white')
    drawCircle(cx + 12 * scaleX, cy + 20 * scaleY, 8 * scaleY, fill='white')

    # 眼睛
    drawCircle(cx - 6 * scaleX, cy - 20 * scaleY, 4, fill='black')
    drawCircle(cx + 6 * scaleX, cy - 20 * scaleY, 4, fill='black')

    # 嘴
    mx = cx + 10 * scaleX
    my = cy + 8 * scaleY
    drawRect(mx - 2, my + 2, 4, 6, fill='beige', border='black', borderWidth=0.5)
    drawCircle(mx, my, 4.5, fill='red', border='black', borderWidth=0.5)
def drawBox(x, y, w, h):
    # top of the box
    drawRect(x, y, w, h, fill='sienna', border='black')

    # front side to make it look thicker
    drawRect(x, y + h, w, 10, fill='peru', border='black')
def drawChargeGlow(cx, cy, chargeAmount):
    glowR = 28 + min(20, chargeAmount)
    drawCircle(cx, cy - 5, glowR, fill='deepskyblue', opacity=15)
    drawCircle(cx, cy - 5, glowR - 8, fill='white', opacity=10)
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
    app.platforms = [first, p2]

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
    app.score = 0

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

    newWidth = int(random() * 40) + 70
    newY = y + int(random() * 80) - 40
    newY = max(180, min(360, newY))

    # 如果旧板在左边，新板放右边
    if x < 200:
        newX = 220
    else:
        newX = 70

    return (newX, newY, newWidth, h)

def onKeyPress(app, key):
    if key == 'left':
        app.jumpDirection = -1
    if key == 'right':
        app.jumpDirection = 1
    elif key == 'r' and app.gameOver:
        onAppStart(app)

def onStep(app):
    ret, frame = app.cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = app.faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

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
            app.playerVY += 1

            ghostBottom = app.playerY + 20

            if app.playerVY > 0:
                targetIndex = 1 - app.currentPlatformIndex
                x, y, w, h = app.platforms[targetIndex]

                withinX = (x <= app.playerX <= x + w)
                crossedTop = (prevBottom <= y and ghostBottom >= y)

                if withinX and crossedTop:
                    print("landed on target", targetIndex)

                    app.currentPlatformIndex = targetIndex

                    app.playerY = y - 25
                    app.playerVY = 0
                    app.playerVX = 0
                    app.isJumping = False
                    app.isCharging = False
                    app.groundY = y - 25

                    oldPlatform = app.platforms[targetIndex]
                    newPlatform = generateNextPlatform(oldPlatform)

                    app.platforms = [oldPlatform, newPlatform]
                    app.currentPlatformIndex = 0
                    app.score += 1
                    

            if app.playerY > app.height + 50:
                app.gameOver = True
                app.isJumping = False
                app.playerVX = 0
                app.playerVY = 0
                       

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

    # Ghost player
    drawGhost(app.playerX, app.playerY, app.playerVY, app.isCharging, app.maxSquatDepth)

    drawLabel(f"squatDepth: {int(app.squatDepth)}", app.width//2, 50, size=20)
    drawLabel(f"isCharging: {app.isCharging}", app.width//2, 160, size=16)
    drawLabel(f"Score: {app.score}", 70, 30, size=20)
    drawLabel(f"Press Left and Right to change direction", app.width//2, 100, size=16)
    if app.isCharging:
        drawChargeGlow(app.playerX, app.playerY, app.maxSquatDepth)
    if app.gameOver:
        drawLabel("Game Over", app.width // 2, app.height // 2, size=32, fill='red', bold=True)
        drawLabel(f"Final Score: {app.score}", app.width//2, app.height//2 + 40, size=18)


runApp(width=400, height=600)