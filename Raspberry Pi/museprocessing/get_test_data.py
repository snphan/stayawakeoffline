# Uvic muse imports (so that we can override some of the classes' data formatting)
from uvicmuse.MuseWrapper import MuseWrapper
from uvicmuse.constants import *
from uvicmuse.muse import *
from uvicmuse.helper import *
import pygatt
import asyncio
from functools import partial
from pylsl import StreamInfo, StreamOutlet
from multiprocessing import Process

# User imported libraries
import winsound
import asyncio
import time
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import signal
import sys
import pandas as pd

from datetime import datetime

from pathlib import Path
import os

# Museprocessing
import preprocessing as prep



# ==================================================
""" 
TODO:
- Need to match the user defined sample rate to the sample rate of the device.
- Make a class that allows the user to toggle data collection modes (EEG, Accel, Gyro or all)
- Change the data order in the method override
"""
# ==================================================

# MARK: Classes
class MuseData(MuseWrapper):
    '''A class for visualizing and collecting live data from the Muse 2 headset
    
    Note
    ----

    Parameters
    ----------

    Attributes
    ----------
    '''
    REFRESH_RATE = 50
    EEG_DATA_COLUMNS = [
        "Time",
        "Channel 1",
        "Channel 2",
        "Channel 3",
        "Channel 4",
        "Channel 5",
    ]
    ACCEL_DATA_COLUMNS = [ "Time","Accel X", "Accel Y", "Accel Z",]
    GYRO_DATA_COLUMNS = [ "Time", "Gyro X", "Gyro Y", "Gyro Z",]

    def __init__(self, loop, target_name=None, timeout=10, max_buff_len=2 * 256, sample_time=10):
        super().__init__(loop, target_name, timeout, max_buff_len)
        self.sample_time = sample_time
        self.all_eeg_data = {k: [] for k in self.EEG_DATA_COLUMNS} 
        self.all_accel_data = {k: [] for k in self.ACCEL_DATA_COLUMNS}
        self.all_gyro_data = {k: [] for k in self.GYRO_DATA_COLUMNS}

        # To correct timestamps
        self.inital_eeg_timestamp = 0.0
        self.inital_accel_timestamp = 0.0
        self.inital_gyro_timestamp = 0.0


        # Plotting attributes
        self.eeg_ani, self.eeg_fig, self.eeg_axs, self.eeg_lines = None, None, None, []
        self.accel_ani, self.accel_fig, self.accel_axs, self.accel_lines = None, None, None, []
        self.gyro_ani, self.gyro_fig, self.gyro_axs, self.gyro_lines = None, None, None, []

        self.run_eeg_ani = False
        self.run_accel_ani = False
        self.run_gyro_ani = False

        # Labeling data
        self.labels = {'Time': [], 'Label': []}


    def save_all_data(self):
        '''Save and output as .csv
        '''
        DATA_TYPES = ["EEG", "Accel", "Gyro"]

        all_eeg_data_df = pd.DataFrame.from_dict(self.all_eeg_data)
        all_accel_data_df = pd.DataFrame.from_dict(self.all_accel_data)
        all_gyro_data_df = pd.DataFrame.from_dict(self.all_gyro_data)

        current_dir = Path(__file__).resolve().parent  # Current working directory
        if not current_dir.joinpath("Output Data").exists():
            os.mkdir(current_dir.joinpath("Output Data"))

        current_dir = current_dir.joinpath("Output Data")

        # Backup data
        if not current_dir.joinpath("Backups").exists():
            os.mkdir(current_dir.joinpath("Backups"))
        
        for ind, df in enumerate(
            [all_eeg_data_df, all_accel_data_df, all_gyro_data_df]
        ):
            df.to_csv(
                current_dir.joinpath("Backups").joinpath(
                    f"backup-{DATA_TYPES[ind]}.csv",
                ),
                index=True
            )

        # Format data title
        SUBJECT_INITIALS = input("\n\nEnter your initials: ").upper()
        TASK = input("Enter the task (RAISEARM): ").upper()

        current_datetime = datetime.now().strftime("%Y-%m-%d %H.%M.%S")

        if not current_dir.joinpath(f"{current_datetime}-{TASK}").exists():
            os.mkdir(current_dir.joinpath(f"{current_datetime}-{TASK}"))

        current_dir = current_dir.joinpath(f"{current_datetime}-{TASK}")

        for ind, df in enumerate(
            [all_eeg_data_df, all_accel_data_df, all_gyro_data_df]
        ):
            df.to_csv(
                current_dir.joinpath(
                    f"{TASK}-{SUBJECT_INITIALS}-{DATA_TYPES[ind]}-{self.sample_time}s.csv"
                ),
                index=True,
            )
            print("Saved to {}".format(current_dir.joinpath(
                    f"{TASK}-{SUBJECT_INITIALS}-{DATA_TYPES[ind]}-{self.sample_time}s.csv"
                )))

    def initialize_eegfft_ani(self):
        '''Setup the eeg signal animation
        '''
        PLOT_WINDOW_YLIM = 400
        PLOT_WINDOW_XLIM = 200
        self.eeg_fig, self.eeg_axs = plt.subplots(
            len(self.EEG_DATA_COLUMNS) - 1
        )
        self.eeg_fig.suptitle("Muse 2 EEG Data")
        self.eeg_fig.tight_layout()
        for ind, ax in enumerate(self.eeg_axs):
            ax.set_title(self.EEG_DATA_COLUMNS[ind+1]) # Skip the timeestamp column
            ax.set(ylabel="|F|")
            ax.set_ylim([-PLOT_WINDOW_YLIM, PLOT_WINDOW_YLIM])
            ax.axvline(12, color='red')
            ax.axvline(30, color='red')
            ax.axvline(8, color='red')
        self.eeg_axs[len(self.eeg_axs) - 1].set(xlabel="Freq (Hz)")

        xs = np.arange(0, PLOT_WINDOW_XLIM, 1)
        ys = [[0] * len(xs) for i in range(len(self.eeg_axs))]

        for ind, ax in enumerate(self.eeg_axs):
            (line,) = ax.plot(xs, ys[ind])
            self.eeg_lines.append(line)
        
        def animate_eegfft(i, ys, xs):
            # Get data
            if self.run_eeg_ani:
                EEG_data = np.transpose(self.pull_eeg())
                if len(EEG_data) > 0:
                    if self.inital_eeg_timestamp == 0:
                        # First time
                        self.inital_eeg_timestamp = EEG_data[0][0]

                    # Update the time 
                    self.all_eeg_data['Time'] += list(EEG_data[0] - self.inital_eeg_timestamp)
                    
                    # Update all of the y data
                    for ind, y in enumerate(ys):

                        freq, FFT_data = prep.format_fft_data(EEG_data[i+1])
                        print(ind)
                        print(freq)
                        print(FFT_data)
                        self.eeg_lines[ind].set_data(freq, FFT_data)

                    # Output the current time
                    print(' '*50,end="\r", flush=True)
                    print(f"Elapsed Time {self.all_eeg_data['Time'][-1]}", end="\r", flush="True")

                    # Stop animation when finished collecting set number of seconds
                    if self.all_eeg_data['Time'][-1] >= self.sample_time:
                        self.eeg_fig.suptitle(
                            f"Muse 2 EEG Data: Collection Complete! ~{self.sample_time}"
                        )
                        self.eegfft_ani.event_source.stop()
            else: 
                pass

            return self.eeg_lines

        self.eeg_ani = animation.FuncAnimation(
            self.eeg_fig,
            animate_eegfft,
            fargs=(ys,xs),
            interval =50,
            frames = 200,
            blit=True,
            repeat=True,
        )


    def initialize_eeg_ani(self):
        '''Setup the eeg signal animation
        '''
        PLOT_WINDOW_YLIM = 150
        PLOT_WINDOW_XLIM = 200
        self.eeg_fig, self.eeg_axs = plt.subplots(
            len(self.EEG_DATA_COLUMNS) - 1
        )
        self.eeg_fig.suptitle("Muse 2 EEG Data")
        self.eeg_fig.tight_layout()
        for ind, ax in enumerate(self.eeg_axs):
            ax.set_title(self.EEG_DATA_COLUMNS[ind+1]) # Skip the timeestamp column
            ax.set(ylabel="μV")
            ax.set_ylim([-PLOT_WINDOW_YLIM, PLOT_WINDOW_YLIM])
        self.eeg_axs[len(self.eeg_axs) - 1].set(xlabel="Time (s)")

        xs = np.arange(0, PLOT_WINDOW_XLIM, 1)
        ys = [[0] * len(xs) for i in range(len(self.eeg_axs))]

        for ind, ax in enumerate(self.eeg_axs):
            (line,) = ax.plot(xs, ys[ind])
            self.eeg_lines.append(line)
        
        def animate_eeg(i, ys):
            # Get data
            if self.run_eeg_ani:
                EEG_data = np.transpose(self.pull_eeg())
                if len(EEG_data) > 0:
                    if self.inital_eeg_timestamp == 0:
                        # First time
                        self.inital_eeg_timestamp = EEG_data[0][0]

                    # Update the time 
                    self.all_eeg_data['Time'] += list(EEG_data[0] - self.inital_eeg_timestamp)
                    
                    # Update all of the y data
                    for ind, y in enumerate(ys):
                        # First add data to the master dictionary
                        self.all_eeg_data[self.EEG_DATA_COLUMNS[ind + 1]] += list(EEG_data[ind+1])

                        y += list(EEG_data[ind + 1])
                        y = y[-len(xs):]
                        ys[ind] = y
                        self.eeg_lines[ind].set_ydata(ys[ind])

                    # Output the current time
                    print(' '*50,end="\r", flush=True)
                    print(f"Elapsed Time {self.all_eeg_data['Time'][-1]}", end="\r", flush="True")

                    # Stop animation when finished collecting set number of seconds
                    if self.all_eeg_data['Time'][-1] >= self.sample_time:
                        self.eeg_fig.suptitle(
                            f"Muse 2 EEG Data: Collection Complete! ~{self.sample_time}"
                        )
                        self.eeg_ani.event_source.stop()
            else: 
                pass

            return self.eeg_lines
        
        self.eeg_ani = animation.FuncAnimation(
            self.eeg_fig,
            animate_eeg,
            fargs=(ys,),
            interval =50,
            frames = 200,
            blit=True,
            repeat=True,
        )

    def initialize_accel_ani(self):
        '''Setup the accel signal animation
        '''
        PLOT_WINDOW_YLIM = 3
        PLOT_WINDOW_XLIM = 200
        self.accel_fig, self.accel_axs = plt.subplots(
            len(self.ACCEL_DATA_COLUMNS) - 1
        )
        self.accel_fig.suptitle("Muse 2 ACCEL Data")
        self.accel_fig.tight_layout()
        for ind, ax in enumerate(self.accel_axs):
            ax.set_title(self.ACCEL_DATA_COLUMNS[ind+1]) # Skip the timeestamp column
            ax.set(ylabel="μV")
            ax.set_ylim([-PLOT_WINDOW_YLIM, PLOT_WINDOW_YLIM])
        self.accel_axs[len(self.accel_axs) - 1].set(xlabel="Time (s)")

        xs = np.arange(0, PLOT_WINDOW_XLIM, 1)
        ys = [[0] * len(xs) for i in range(len(self.accel_axs))]

        for ind, ax in enumerate(self.accel_axs):
            (line,) = ax.plot(xs, ys[ind])
            self.accel_lines.append(line)
        
        def animate_accel(i, ys):
            # Get data
            ACC_data = np.transpose(self.pull_acc())
            if len(ACC_data) > 0:
                if self.inital_accel_timestamp == 0:
                    # First time
                    self.inital_accel_timestamp = ACC_data[0][0]
                    self.accel_ani.event_source.stop()

                # Update the time 
                self.all_accel_data['Time'] += list(ACC_data[0] - self.inital_accel_timestamp)
                
                # Update all of the y data
                for ind, y in enumerate(ys):
                    # First add data to the master dictionary
                    self.all_accel_data[self.ACCEL_DATA_COLUMNS[ind + 1]] += list(ACC_data[ind+1])

                    y += list(ACC_data[ind + 1])
                    y = y[-len(xs):]
                    ys[ind] = y
                    self.accel_lines[ind].set_ydata(ys[ind])
            
                # Stop animation when finished collecting set number of seconds
                if self.all_accel_data['Time'][-1] >= self.sample_time:
                    self.accel_fig.suptitle(
                        f"Muse 2 Accel Data: Collection Complete! ~{self.sample_time}"
                    )
                    self.accel_ani.event_source.stop()

            return self.accel_lines
        
        self.accel_ani = animation.FuncAnimation(
            self.accel_fig,
            animate_accel,
            fargs=(ys,),
            interval =50,
            frames = 200,
            blit=True,
            repeat=True,
        )

    def initialize_gyro_ani(self):
        '''Setup the gyro signal animation
        '''
        PLOT_WINDOW_YLIM = 100
        PLOT_WINDOW_XLIM = 200
        self.gyro_fig, self.gyro_axs = plt.subplots(
            len(self.GYRO_DATA_COLUMNS) - 1
        )
        self.gyro_fig.suptitle("Muse 2 GYRO Data")
        self.gyro_fig.tight_layout()
        for ind, ax in enumerate(self.gyro_axs):
            ax.set_title(self.GYRO_DATA_COLUMNS[ind+1]) # Skip the timeestamp column
            ax.set(ylabel="μV")
            ax.set_ylim([-PLOT_WINDOW_YLIM, PLOT_WINDOW_YLIM])
        self.gyro_axs[len(self.gyro_axs) - 1].set(xlabel="Time (s)")

        xs = np.arange(0, PLOT_WINDOW_XLIM, 1)
        ys = [[0] * len(xs) for i in range(len(self.gyro_axs))]

        for ind, ax in enumerate(self.gyro_axs):
            (line,) = ax.plot(xs, ys[ind])
            self.gyro_lines.append(line)
        
        def animate_gyro(i, ys):
            # Get data
            GYRO_data = np.transpose(self.pull_gyro())
            if len(GYRO_data) > 0:
                if self.inital_gyro_timestamp == 0:
                    # First time
                    self.inital_gyro_timestamp = GYRO_data[0][0]
                    self.gyro_ani.event_source.stop()

                # Update the time 
                self.all_gyro_data['Time'] += list(GYRO_data[0] - self.inital_gyro_timestamp)
                
                # Update all of the y data
                for ind, y in enumerate(ys):
                    # First add data to the master dictionary
                    self.all_gyro_data[self.GYRO_DATA_COLUMNS[ind + 1]] += list(GYRO_data[ind+1])

                    y += list(GYRO_data[ind + 1])
                    y = y[-len(xs):]
                    ys[ind] = y
                    self.gyro_lines[ind].set_ydata(ys[ind])
                
                # Stop animation when finished collecting set number of seconds
                if self.all_gyro_data['Time'][-1] >= self.sample_time:
                    self.gyro_fig.suptitle(
                        f"Muse 2 Gyro Data: Collection Complete! ~{self.sample_time}"
                    )
                    self.gyro_ani.event_source.stop()

            return self.gyro_lines
        
        self.gyro_ani = animation.FuncAnimation(
            self.gyro_fig,
            animate_gyro,
            fargs=(ys,),
            interval =50,
            frames = 200,
            blit=True,
            repeat=True,
        )

    def start_animations(self):
        '''Show all of the animations
        ''' 
        input("Press Enter when you are ready to collect data")
        for ind, ani in enumerate([self.eeg_ani, self.accel_ani, self.gyro_ani]):
            if ani is not None:
                self.set_run_plot_state(ind)
        plt.show()    
        
    def set_run_plot_state(self, index):
        '''
        0 = eeg_ani
        1 = accel_ani
        2 = gyro_ani
        '''           
        if index == 0:
            self.run_eeg_ani = True
            return
        if index == 1:
            self.run_accel_ani = True
            return
        if index == 2:
            self.run_gyro_ani = True
            return
        print('Couldn\'t set the run state')
        return
    
        

    ###
    # MARK: Method Overriding
    ###
    def _push(self, data, timestamps, offset=0):
        '''Override method to reformat data output. Timestamps should be the first column
        '''
        for ii in range(data.shape[1]):
            if not is_data_valid(data[:, ii], timestamps[ii]):
                continue
            if offset == EEG_PORT_OFFSET:
                to_append_eeg_data = [
                    (timestamps[ii]),
                    data[0, ii],
                    data[1, ii],
                    data[2, ii],
                    data[3, ii],
                    data[4, ii],
                ]
                if len(self.eeg_buff) >= self.max_buff_len:
                    self.eeg_buff.pop(0)
                self.eeg_buff.append(to_append_eeg_data)

            elif offset == PPG_PORT_OFFSET:
                to_append_ppg_data = [
                    (timestamps[ii]),
                    data[0, ii],
                    data[1, ii],
                    data[2, ii],
                ]
                if len(self.ppg_buff) >= self.max_buff_len:
                    self.ppg_buff.pop(0)
                self.ppg_buff.append(to_append_ppg_data)

            elif offset == ACC_PORT_OFFSET:
                to_append_acc_data = [
                    (timestamps[ii]),
                    data[0, ii],
                    data[1, ii],
                    data[2, ii],
                ]
                if len(self.acc_buff) >= self.max_buff_len:
                    self.acc_buff.pop(0)
                self.acc_buff.append(to_append_acc_data)

            elif offset == GYRO_PORT_OFFSET:
                to_append_gyro_data = [
                    (timestamps[ii]),
                    data[0, ii],
                    data[1, ii],
                    data[2, ii],
                ]
                if len(self.gyro_buff) >= self.max_buff_len:
                    self.gyro_buff.pop(0)
                self.gyro_buff.append(to_append_gyro_data)

    def search_and_connect(self):
        print('Connecting Sequence is starting... ')
        return super().search_and_connect()

def print_listening(frame):
    message = "Listening"
    period_cnt = frame % 5
    for k in range(period_cnt):
        message += "."
    print("{}".format(" " * 50), end="\r", flush=True)
    print("{}".format(message), end="\r", flush=True)


# https://stackoverflow.com/questions/18114560/python-catch-ctrl-c-command-prompt-really-want-to-quit-y-n-resume-executi
def exit_gracefully(signum, frame):
    # restore the original signal handler as otherwise evil things will happen
    # in raw_input when CTRL+C is pressed, and our signal handler is not re-entrant
    signal.signal(signal.SIGINT, original_sigint)

    try:
        if input("\nReally quit? (y/n)> ").lower().startswith("y"):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Ok ok, quitting")
        sys.exit(1)

    # restore the exit gracefully handler here
    signal.signal(signal.SIGINT, exit_gracefully)

def beep(every, for_duration):
    '''Play the windows beeping noise every n seconds for a duration of m seconds

    Parameters
    ----------
    every: int
        When to beep
    for_duration: int
        How long to beep for
    '''
    for i in range(int(for_duration/every)):
        print('Beeping!')
        winsound.Beep(1000, 1000)
        time.sleep(every)

# ==================================================
# ==================================================

def main(mode="r"):
    SAMPLE_TIME = 600
    LABEL_INTERVAL = 300
    loop = asyncio.get_event_loop()
    data_collector = MuseData(loop=loop, sample_time=SAMPLE_TIME)
    data_collector.search_and_connect()

    # Beeping noise
    # beep_process = Process(target=beep, args=(LABEL_INTERVAL, SAMPLE_TIME))
    # beep_process.start()

    # ten_data_collector.initialize_eeg_ani()
    data_collector.initialize_eegfft_ani()
    # ten_data_collector.initialize_accel_ani()
    # ten_data_collector.initialize_gyro_ani()
    data_collector.start_animations()
    # ten_data_collector.save_all_data()
    # beep_process.terminate()
    data_collector.disconnect()

# ==================================================
# ==================================================

if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exit_gracefully)
    main()