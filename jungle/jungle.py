import cv2
import sys  # 用sys.exit退出程序
import random  # 生成随机数
import pygame  # 导入pygame库，用于游戏开发
import numpy as np  # 导入numpy库，用于进行数学运算
from main import main_menu

from pygame.locals import *  # 从pygame.locals导入所有常量
from utils_mediapipe import MediaPipeHand  # 从utils_mediapipe模块导入MediaPipeHand类，用于手部跟踪

# 游戏的全局变量
FPS = 32  # 设置游戏的帧率
SCREENWIDTH = 289  # 设置游戏屏幕宽度
SCREENHEIGHT = 511  # 设置游戏屏幕高度
#SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))  # 初始化游戏显示窗口
GROUNDY = SCREENHEIGHT * 0.8  # 地面的垂直位置
GAME_SPRITES = {}  # 用于存储游戏中的所有物质
GAME_SOUNDS = {}  # 用于存储游戏中的所有声音
PLAYER = 'gallery/sprites/plane.png'  # 小飞机图片路径
BACKGROUND = 'gallery/sprites/background.png'  # 背景图片路径
PIPE = 'gallery/sprites/pipe.png'  # 管子图片路径

# 手部跟踪的类的初始化
cap = cv2.VideoCapture(0)  # 打开摄像头，'0' 代表一个摄像头
hand = MediaPipeHand(static_image_mode=False, max_num_hands=1)  # 初始化MediaPipeHand对象，配置为动态模式，最多跟踪一个手部

def welcomeScreen(SCREEN):
    # 在控制台打印开始游戏的指示
    print("请按空格键或者向上键开始游戏")
    playerx = int(SCREENWIDTH / 5)
    playery = int((SCREENHEIGHT - GAME_SPRITES['player'].get_height()) / 2)
    messagex = int((SCREENWIDTH - GAME_SPRITES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.13)
    basex = 0

    while True:
        for event in pygame.event.get():
            # 如果用户点击关闭按钮或按下Esc键，关闭游戏
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            # 如果用户按下空格键或向上键，开始游戏
            elif event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                return

        # 将背景、飞机、消息和基地图像绘制到屏幕上
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        SCREEN.blit(GAME_SPRITES['message'], (messagex, messagey))
        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))

        # 更新屏幕显示
        pygame.display.update()
        FPSCLOCK=pygame.time.Clock()
        FPSCLOCK.tick(FPS)

def mainGame(SCREEN):
    # 在控制台打印退出游戏的指示
    print("请按esc或向下键退出游戏")

    score = 0  # 初始化得分
    collisions = 0  # 碰撞次数初始化为0
    playerx = int(SCREENWIDTH / 5)  # 设置小飞机的初始横坐标
    playery = int(SCREENWIDTH / 2)  # 设置小飞机的初始纵坐标
    basex = 0  # 设置地面的横坐标

    # 创建两个管道用于在屏幕上显示
    newPipe1 = getRandomPipe()  # 创建第一个管道
    newPipe2 = getRandomPipe()  # 创建第二个管道

    # 上方管道的列表
    upperPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},
    ]
    # 下方管道的列表
    lowerPipes = [
        {'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},
    ]

    pipeVelX = -4  # 管道的水平移动速度

    # 飞机的运动参数
    playerVelY = -9  # 飞机的垂直速度
    playerMaxVelY = 10  # 飞机的最大下降速度
    playerMinVelY = -8  # 飞机的最大上升速度
    playerAccY = 1  # 飞机下降的加速度

    playerFlapAccv = -8
    playerFlapped = False

    while True:

        # 从摄像头读取图像进行手部跟踪
        ret, img = cap.read()
        # 初始化angle变量
        angle = 0  # 默认值为0，以防ret为False时angle未被赋值
        if ret:# 检查是否读取到
            # 创建第三人称视角效果
            img = cv2.flip(img, 1)
            # 提取手部关键点
            param = hand.forward(img)
            # 显示手部关键点
            img = hand.draw2d(img.copy(), param)
            cv2.imshow('img 2D', img)
            cv2.waitKey(1)
            # 计算平均关节角度
            angle = np.mean(param[0]['angle'])

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()



        crashTest = isCollide(playerx, playery, upperPipes, lowerPipes)
        if crashTest:
            collisions += 1  # 碰撞时增加碰撞次数
            if collisions >= 1:
                GAME_SOUNDS['die'].play()  # 播放 die 音效
                break  # 跳出游戏循环
        if not crashTest:
            # check for score
            playerMidPos = playerx + GAME_SPRITES['player'].get_width() / 2
            for pipe in upperPipes:
                pipeMidPos = pipe['x'] + GAME_SPRITES['pipe'][0].get_width() / 2
                if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                    score += 1
                    print(f"Your score is {score}")
                    GAME_SOUNDS['point'].play()

        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY

        if playerFlapped:
            playerFlapped = False
        playerHeight = GAME_SPRITES['player'].get_height()
        playery = playery + min(playerVelY, GROUNDY - playery - playerHeight)
        # Set playery 0 to 384 pixel, as finger flexion angle 0 to 90 deg
        playery = angle / 90 * 384



        # 管子移到左边
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        # Add a new pipe when the first is about to cross the leftmost part of the screen
        if 0 < upperPipes[0]['x'] < 5:
            newpipe = getRandomPipe()
            upperPipes.append(newpipe[0])
            lowerPipes.append(newpipe[1])

        # 删除屏幕外的管子
        if upperPipes[0]['x'] < -GAME_SPRITES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Lets blit our sprites now
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(GAME_SPRITES['pipe'][0], (upperPipe['x'], upperPipe['y']))
            SCREEN.blit(GAME_SPRITES['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        SCREEN.blit(GAME_SPRITES['base'], (basex, GROUNDY))
        SCREEN.blit(GAME_SPRITES['player'], (playerx, playery))
        myDigits = [int(x) for x in list(str(score))]
        width = 0
        for digit in myDigits:
            width += GAME_SPRITES['numbers'][digit].get_width()
        Xoffset = (SCREENWIDTH - width) / 2

        for digit in myDigits:
            SCREEN.blit(GAME_SPRITES['numbers'][digit], (Xoffset, SCREENHEIGHT * 0.12))
            Xoffset += GAME_SPRITES['numbers'][digit].get_width()
        pygame.display.update()
        FPSCLOCK = pygame.time.Clock()
        FPSCLOCK.tick(FPS)

#  碰撞检测
def isCollide(playerx, playery, upperPipes, lowerPipes):
    if playery > GROUNDY - 25 or playery < 0:
        GAME_SOUNDS['hit'].play()
        return False

    for pipe in upperPipes:
        pipeHeight = GAME_SPRITES['pipe'][0].get_height()
        if (playery < pipeHeight + pipe['y'] and abs(playerx - pipe['x']) < GAME_SPRITES['pipe'][0].get_width()):
            GAME_SOUNDS['hit'].play()
            return True

    for pipe in lowerPipes:
        if (playery + GAME_SPRITES['player'].get_height() > pipe['y']) and abs(playerx - pipe['x']) < \
                GAME_SPRITES['pipe'][0].get_width():
            GAME_SOUNDS['hit'].play()
            return True

    return False

# 随机生成障碍物
def getRandomPipe():
    pipeHeight = GAME_SPRITES['pipe'][0].get_height()
    offset = SCREENHEIGHT / 3
    y2 = offset + random.randrange(0, int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset))
    pipeX = SCREENWIDTH + 10
    y1 = pipeHeight - y2 + offset
    pipe = [
        {'x': pipeX, 'y': -y1},  # upper Pipe
        {'x': pipeX, 'y': y2}  # lower Pipe
    ]
    return pipe

def run():
    SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))  # 初始化游戏显示窗口
    # This will be the main point from where our game will start
    pygame.init()  # Initialize all pygame's modules
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_caption('丛林冒险')
    GAME_SPRITES['numbers'] = (
        pygame.image.load('gallery/sprites/0.png').convert_alpha(),
        pygame.image.load('gallery/sprites/1.png').convert_alpha(),
        pygame.image.load('gallery/sprites/2.png').convert_alpha(),
        pygame.image.load('gallery/sprites/3.png').convert_alpha(),
        pygame.image.load('gallery/sprites/4.png').convert_alpha(),
        pygame.image.load('gallery/sprites/5.png').convert_alpha(),
        pygame.image.load('gallery/sprites/6.png').convert_alpha(),
        pygame.image.load('gallery/sprites/7.png').convert_alpha(),
        pygame.image.load('gallery/sprites/8.png').convert_alpha(),
        pygame.image.load('gallery/sprites/9.png').convert_alpha(),
    )

    GAME_SPRITES['message'] = pygame.image.load('gallery/sprites/message.png').convert_alpha()
    GAME_SPRITES['base'] = pygame.image.load('gallery/sprites/base.png').convert_alpha()
    GAME_SPRITES['pipe'] = (pygame.transform.rotate(pygame.image.load(PIPE).convert_alpha(), 180),
                            pygame.image.load(PIPE).convert_alpha()
                            )

    # 游戏音效
    GAME_SOUNDS['hit'] = pygame.mixer.Sound('gallery/audio/hit.wav')
    GAME_SOUNDS['point'] = pygame.mixer.Sound('gallery/audio/point.wav')
    GAME_SOUNDS['die'] = pygame.mixer.Sound('gallery/audio/die.wav')

    # 初始化背景图片
    GAME_SPRITES['background'] = pygame.image.load(BACKGROUND).convert()
    #  使用函数使得背景图片大小与窗口相适应
    GAME_SPRITES['background'] = pygame.transform.scale(GAME_SPRITES['background'], (SCREENWIDTH, SCREENHEIGHT))
    GAME_SPRITES['player'] = pygame.image.load(PLAYER).convert_alpha()
    # 计算新的尺寸（例如，宽度和高度都是原来的四分之一）
    new_width = GAME_SPRITES['player'].get_width() // 4
    new_height = GAME_SPRITES['player'].get_height() // 4
    # 对小飞机图像进行缩放
    GAME_SPRITES['player'] = pygame.transform.scale(GAME_SPRITES['player'], (new_width, new_height))

    while True:
        welcomeScreen(SCREEN)  # Shows welcome screen to the user until he presses a button
        mainGame(SCREEN)  # This is the main game function

if __name__ == "__main__":
    run()
