'''Functions for simulating collected data
'''
from tkinter import filedialog
import os
from pathlib import Path
import numpy as np
import pandas as pd
import preprocessing as prep
import matplotlib.pyplot as plt

# https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def gen_ba_ratios(time, eeg):
    '''ba = beta/alpha ratios. Process only one stream

    Params
    ------
    time: List(float)
        the full time array for the data set
    eeg: List(float)
        a single channel from the dataset

    
    '''

    CHUNK_LENGTH = 100
    chunked_time = list(chunks(time, CHUNK_LENGTH)) 
    chunked_eeg = list(chunks(eeg, CHUNK_LENGTH)) 

    chunked_freqs = []
    chunked_amplitudes = []

    # FFT all of the chunks
    for i in range(len(chunked_time)):
        freq, amplitude = prep.format_fft_data(chunked_time[i], chunked_eeg[i])
        chunked_freqs.append(freq)
        chunked_amplitudes.append(amplitude)

    # Find the beta/alpha ratios for all of the chunks
    ba_ratios = [prep.calc_beta_alpha_ratio(chunked_freqs[i], chunked_amplitudes[i]) for i in range(chunked_freqs)]

    # The time of b/a will be taken as the first element of each chunk
    times = [chunked_time[i][0] for i in range(len(chunked_time))]

    return times, ba_ratios



    

    


    







#================================================== 
# HELPER FUNCTIONS

def get_input_path():
    cwd = Path(__file__).resolve().parent
    return filedialog.askopenfilename(initialdir=cwd, title="Select the Input Data") 


if __name__ == "__main__":
    input_path = Path(get_input_path())
    data = pd.read_csv(input_path, index_col=0)

    # Process the second channel only:
    eeg_times, channel_2 = list(data['Time']), list(data['Channel 2'])
    times, ba_ratios = gen_ba_ratios(eeg_times, channel_2)
    plt.plot(times, ba_ratios)
    plt.xlabel('Time (s)')
    plt.ylabel('BA_ratios')
    plt.show()
