import RPi.GPIO as GPIO
import time

# pin numbering
GPIO.setmode(GPIO.BCM)

# choose pin 11 (GPIO 17) for the LED
led = 17
GPIO.setup(led,GPIO.OUT)

# Flash
GPIO.output(led,GPIO.HIGH)
time.sleep(1)
GPIO.output(led,GPIO.LOW)
