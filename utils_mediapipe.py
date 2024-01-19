import cv2
import numpy as np
import mediapipe as mp


class MediaPipeHand:
    def __init__(self, static_image_mode=True, max_num_hands=1):
        super(MediaPipeHand, self).__init__()
        self.max_num_hands = max_num_hands

        # 访问 MediaPipe Solutions Python API
        mp_hands = mp.solutions.hands
        # help(mp_hands.Hands)

        # MediaPipe Hands初始化
        # static_image_mode:
        #   对于视频处理设置为 False: 将使用前一帧来定位手部以降低延迟
        #   对于不相关的图像设置为 True: 允许在每个输入图像上运行手部检测
        
        # max_num_hands:
        #   检测的最大手部数量
        
        # min_detection_confidence:
        #   手部检测模型的置信值[0,1]，用于确定检测是否成功
        
        # min_tracking_confidence:
        # 用于确定手部地标是否成功跟踪的最小置信值[0,1]
        # 如果静态图像模式为true，则忽略此参数

        self.pipe = mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

        # 定义手部参数
        self.param = []
        for i in range(max_num_hands):
            p = {
                'keypt': np.zeros((21, 2)),  # 2D关键点在图像坐标中（像素）
                'joint': np.zeros((21, 3)),  # 3D关节在相对坐标中
                'joint_3d': np.zeros((21, 3)),  # 3D关节在绝对坐标中（米）
                'class': None,  # 左手/右手
                'score': 0,  # 预测的手型概率（总是>0.5，相反的手型为1-score）
                'angle': np.zeros(15),  # 关节角度
                'gesture': None,  # 手势类型
                'fps': -1,  # 每秒帧数
            }
            self.param.append(p)

        # 定义将关键点链接在一起形成骨架的运动树
        self.ktree = [0,          # 手腕
                      0,1,2,3,    # 拇指
                      0,5,6,7,    # 食指
                      0,9,10,11,  # 中指
                      0,13,14,15, # 无名指
                      0,17,18,19] # 小拇指

        # 为21个关键点定义颜色
        # 这里定义了一个颜色数组，用于在图像中绘制不同的关键点和骨骼
        self.color = [[0,0,0], # Wrist black
                      [255,0,0],[255,60,0],[255,120,0],[255,180,0], # Thumb
                      [0,255,0],[60,255,0],[120,255,0],[180,255,0], # Index
                      [0,255,0],[0,255,60],[0,255,120],[0,255,180], # Middle
                      [0,0,255],[0,60,255],[0,120,255],[0,180,255], # Ring
                      [0,0,255],[60,0,255],[120,0,255],[180,0,255]] # Little
        self.color = np.asarray(self.color)
        self.color_ = self.color / 255 # For Open3D RGB
        self.color[:,[0,2]] = self.color[:,[2,0]] # For OpenCV BGR
        self.color = self.color.tolist()            


    def result_to_param(self, result, img):
        # 将mediapipe手部结果转换为自定义参数
        img_height, img_width, _ = img.shape

        # 重置参数
        for p in self.param:
            p['class'] = None

        if result.multi_hand_landmarks is not None:
            # L遍历不同的手
            for i, res in enumerate(result.multi_handedness):
                if i>self.max_num_hands-1: break # Note: Need to check if exceed max number of hand
                self.param[i]['class'] = res.classification[0].label
                self.param[i]['score'] = res.classification[0].score

            # Loop through different hands
            for i, res in enumerate(result.multi_hand_landmarks):
                if i>self.max_num_hands-1: break # Note: Need to check if exceed max number of hand
                # Loop through 21 landmark for each hand
                for j, lm in enumerate(res.landmark):
                    self.param[i]['keypt'][j,0] = lm.x * img_width # Convert normalized coor to pixel [0,1] -> [0,width]
                    self.param[i]['keypt'][j,1] = lm.y * img_height # Convert normalized coor to pixel [0,1] -> [0,height]

                    self.param[i]['joint'][j,0] = lm.x
                    self.param[i]['joint'][j,1] = lm.y
                    self.param[i]['joint'][j,2] = lm.z


                # Convert relative 3D joint to angle
                self.param[i]['angle'] = self.convert_3d_joint_to_angle(self.param[i]['joint'])

        return self.param


    def convert_3d_joint_to_angle(self, joint):
        # Get direction vector of bone from parent to child
        v1 = joint[[0,1,2,3,0,5,6,7,0,9,10,11,0,13,14,15,0,17,18,19],:] # Parent joint
        v2 = joint[[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],:] # Child joint
        v = v2 - v1 # [20,3]
        # Normalize v
        v = v/np.linalg.norm(v, axis=1)[:, np.newaxis]

        # Get angle using arcos of dot product
        angle = np.arccos(np.einsum('nt,nt->n',
            v[[0,1,2,4,5,6,8,9,10,12,13,14,16,17,18],:], 
            v[[1,2,3,5,6,7,9,10,11,13,14,15,17,18,19],:])) # [15,]

        return np.degrees(angle) # Convert radian to degree


    def draw2d(self, img, param):
        img_height, img_width, _ = img.shape

        # Loop through different hands
        for p in param:
            if p['class'] is not None:
                # # Label left or right hand
                # x = int(p['keypt'][0,0]) - 30
                # y = int(p['keypt'][0,1]) + 40
                # # cv2.putText(img, '%s %.3f' % (p['class'], p['score']), (x, y), 
                # cv2.putText(img, '%s' % (p['class']), (x, y), 
                #     cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # Red
                
                # Label average angle
                x = int(p['keypt'][0,0]) - 30
                y = int(p['keypt'][0,1]) + 40
                # cv2.putText(img, '%s %.3f' % (p['class'], p['score']), (x, y), 
                cv2.putText(img, 'Ave angle %d deg' % (np.mean(p['angle'])), (x, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2) # Red
                
                # Loop through keypoint for each hand
                for i in range(21):
                    x = int(p['keypt'][i,0])
                    y = int(p['keypt'][i,1])
                    if x>0 and y>0 and x<img_width and y<img_height:
                        # Draw skeleton
                        start = p['keypt'][self.ktree[i],:]
                        x_ = int(start[0])
                        y_ = int(start[1])
                        if x_>0 and y_>0 and x_<img_width and y_<img_height:
                            cv2.line(img, (x_, y_), (x, y), self.color[i], 2) 

                        # Draw keypoint
                        cv2.circle(img, (x, y), 5, self.color[i], -1)
                        # cv2.circle(img, (x, y), 3, self.color[i], -1)

                        # # Number keypoint
                        # cv2.putText(img, '%d' % (i), (x, y), 
                        #     cv2.FONT_HERSHEY_SIMPLEX, 1, self.color[i])

                        # # Label visibility and presence
                        # cv2.putText(img, '%.1f, %.1f' % (p['visible'][i], p['presence'][i]),
                        #     (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1, self.color[i])
                
                # Label gesture
                if p['gesture'] is not None:
                    size = cv2.getTextSize(p['gesture'].upper(), 
                        # cv2.FONT_HERSHEY_SIMPLEX, 2, 2)[0]
                        cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                    x = int((img_width-size[0]) / 2)
                    cv2.putText(img, p['gesture'].upper(),
                        # (x, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,255), 2)
                        (x, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

                    # Label joint angle
                    self.draw_joint_angle(img, p)

            # Label fps
            if p['fps']>0:
                cv2.putText(img, 'FPS: %.1f' % (p['fps']),
                    (0, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)   

        return img


    def forward(self, img):
        # Preprocess image
        # img = cv2.flip(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), 1)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Extract hand result
        result = self.pipe.process(img)

        # Convert hand result to my own param
        param = self.result_to_param(result, img)

        return param

