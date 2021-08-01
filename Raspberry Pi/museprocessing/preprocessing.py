'''Functions/Classes used to preprocess the data will go here
'''
import numpy as np

def add(a, b):
    '''A dummy function to test if the pytests library is working'''
    return a+b

def filterNoise(li, lowerBound, upperBound):
    for ele in li:
        if ele < lowerBound or ele > upperBound
        li.remove(ele)
    return li

def format_fft_data(EEG_data):
    '''Should output the x and y fourier transform data.
    input:
    '''
#==================================================
# INSERT CODE HERE
# Download from the internet if not already installed



    samples_per_sec = 256

    FFT_data = np.fft.fft(EEG_data)
    freq = np.fft.fftfreq(len(EEG_data))*samples_per_sec

# Drop negative Fourier
    freq = freq[0:int(len(freq)/2)]
    FFT_data = fftdata[0:int(len(FFT_data)/2)]
    FFT_data=np.sqrt(FFT_data.real**2 + FFT_data.imag**2)
    return freq,FFT_data


#==================================================

    pass




















































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

    bands = {'alpha': (13,20), 'beta':(8,12)} # From literature

    alpha_inds = np.where((freq >= bands['alpha'][0]) & (freq >= bands['alpha'][1]))
    beta_inds = np.where((freq >= bands['beta'][0]) & (freq >= bands['beta'][1]))


    alpha_power = np.mean(FFT_data[alpha_inds])
    beta_power = np.mean(FFT_data[beta_inds])

    return beta_power/alpha_power


calc_beta
