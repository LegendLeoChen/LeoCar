import RPi.GPIO as GPIO
import time

class MotorControl:
    def __init__(self, pwm_channel_1, pwm_channel_2, in1, in2, in3, in4, standby=22):
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup pins
        self.in1 = in1
        self.in2 = in2
        self.in3 = in3
        self.in4 = in4
        self.standby = standby

        GPIO.setup(self.in1, GPIO.OUT)
        GPIO.setup(self.in2, GPIO.OUT)
        GPIO.setup(self.in3, GPIO.OUT)
        GPIO.setup(self.in4, GPIO.OUT)
        GPIO.setup(self.standby, GPIO.OUT)

        # Initialize PWM
        GPIO.setup(pwm_channel_1, GPIO.OUT)
        GPIO.setup(pwm_channel_2, GPIO.OUT)

        self.pwm_channel_1 = GPIO.PWM(pwm_channel_1, 5000)
        self.pwm_channel_2 = GPIO.PWM(pwm_channel_2, 5000)

        self.pwm_channel_1.start(0)
        self.pwm_channel_2.start(0)
        
        # WORK
        GPIO.output(self.standby, GPIO.HIGH)

    def set_pwm(self, moto1, moto2, amplitude=100):
                
        # Motor 1
        GPIO.output(self.in1, GPIO.HIGH if moto1 > 0 else GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW if moto1 > 0 else GPIO.HIGH)

        # Motor 2
        GPIO.output(self.in3, GPIO.LOW if moto2 > 0 else GPIO.HIGH)
        GPIO.output(self.in4, GPIO.HIGH if moto2 > 0 else GPIO.LOW)

        # Limit PWM values
        moto1 = max(-amplitude, min(amplitude, moto1))
        moto2 = max(-amplitude, min(amplitude, moto2))

        # Set PWM values
        self.pwm_channel_1.ChangeDutyCycle(abs(moto1))
        self.pwm_channel_2.ChangeDutyCycle(abs(moto2))

    def stop_motors(self):
        self.pwm_channel_1.ChangeDutyCycle(0)
        self.pwm_channel_2.ChangeDutyCycle(0)

    def cleanup(self):
        GPIO.cleanup()


if __name__ == "__main__":
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
    motor_control = MotorControl(**left_motor_pins, **right_motor_pins, standby=22)

    # Run the robot in different directions
    try:
        while True:
            motor_control.set_pwm(50, 50)  # Forward
            time.sleep(2)
            motor_control.stop_motors()
            time.sleep(1)
            motor_control.set_pwm(-50, -50)  # Backward
            time.sleep(2)
            motor_control.stop_motors()
            time.sleep(1)
            motor_control.set_pwm(30, 50)  # Left
            time.sleep(2)
            motor_control.stop_motors()
            time.sleep(1)
            motor_control.set_pwm(50, 30)  # Right
            time.sleep(2)
            motor_control.stop_motors()
            time.sleep(1)
            motor_control.set_pwm(0, 0)  # Stop
            time.sleep(1)
            motor_control.set_pwm(25, -25)  # Pivot Turn
            time.sleep(2)
            motor_control.stop_motors()
            time.sleep(1)

    except KeyboardInterrupt:
        motor_control.cleanup()
