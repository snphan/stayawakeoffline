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

def ba_static_window(time, eeg):
    '''ba = beta/alpha ratios. Process only one stream using the staic window method.
    

    Params
    ------
    time: List(float)
        the full time array for the data set
    eeg: List(float)
        a single channel from the dataset

    
    '''

    CHUNK_LENGTH = 256
    chunked_time = list(chunks(time, CHUNK_LENGTH)) 
    chunked_eeg = list(chunks(eeg, CHUNK_LENGTH)) 

    chunked_freqs = []
    chunked_magnitudes = []

    # FFT all of the chunks
    for i in range(len(chunked_time)):
        freq, magnitude = prep.format_fft_data(chunked_eeg[i])
        chunked_freqs.append(freq)
        chunked_magnitudes.append(magnitude)

    # Find the beta/alpha ratios for all of the chunks
    ba_ratios = [prep.calc_beta_alpha_ratio(chunked_freqs[i], chunked_magnitudes[i]) for i in range(len(chunked_freqs))]

    # The time of b/a will be taken as the first element of each chunk
    times = [chunked_time[i][0] for i in range(len(chunked_time))]

    return times, ba_ratios


def ba_overlap_window(time, eeg, step, window_len):
    '''ba =beta/alpha ratio. Process the data using the sliding (overlapping) window method

    Params
    ------
    time: List(float)
        the full time array for the data set
    eeg: List(float)
        a single channel from the dataset
    step: int
        how much to advance the window each time
    window_len: int
        the width of the window in number of samples

    Returns
    -------
    times: List(float)
        the start times of each window
    ba_ratios: List(float)
        the ba_ratios at each overlapping window
    '''
    
    chunked_time = []
    chunked_eeg = []
    for i in range(0, len(eeg),step):
        if i+window_len >= len(eeg):
            # Last time through
            chunked_eeg.append(eeg[i:len(eeg)])
            chunked_time.append(time[i:len(eeg)])
            break
        chunked_eeg.append(eeg[i:i+window_len]) 
        chunked_time.append(time[i:i+window_len])

    chunked_freqs = []
    chunked_magnitudes = []
    # FFT all of the chunks
    for i in range(len(chunked_time)):
        freq, magnitude = prep.format_fft_data(chunked_eeg[i])
        chunked_freqs.append(freq)
        chunked_magnitudes.append(magnitude)

    # Find the beta/alpha ratios for all of the chunks
    ba_ratios = [prep.calc_beta_alpha_ratio(chunked_freqs[i], chunked_magnitudes[i]) for i in range(len(chunked_freqs))]

    # The time of b/a will be taken as the first element of each chunk
    times = [chunked_time[i][0] for i in range(len(chunked_time))]

    return times, ba_ratios


    


    







#================================================== 
# HELPER FUNCTIONS

def get_input_path():
    cwd = Path(__file__).resolve().parent
    return filedialog.askopenfilename(initialdir=cwd, title="Select the Input Data") 

#==================================================
if __name__ == "__main__":
    input_path = Path(get_input_path())
    data = pd.read_csv(input_path, index_col=0)

    # Process the second channel only:
    eeg_times, channel_2 = list(data['Time']), list(data['Channel 2'])

    times, ba_ratios = ba_overlap_window(eeg_times, channel_2, 50, 200)
    plt.plot(times, ba_ratios)
    plt.xlabel('Time (s)')
    plt.ylabel('BA_ratios')
    plt.title(input_path.name)
    plt.show()
