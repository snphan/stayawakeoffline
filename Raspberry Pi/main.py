from uvicmuse.MuseWrapper import MuseWrapper as MW
import asyncio
import time

lowerBound = 100
upperBound = 200
endFlag = False

def processData(eeg_data): #bluetooth params passed????
    #process data from muse
    return 150
    #returns data from muse as single or tuples of frequencies

def main():
    #bluetooth connection stuff/lib start--------------->
    loop = asyncio.get_event_loop()
    M_wrapper = MW (loop = loop,
        target_name = None,
        timeout = 10,
        max_buff_len = 500) 
        
    M_wrapper.search_and_connect()
    
    #<------end
    
    while(True):
        while endFlag == False:

            curr = processData()
            EEG_data = M_wrapper.pull_eeg()
            processData(EEG_data)
            time.sleep(5)
            print("sleeped \n\n\n\n\n")

            if curr < lowerBound or curr > upperBound:
                print("xd")
                #make beep sound

            #update End flag via GPIO/button
            
            #optional - delay timer for inner loop
            
        #optional - delay timer for outer loop


main()