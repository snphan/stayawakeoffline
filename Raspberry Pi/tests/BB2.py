import RPi.GPIO as GPIO
import time

# pin numbering
GPIO.setmode(GPIO.BCM)

# choose GPIO 27 for the led
led = 27
GPIO.setup(led,GPIO.OUT)

# choose GPIO 17 for the button
button = 17
GPIO.setup(button,GPIO.OUT)

# choose GPIO 13 for the buzzer
buzzer = 13
GPIO.setup(buzzer,GPIO.OUT)
pwm = GPIO.PWM(buzzer, 3500)

GPIO.output(led,GPIO.LOW)
flag = GPIO.input(button)
print(type(flag))

for ii in range(0,6):
    flag = GPIO.input(button)
    if flag:
        GPIO.output(led,GPIO.HIGH)
    else:
        GPIO.output(led,GPIO.LOW)   
    # Flash
    pwm.start(50)
    time.sleep(5)
    pwm.ChangeDutyCycle(0)
    time.sleep(0.1)


GPIO.cleanup()