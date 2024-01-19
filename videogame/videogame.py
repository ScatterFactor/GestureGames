import math
import time
import cv2
import mediapipe as mp
import pygame
import cvzone
from cvzone.HandTrackingModule import HandDetector

scoress = 1

def run():
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    resize_w = 1280
    resize_h = 720
    fpsTime = time.time()

    imgDesk = cv2.imread('videogame/bg.png')
    imgstart = cv2.imread('videogame/start.png')
    imgfin = cv2.imread('videogame/finish.png')

    cap = cv2.VideoCapture(0)
    cap.set(3, resize_w)
    cap.set(4, resize_h)

    t0 = 1.48
    tt1 = 0.39

    # 谱面>
    # 时轴
    t = []
    for i in range(18):
        t.append(t0 + i * tt1)

    for i in range(9):
        t.append(8.5 + i * 1.17)

    for i in range(2):
        t.append(20.2 + i * 1.17)
        t.append(20.2 + i * 1.17)
    t.append(21.76)
    t.append(22.15)
    for i in range(2):
        t.append(22.54)
    for i in range(2):
        t.append(23.71)

    t.append(24.85)
    t.append(25.42)
    t.append(25.61)
    t.append(25.99)
    t.append(25.99 + 0.38)
    t.append(25.99 + 0.76)
    t.append(27.13)
    t.append(27.13 + 0.76)
    for i in range(2):
        t.append(28.27)

    for i in range(2):
        t.append(29.41 + i * 1.16)
        t.append(29.41 + i * 1.16)
    t.append(30.57 + tt1)
    t.append(30.57 + 2 * tt1)
    for i in range(2):
        t.append(31.73)
    for i in range(2):
        t.append(32.89)

    t.append(34.03)
    t.append(34.61)
    t.append(34.80)
    t.append(35.17)
    t.append(35.17 + 0.38)
    t.append(35.17 + 0.76)
    t.append(36.34)
    t.append(36.34 + 0.78)
    for i in range(2):
        t.append(37.51)

    for i in range(6):
        t.append(38.68 + i * 0.165)
    for i in range(6):
        t.append(39.85 + i * 0.165)
    for i in range(6):
        t.append(40.99 + i * 0.165)
    for i in range(6):
        t.append(42.16 + i * 0.165)

    for i in range(2):
        t.append(43.33)
    for i in range(2):
        t.append(44.47)
    t.append(45.64)
    for i in range(3):
        t.append(46.22 + 0.195 * i)
    t.append(46.8)

    for i in range(6):
        t.append(47.94 + i * 0.165)
    t.append(49.08)
    for i in range(6):
        t.append(50.25 + i * 0.165)
    t.append(51.40)

    for i in range(5):
        t.append(52.57 + i * 0.195)
    for i in range(3):
        t.append(53.71 + 0.39 * i)
    t.append(54.89)
    for i in range(2):
        t.append(56.81 + i * 0.195)
    for i in range(2):
        t.append(57.24)

    # 定位
    # 1280:160 320 480 640 800 960 1120
    # 720: 120 240 360 480 600
    key = [(320, 120), (160, 380), (480, 380), (900, 340), (740, 600), (1060, 600),
           (180, 240), (300, 240), (420, 240), (640, 480), (760, 480), (880, 480),
           (600, 120), (450, 300), (300, 480), (1060, 240), (900, 420), (740, 600),

           (640, 360),
           (187, 120), (314, 240), (441, 360), (568, 480), (695, 600), (822, 480), (949, 360), (1076, 360),

           (400, 200), (880, 200), (400, 500), (880, 500), (640, 200), (640, 500), (400, 200), (880, 200), (400, 500),
           (880, 500),

           (160, 600), (320, 520), (480, 440), (640, 360), (800, 280), (960, 200), (1120, 120), (640, 500), (400, 200),
           (880, 200),

           (320, 600), (960, 120), (400, 500), (880, 500), (640, 200), (640, 500), (400, 200), (880, 200), (400, 500),
           (880, 500),

           (160, 580), (320, 470), (480, 360), (640, 250), (800, 140), (960, 250), (1120, 360), (640, 500), (400, 200),
           (880, 200),

           (190, 360), (340, 280), (490, 200), (640, 120), (790, 200), (940, 280),
           (1090, 360), (940, 440), (790, 520), (640, 600), (490, 520), (340, 440),
           (190, 360), (340, 280), (490, 200), (640, 120), (790, 200), (940, 280),
           (1090, 360), (940, 440), (790, 520), (640, 600), (490, 520), (340, 440),

           (400, 200), (880, 250), (400, 500), (880, 450), (200, 240), (620, 360), (780, 420), (940, 360), (1100, 240),

           (190, 600), (340, 500), (490, 400), (640, 300), (790, 200), (940, 100),
           (800, 480),
           (340, 600), (490, 500), (640, 400), (790, 300), (940, 200), (1090, 100),
           (480, 240),

           (320, 360), (480, 440), (640, 360), (800, 280), (960, 200), (960, 480), (640, 360), (320, 240),
           (640, 240),
           (640, 240), (640, 480), (500, 360), (780, 360)]

    # <谱面

    s = []
    for i in range(128):
        s.append(1)

    pointnum = 127
    scoress = 0
    start = 0
    starttime = 0
    end = 0

    pygame.mixer.init()
    pygame.mixer.music.load("videogame/踊子プリムロゼのテーマ.mp3")
    with mp_hands.Hands(
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3) as hands:
        while cap.isOpened():
            success, image = cap.read()

            def hit(i):
                if t[i] < time.time() - starttime < t[i] + 1:
                    if dis(key[i]) < absdis:
                        image = combo(key[i])
                        s[i] = 0
                        global scoress
                        scoress += 1
                elif time.time() - starttime > t[i] + 1:
                    s[i] = 0

            def play(i):
                if t[i] - 1 < time.time() - starttime < t[i]:
                    image = addpre(key[i])
                elif t[i] < time.time() - starttime < t[i] + 1:
                    image = addpoi(key[i])

            image = cv2.resize(image, (resize_w, resize_h))
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image.flags.writeable = False
            image = cv2.flip(image, 1)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = hands.process(image)

            # Draw the hand annotations on the image.
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            image = cv2.addWeighted(image, 0.2, imgDesk, 0.8, 0)

            addpre = lambda point: cv2.circle(image, point, 50, (64, 66, 68), 15, 2)
            addpoi = lambda point: cv2.circle(image, point, 56, (255, 245, 152), -1)
            combo = lambda point: cv2.circle(image, point, 56, (0, 255, 255), -1)

            for i in range(pointnum):
                if s[i]:
                    play(i)

            # 判断是否有手掌
            if results.multi_hand_landmarks:
                # 遍历每个手掌
                for hand_landmarks in results.multi_hand_landmarks:
                    # mp_drawing.draw_landmarks(
                    #     image,
                    #     hand_landmarks,
                    #     mp_hands.HAND_CONNECTIONS,
                    #     mp_drawing_styles.get_default_hand_landmarks_style(),
                    #     mp_drawing_styles.get_default_hand_connections_style()
                    # )
                    landmark_list = []
                    for landmark_id, finger_axis in enumerate(hand_landmarks.landmark):
                        landmark_list.append([
                            landmark_id, finger_axis.x, finger_axis.y,
                            finger_axis.z
                        ])
                    if landmark_list:
                        # 比例缩放到像素
                        ratio_x_to_pixel = lambda x: math.ceil(x * resize_w)
                        ratio_y_to_pixel = lambda y: math.ceil(y * resize_h)

                        index_finger_tip = landmark_list[8]
                        index_finger_tip_x = ratio_x_to_pixel(index_finger_tip[1])
                        index_finger_tip_y = ratio_y_to_pixel(index_finger_tip[2])
                        # 画
                        index_finger_point = (index_finger_tip_x, index_finger_tip_y)
                        circle_func = lambda point: cv2.circle(image, point, 10, (232, 232, 232), -1)
                        image = circle_func(index_finger_point)

                        dis = lambda loc: (index_finger_tip_x - loc[0]) ** 2 + (index_finger_tip_y - loc[1]) ** 2
                        absdis = 60 ** 2

                        if not start:
                            if (index_finger_tip_x - 640) ** 2 + (index_finger_tip_y - 360) ** 2 > 72 ** 2:
                                image = cv2.addWeighted(image, 0.6, imgstart, 0.4, 0)
                            else:
                                start = 1
                                starttime = time.time()
                                pygame.mixer.music.play()
                        else:
                            # key
                            for i in range(pointnum):
                                if s[i]:
                                    hit(i)

            if 70 < time.time() - starttime < 71:
                pygame.mixer.music.stop()
                end = 1
                if scoress == pointnum:
                    cv2.putText(image, "FULL COMBO", (600, 380),
                                cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 255), 2)
            if end:
                image = cv2.addWeighted(image, 0.5, imgfin, 0.5, 0)
                cv2.putText(image, str(int(scoress)) + "/127", (600, 480),
                            cv2.FONT_HERSHEY_PLAIN, 5, (0, 255, 255), 2)

            cTime = time.time()
            fps_text = 1 / (cTime - fpsTime)
            fpsTime = cTime
            songtime = 0.0000
            if time.time() - starttime < 70:
                songtime = time.time() - starttime
            cv2.putText(image, "Time: " + str(int(songtime)), (1080, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (23, 210, 252), 2)
            cv2.putText(image, "FPS: " + str(int(fps_text)), (10, 20),
                        cv2.FONT_HERSHEY_PLAIN, 1, (23, 210, 252), 2)
            # cv2.putText(image, str(int(scoress)), (635, 30),
            #             cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 255), 2)
            cv2.imshow('game', image)
            if cv2.waitKey(5) & 0xFF == 27:
                break
    cap.release()
