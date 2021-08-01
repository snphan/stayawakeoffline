import RPi.GPIO as GPIO
import time

# pin numbering
GPIO.setmode(GPIO.BCM)

# choose GPIO 17 for the button
button = 17
GPIO.setup(button,GPIO.OUT)

# choose GPIO 13 for the buzzer
buzzer = 13
GPIO.setup(buzzer,GPIO.OUT)
pwm = GPIO.PWM(buzzer, 3500)


for ii in range(0,10):
    print(GPIO.input(button))
    # Flash
    pwm.start(50)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)
    time.sleep(0.2)


GPIO.cleanup()