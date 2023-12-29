# —*-coding:utf-8 一*一
"""
作者:LegendLeo
日期:2023年12月10日
"""
from flask import Flask, jsonify, request, make_response
import time
from flask_cors import CORS

from device import MotorControl

app = Flask(__name__, static_url_path="")
CORS(app, resources={r"/position/*": {"origins": "*"}})

angle = 0  # 角度变化量的sin值（为正向左，为负向右）


@app.route("/")
def index():
    return app.send_static_file("index.html")


@app.route('/position', methods=['POST'])
def send_button_position():  # put application's code here
    global angle
    args = request.json
    try:
        angle = round(args["angle"], 2)
        print(f'angle = {angle:.2f}')
        if angle > 0:
            motor_control.set_pwm(-15, 15)
        elif angle < 0:
            motor_control.set_pwm(15, -15)
        else:
            motor_control.set_pwm(0, 0)
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


if __name__ == '__main__':
    motor_control = motor_init()
    # app.run()
    app.run(debug=True, host='0.0.0.0', port=5000)
