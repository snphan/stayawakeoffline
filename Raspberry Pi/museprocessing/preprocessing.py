'''Functions/Classes used to preprocess the data will go here
'''
import numpy as np
import matplotlib.pyplot as plt
from tkinter import filedialog
from pathlib import Path
import pandas as pd
import time 
from matplotlib.animation import FuncAnimation
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from uvicmuse.MuseWrapper import MuseWrapper
import asyncio




def add(a, b):
    '''A dummy function to test if the pytests library is working'''
    return a+b

def filterNoise(li, lowerBound, upperBound):
    for ele in li:
        if ele < lowerBound or ele > upperBound:
            li.remove(ele)
    return li

def format_fft_data(EEG_data):
    '''Should output the x and y fourier transform data.
    input:
    '''
    samples_per_sec = 256

    FFT_data = np.fft.fft(EEG_data)
    freq = np.fft.fftfreq(len(EEG_data))*samples_per_sec

    # Drop negative Fourier
    freq = freq[0:int(len(freq)/2)]
    FFT_data = FFT_data[0:int(len(FFT_data)/2)]
    FFT_data=np.sqrt(FFT_data.real**2 + FFT_data.imag**2)
    return freq,FFT_data


def plot_fft(freq, FFT_data, title):

    plt.clf()
    plt.plot(freq, FFT_data)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('|F|')
    plt.title(f'FFT of {title}')
    plt.draw()
    plt.pause(0.001)

def calc_beta_alpha_ratio(freq, FFT_data):
    '''Calculate the beta/alpha ratio using the averages of the alpha beta bands.
    The averages represent the "power" of each of these peaks

    Params
    ------
    freq: List(float)
        Frequencies from the FFT
    FFT_data: List(Float)
        The amplitudes from the FFT

    Returns
    -------
    beta_power/alpha_power: float
    '''

    bands = {'beta': (13,30), 'alpha':(8,12)} # From literature

    alpha_inds = np.where((freq >= bands['alpha'][0]) & (freq <= bands['alpha'][1]))
    beta_inds = np.where((freq >= bands['beta'][0]) & (freq <= bands['beta'][1]))


    alpha_power = np.mean(FFT_data[alpha_inds])
    beta_power = np.mean(FFT_data[beta_inds])

    return beta_power/alpha_power


#================================================== 
# HELPER FUNCTIONS

def get_data():
    cwd = Path(__file__).resolve().parent
    input_path = Path(filedialog.askopenfilename(initialdir=cwd, title="Select the Input Data"))
    data = pd.read_csv(input_path, index_col=0)
    data.index.name = input_path.name
    return data

#==================================================

if __name__ == '__main__':

    loop = asyncio.get_event_loop()
    M_wrapper = MuseWrapper(loop=loop, target_name=None, timeout=10, max_buff_len=5000)
    M_wrapper.search_and_connect()
    
    fig = plt.figure()
    fig.suptitle('Live Data')
    ax = plt.axes(xlim=(0, 100), ylim=(-2, 1000))
    ax.xaxis.set_major_locator(MultipleLocator(10))
    ax.xaxis.set_major_formatter('{x:.0f}')
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.set(ylabel="|F|", xlabel="Freq (Hz)")
    ax.axvline(12, color='red')
    ax.axvline(30, color='red')
    ax.axvline(8, color='red')
    ax.text(8, 800, 'Alpha', rotation=90, color='red')
    ax.text(22, 800, 'Beta', rotation=90, color='red')
    line, = ax.plot([],[], lw=2)


    def init():
        line.set_data([],[])
        return line, 

    start_time = time.time()
    buffer = [1]*(5*256)
    def animate_fft(i):
        global buffer
        ANALYSIS_CHANNEL = 2
        EEG_data = M_wrapper.pull_eeg()
        EEG_data = np.transpose(EEG_data)


        channel_data = EEG_data[ANALYSIS_CHANNEL-1]

        buffer = np.roll(buffer, -len(channel_data))
        buffer[-len(channel_data):] = channel_data

        freq, FFT_data = format_fft_data(buffer)
        x = freq
        y = FFT_data
        print(' '*100, end='\r', flush=True)
        print(calc_beta_alpha_ratio(freq, FFT_data), end='\r', flush=True)
        line.set_data(x,y)
        ax.set_title(f'@{time.time() - start_time}s')
        return line,

    anim = FuncAnimation(fig, animate_fft, init_func=init, frames=1000, interval=200, blit=False, repeat=True)

    plt.show()
        
