'''Functions/Classes used to preprocess the data will go here
'''
import numpy as np

def add(a, b):
    '''A dummy function to test if the pytests library is working'''
    return a+b


def format_fft_data(EEG_data):
    '''Should output the x and y fourier transform data.
    input: 
    '''
#==================================================
# INSERT CODE HERE

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


