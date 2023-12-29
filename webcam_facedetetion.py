# —*-coding:utf-8 一*一
"""
作者:LegendLeo
日期:2023年12月09日
"""
import cv2
import numpy as np
from urllib import request

url = "http://192.168.43.212:8080/?action=snapshot"
# 加载预训练模型
face_cascade = cv2.CascadeClassifier('D:\OpenCV\opencv\opencv-4.5.0\sources\data\haarcascades\haarcascade_frontalface_default.xml')

def downloadImg():
    global url
    with request.urlopen(url) as f:
        data = f.read()
        img1 = np.frombuffer(data, np.uint8)
        # print("img1 shape ", img1.shape) # (83653,)
        img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
        return img_cv

while True:
    # 读取视频流中的一帧
    frame = downloadImg()

    # 将帧转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    print(gray.shape[1])
    # 检测人脸
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    # 在图像中标记检测到的人脸
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f'face', (x, y), cv2.LINE_AA, 1, (255, 255, 255))

    # 显示结果
    cv2.imshow('Face Detection', frame)

    # 按下'q'键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放摄像头并关闭窗口
frame.release()
cv2.destroyAllWindows()
