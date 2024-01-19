import pygame
import os
import random
import mediapipe as mp
import cv2

pygame.init()

# 初始化MediaPipe手部模块
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# 用于绘制手关键点的工具
mp_drawing = mp.solutions.drawing_utils

# 打开摄像头
cap = cv2.VideoCapture(0)

# 常数设置
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
# 设置屏幕大小
#SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# 两个跑步状态循环切换
RUNNING = [pygame.image.load(os.path.join("Resources/Knight", "The_Knight_Idle.png")),
           pygame.image.load(os.path.join("Resources/Knight", "The_Knight_Walking.png"))]
# 跳状态
JUMPING = pygame.image.load(os.path.join("Resources/Knight", "The_Knight_Idle.png"))

# 蹲状态
STAYING = [pygame.image.load(os.path.join("Resources/Knight", "The_Knight_Stagger_Hazard.png")),
           pygame.image.load(os.path.join("Resources/Knight", "The_Knight_Stagger_Hazard.png"))]

# 仙人掌障碍，分为大仙人掌和小仙人掌
SMALL_CACTUS = [pygame.image.load(os.path.join("Resources/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Resources/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Resources/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Resources/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Resources/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Resources/Cactus", "LargeCactus3.png"))]

# 飞鸟障碍，两个状态切换
BIRD = [pygame.image.load(os.path.join("Resources/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Resources/Bird", "Bird2.png"))]

# 云
CLOUD = pygame.image.load(os.path.join("Resources/Other", "Cloud.png"))

# 游戏结束
OVER = pygame.image.load(os.path.join("Resources/Other", "GameOver.png"))

# 背景
BG = pygame.image.load(os.path.join("Resources/Other", "Track.png"))


# 小骑士类
class Knight:
    X_POS = 80
    Y_POS = 260
    Y_POS_DUCK = 290
    JUMP_VEL = 8.5  # 跳跃时的垂直速度

    def __init__(self):
        # 设置初始状态
        self.stay_img = STAYING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_stay = False
        self.dino_run = True
        self.dino_jump = False

        # 设置已经跑到的坐标
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        # dino_rect作为碰撞检测
        self.dino_rect = self.image.get_rect()
        # 设置初始在的地方
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, input):
        if self.dino_stay:
            self.stay()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        # # 如果不在跳状态，那点方向上键切换成跳状态
        # if input[pygame.K_UP] and not self.dino_jump:
        #     self.dino_stay = False
        #     self.dino_run = False
        #     self.dino_jump = True
        # # 如果不在蹲状态，那点方向下键切换为蹲状态
        # elif input[pygame.K_DOWN] and not self.dino_jump:
        #     self.dino_stay = True
        #     self.dino_run = False
        #     self.dino_jump = False
        # # 如果不是在跳和蹲，那就切换成跑状态
        # elif not (self.dino_jump or input[pygame.K_DOWN]):
        #     self.dino_stay = False
        #     self.dino_run = True
        #     self.dino_jump = False
        # 如果不在跳状态，那点方向上键切换成跳状态
        if input==pygame.K_UP and not self.dino_jump:
            self.dino_stay = False
            self.dino_run = False
            self.dino_jump = True
        # 如果不在蹲状态，那点方向下键切换为蹲状态
        elif input==pygame.K_DOWN and not self.dino_jump:
            self.dino_stay = True
            self.dino_run = False
            self.dino_jump = False
        # 如果不是在跳和蹲，那就切换成跑状态
        elif not (self.dino_jump or input==pygame.K_DOWN):
            self.dino_stay = False
            self.dino_run = True
            self.dino_jump = False

    def stay(self):
        # 每5个步长选一张图像，调整帧率
        self.image = self.stay_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < - self.JUMP_VEL:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        # 将恐龙绘制到屏幕上
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Cloud:
    def __init__(self):
        # 随机绘制
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))


# 障碍基类
class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 200
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1

def gesture():
    # 读取每一帧
    ret, frame = cap.read()
    if not ret:
        return

    # 将图像转换为RGB格式
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 进行手部检测
    results = hands.process(rgb_frame)

    key=None

    status=""

    # 如果检测到手部
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 获取手部关键点
            landmarks = hand_landmarks.landmark

            # 获取大拇指、食指和中指的关键点
            thumb_tip = landmarks[4]
            index_finger_tip = landmarks[8]
            middle_finger_tip = landmarks[12]

            # 计算大拇指和食指的距离
            thumb_index_distance = ((thumb_tip.x - index_finger_tip.x) ** 2 + (
                        thumb_tip.y - index_finger_tip.y) ** 2) ** 0.5

            # 计算大拇指和中指的距离
            thumb_middle_distance = ((thumb_tip.x - middle_finger_tip.x) ** 2 + (
                        thumb_tip.y - middle_finger_tip.y) ** 2) ** 0.5

            # 判断食指是否竖直
            thumb_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
            index_finger_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
            middle_finger_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
            ring_finger_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y
            pinky_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y

            # 判断食指是否相对其他手指更远离手腕
            index_finger_up = index_finger_tip_y < min(thumb_tip_y, middle_finger_tip_y, ring_finger_tip_y, pinky_tip_y)


            # 根据距离判断手的状态
            if thumb_index_distance > 0.1 and thumb_middle_distance > 0.1:
                status = "jump"  # 手掌张开，代表跳
                key = pygame.K_UP
            elif thumb_index_distance < 0.1 and thumb_middle_distance < 0.1:
                status = "run"  # 手握拳代表继续跑
                key = None
            elif index_finger_up:
                status = "squat"  # 只伸出一个食指，代表蹲
                key = pygame.K_DOWN

            # 在图像上绘制结果
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    # 显示结果
    cv2.imshow('Hand Tracking', frame)
    return key

def menu(death_count,SCREEN):
    global points
    run = True
    while run:

        input = gesture()

        SCREEN.fill((255, 255, 255))
        font = pygame.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Open your fingers to Start", True, (0, 0, 0))
            caption = font.render("open your fingers(jump) & only hold your index finger(squat)" , True, (0, 0, 0))
            captionRect = caption.get_rect()
            captionRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(caption, captionRect)
        elif death_count > 0:
            SCREEN.blit(OVER, (SCREEN_WIDTH // 2 - 190, 60))

            text = font.render("Open your fingers to Restart", True, (0, 0, 0))
            score = font.render("Your Score: " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(RUNNING[0], (SCREEN_WIDTH // 2 - 20, SCREEN_HEIGHT // 2 - 150))
        pygame.display.update()
        if input ==pygame.QUIT:
            run=False
        if input == pygame.K_UP:
            main(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                main(SCREEN)




def main(SCREEN):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pygame.time.Clock()
    player = Knight()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed
        points += 1
        # 每100分加快一个速度
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(points), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        SCREEN.blit(text, textRect)

    # 绘制背景
    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        # 用两张一样的图片达到无缝切换的效果
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        input = gesture()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # 释放摄像头和关闭窗口
                cap.release()
                cv2.destroyAllWindows()

        SCREEN.fill((255, 255, 255))
        #input = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(input)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 2) == 2:
                obstacles.append(Bird(BIRD))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.dino_rect.colliderect(obstacle.rect):
                death_count += 1
                menu(death_count,SCREEN=SCREEN)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()

        clock.tick(30)
        pygame.display.update()




def run():
    # 常数设置
    SCREEN_HEIGHT = 600
    SCREEN_WIDTH = 1100
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    menu(death_count=0,SCREEN=SCREEN)

if __name__ == '__main__':
    run()