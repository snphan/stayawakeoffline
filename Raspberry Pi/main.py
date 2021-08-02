from uvicmuse.MuseWrapper import MuseWrapper as MW
import asyncio
import time
import RPi.GPIO as GPIO
import numpy as np
from museprocessing import preprocessing as prep

lowerBound = 100
upperBound = 200
endFlag = 0

def processData(chOne, chTwo, chThree, chFour, ref, timeSt): #bluetooth params passed????
    #process data from muse, take only the frontal lobe channels 2 and 3
    channelData = [chTwo, chThree]
    baData = []
    for channel in channelData:
        freq, FFT_data = prep.format_fft_data(channel)
        baData.append(prep.calc_beta_alpha_ratio(freq, FFT_data))

    return np.mean(baData)
    #returns data from muse as single or tuples of frequencies

def main():
    GPIO.cleanup()

    #bluetooth connection stuff/lib start--------------->
    loop = asyncio.get_event_loop()
    M_wrapper = MW (loop = loop,
        target_name = None,
        timeout = 10,
        max_buff_len = 500) 
        
    M_wrapper.search_and_connect()
    print("uygutyguyguyguy")
    
    #<------end
    
    
    #GPIO set up start -------------------------->
    GPIO.setmode(GPIO.BCM)
    led = 27
    GPIO.setup(led,GPIO.OUT)
    button = 17
    GPIO.setup(button,GPIO.OUT)
    buzzer = 13
    GPIO.setup(buzzer,GPIO.OUT)
    pwm = GPIO.PWM(buzzer, 3500)
    GPIO.output(led,GPIO.LOW)
    
    #<-------------end
    
    
    while(True):
        if GPIO.input(button) == 1:
            endFlag = 0
            GPIO.output(led,GPIO.HIGH)
            time.sleep(2)
        while endFlag == 0:
            time.sleep(3) 
            EEG_data = M_wrapper.pull_eeg()
            chOne = []
            chTwo = []
            chThree = []
            chFour = []
            ref = []
            timeSt = []
            
            for inner in EEG_data:
                chOne.append(inner[0])
                chTwo.append(inner[1])
                chThree.append(inner[2])
                chFour.append(inner[3])
                ref.append(inner[4])
                timeSt.append(inner[5])
            
            curr = processData(chOne, chTwo, chThree, chFour, ref, timeSt)
            if curr < lowerBound or curr > upperBound:
                pwm.start(50)
                time.sleep(0.5)
                pwm.ChangeDutyCycle(0)
                #make beep sound

            if GPIO.input(button) == 1:
                if endFlag == 0:
                    endFlag = 1
                    GPIO.output(led,GPIO.LOW)
                    time.sleep(2)
                else:
                    endFlag = 0
                    GPIO.output(led,GPIO.HIGH)
                    time.sleep(2)

if __name__ == "__main__":
    main()