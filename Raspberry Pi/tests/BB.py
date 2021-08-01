import RPi.GPIO as GPIO
import time

# pin numbering
GPIO.setmode(GPIO.BCM)

# choose GPIO 17 for the button
button = 17

# choose GPIO 13 for the buzzer
buzzer = 13
GPIO.setup(buzzer,GPIO.OUT)

for ii in range(0,10):
    print(GPIO.input())
    # Flash
    GPIO.output(buzzer,GPIO.HIGH)
    time.sleep(1)
    GPIO.output(buzzer,GPIO.LOW)
    time.sleep(0.2)


GPIO.cleanup()