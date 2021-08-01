from uvicmuse.MuseWrapper import MuseWrapper as MW
import asyncio
import time

lowerBound = 100
upperBound = 200
endFlag = False

def processData(chOne, chTwo, chThree, chFour, ref, timeSt): #bluetooth params passed????
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
    print("uygutyguyguyguy")
    
    #<------end
    
    while(True):
        while endFlag == False:
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
                print("xd")
                #make beep sound

            #update End flag via GPIO/button
            
            #optional - delay timer for inner loop
            
        #optional - delay timer for outer loop


main()