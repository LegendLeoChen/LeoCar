# —*-coding:utf-8 一*一
"""
作者:LegendLeo
日期:2023年12月10日
"""
from flask import Flask, jsonify, request, make_response
import os, time
import threading
from flask_cors import CORS
import cv2
import numpy as np
from urllib import request as urlrequest

from device import MotorControl

app = Flask(__name__, static_url_path="")
CORS(app, resources={r"/position/*": {"origins": "*"}})

angle = 0			# sin delta angle
lock = threading.Lock()

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route('/position',methods=['POST'])
def send_button_position():  # put application's code here
    global angle
    args = request.json
    try:
        angle = round(args["angle"], 2)
        print(f'angle = {angle:.2f}')
        time.sleep(0.01)
        return jsonify({"passed": True, "message": "成功发送位置", "data": f'angle={args["angle"]}'})
    except:
        return jsonify({"passed": False, "message": "错误", "data": None})


def motor_init():
    # Define GPIO pins for left and right motors (change these pins according to your setup)
    left_motor_pins = {
        'pwm_channel_1': 12,
        'in1': 17,
        'in2': 27
    }

    right_motor_pins = {
        'pwm_channel_2': 13,
        'in3': 19,
        'in4': 26
    }
    # Create an instance of MotorControl
    return MotorControl(**left_motor_pins, **right_motor_pins, standby=22)

class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0
        self.i_limit = 10

    def calculate_output(self, error):
        self.integral += error
        self.integral = max(min(self.integral, self.i_limit), -self.i_limit)
        derivative = error - self.prev_error
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        # ~ print(f'{self.kp * error},{self.ki * self.integral},{self.kd * derivative}')
        self.prev_error = error
        return output


motor_control = motor_init()
pid_controller = PIDController(kp=0.02, ki=0.005, kd=0.005)


def downloadImg(url):           # 读取网络摄像头视频帧
    with urlrequest.urlopen(url) as f:
        data = f.read()
        img1 = np.frombuffer(data, np.uint8)
        # print("img1 shape ", img1.shape) # (83653,)
        img_cv = cv2.imdecode(img1, cv2.IMREAD_ANYCOLOR)
        return img_cv
    

def face_detect():              # 人脸检测并控制小车转向
    global motor_control, pid_controller
    url = "http://192.168.43.212:8080/?action=snapshot"
    # 加载预训练模型
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
    while True:
        # 读取视频流中的一帧
        frame = downloadImg(url)
        # 将帧转换为灰度图像
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # 检测人脸
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        if len(faces) > 0:
            x, y, w, h = faces[0]
            target = x + w / 2
            offset = target - gray.shape[1] / 2
            pwm_output = pid_controller.calculate_output(offset)
            print(f'face: {offset}, pwm: {pwm_output:.2f}')
            if abs(offset) > 8:
                if offset < 0:
                    motor_control.set_pwm(-abs(pwm_output), abs(pwm_output))
                else:
                    motor_control.set_pwm(abs(pwm_output), -abs(pwm_output))
                time.sleep(0.15)
                motor_control.set_pwm(0, 0)
            else:
                motor_control.set_pwm(0, 0)
        else:
            motor_control.set_pwm(0, 0)

        
thread1 = threading.Thread(name='t1', target=face_detect)       # 人脸检测线程
thread1.daemon = True
thread1.start()

if __name__ == '__main__':
    # app.run()
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
