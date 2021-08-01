import RPi.GPIO as GPIO
import time

# pin numbering
GPIO.setmode(GPIO.BOARD)

# choose pin 11 (GPIO 17) for the LED
led = 11
GPIO.setup(led,GPIO.OUT)

# Flash
GPIO.output(led,GPIO.HIGH)
time.sleep(1)
GPIO.output(led,GPIO.LOW)
