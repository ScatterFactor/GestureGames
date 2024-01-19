from PIL import Image, ImageTk
import tkinter as tk
import random
import math
import cv2
import mediapipe as mp
import threading
import time


def calculate_distance(point1, point2):
    return math.sqrt((point2.x - point1.x) ** 2 + (point2.y - point1.y) ** 2)


def judge_rps(landmarks, frame):
    g = ""
    # 计算五个指尖到腕部的距离
    tw_dist = []
    # 计算五个指尖到手指底部的距离
    tb_dist = []
    for i, point in enumerate(landmarks.landmark):
        height, width, _ = frame.shape
        x, y = int(point.x * width), int(point.y * height)
        cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

        if i in [4, 8, 12, 16, 20]:  # 指尖的索引
            wrist_point = landmarks.landmark[0]  # 腕部的索引为0
            fingertip_point = point
            tw_distance = calculate_distance(wrist_point, fingertip_point)
            tb_distance = calculate_distance(landmarks.landmark[i - 3], fingertip_point)
            tw_dist.append(tw_distance)
            tb_dist.append(tb_distance)
    # 食指和中指明显比其他手指远离手腕，判定剪刀
    if tw_dist[1] > 1.5 * tw_dist[0] and tw_dist[2] > 1.5 * tw_dist[0] and tw_dist[1] > 1.5 * tw_dist[3] and \
            tw_dist[2] > 1.5 * tw_dist[3] and tw_dist[1] > 1.5 * tw_dist[4] and tw_dist[2] > 1.5 * tw_dist[4]:
        g = 'Scissors'
    else:
        is_rock = False
        for i in range(4):
            if tw_dist[i] > 1.3 * tb_dist[i]:
                continue
            is_rock = True
        if is_rock:
            g = 'Rock'
        else:
            g = 'Paper'
    return g


class RPS:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Rock Paper Scissors Game")

        self.camera_panel = tk.Label(self.root)
        self.rps_panel = tk.Label(self.root)

        self.selected_image = ''
        self.gestuee = ''
        self.is_gameover = False

        self.camera_panel.grid(row=0, column=0, rowspan=3, padx=10, pady=10)
        self.rps_panel.grid(row=0, column=1, padx=10, pady=10)

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.cap = cv2.VideoCapture(0)

        self.start_button = tk.Button(self.root, text="Start", command=self.start_game)
        self.start_button.grid(row=1, column=1, pady=10)

        self.countdown_var = tk.StringVar()
        self.countdown_label = tk.Label(self.root, textvariable=self.countdown_var)
        self.countdown_label.grid(row=2, column=1, pady=10)

        self.update_images()

        self.root.mainloop()

        self.cap.release()
        cv2.destroyAllWindows()

    def load_random_rps_image(self):
        rps_images = ["rps/Scissors.png", "rps/Rock.png", "rps/Paper.png"]
        self.selected_image = random.choice(rps_images)

        image = Image.open(self.selected_image)
        image = image.resize((200, 200), Image.LANCZOS)

        tk_image = ImageTk.PhotoImage(image)
        return tk_image

    def update_images(self):
        ret, frame = self.cap.read()
        if ret:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.gesture = judge_rps(hand_landmarks, frame)
                    cv2.putText(frame, f"Player Goes for: {self.gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
        else:
            return

        if not self.is_gameover:
            self.rps_image = self.load_random_rps_image()

        self.camera_panel.img = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        self.camera_panel.config(image=self.camera_panel.img)

        self.rps_panel.img = self.rps_image
        self.rps_panel.config(image=self.rps_panel.img)

        self.root.after(10, self.update_images)

    def countdown_timer(self):
        self.is_gameover = False

        for i in range(3, 0, -1):
            time.sleep(1)
            self.countdown_var.set(f"Starting in {i}...")
            self.root.update()

        self.root.update()
        self.is_gameover = True

        winner = 'player'
        print(self.gesture)
        print(self.selected_image)

        if self.gesture == '':
            self.countdown_var.set(f'Please make your choice before the countdown ends!')
        else:
            if self.gesture == 'Rock' and self.selected_image == 'rps/Paper.png':
                winner = 'Computer'
            elif self.gesture == 'Paper' and self.selected_image == 'rps/Scissors.png':
                winner = 'Computer'
            elif self.gesture == 'Scissors' and self.selected_image == 'rps/Rock.png':
                winner = 'Computer'
            if self.gesture == self.selected_image.split('.')[0]:
                self.countdown_var.set(f'Game Over! The game resulted in a draw.')
            else:
                self.countdown_var.set(f'Game Over! The Winner is {winner}')

        self.start_button.config(text="Restart")
        self.start_button.config(state="normal")
        self.gesture = ''

    def start_game(self):
        self.start_button.config(state=tk.DISABLED)
        self.countdown_thread = threading.Thread(target=self.countdown_timer)
        self.countdown_thread.start()


if __name__ == '__main__':
    rps = RPS()