# ---- Derived from:
# Backyard Brains Sep. 2019
# Made for python 3
# First install serial library
# Install numpy, pyserial, matplotlib
# pip3 install pyserial
#
# Code will read, parse and display data from BackyardBrains' serial devices
#
# Written by Stanislav Mircic
# stanislav@backyardbrains.com
#%% import block
import threading
import serial
import time
import scipy
import matplotlib.pyplot as plt 
import numpy as np
from datetime import datetime
from PIL import Image
from scipy.signal import butter, lfilter


#%% Make filename

nowvar = datetime.now()
filetime = nowvar.strftime('%Y-%m-%d_%H-%M%S')
filename = 'Data/testfile_' + filetime + '.csv'


#%% main code
global connected
connected = False
# When done acquiring, tell the thread to release all resources
# by setting to false
global thread_should_run
thread_should_run = True
#change name of the port here
port = '/dev/ttyACM0'
#port = 'COM3'
#port = '/dev/cu.usbmodem1411101'
#port = '/dev/cu.usbmodem14101'
baud = 230400
global input_buffer
global sample_buffer
global cBufTail
cBufTail = 0
input_buffer = []
sample_rate = 10000
#display_size = 30000 #3 seconds
display_size = 200 # in 0.1 msec for default sample rate
sample_buffer = np.linspace(0,0,display_size)
serial_port = serial.Serial(port, baud, timeout=0)


def checkIfNextByteExist():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        
        if tempTail==len(input_buffer): 
            return False
        return True
    

def checkIfHaveWholeFrame():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        while tempTail!=len(input_buffer): 
            nextByte  = input_buffer[tempTail] & 0xFF
            if nextByte > 127:
                return True
            tempTail = tempTail +1
        return False;
    
def areWeAtTheEndOfFrame():
        global cBufTail
        global input_buffer
        tempTail = cBufTail + 1
        nextByte  = input_buffer[tempTail] & 0xFF
        if nextByte > 127:
            return True
        return False

def numberOfChannels():
    return 2

def handle_data(data):
    global input_buffer
    global cBufTail
    global sample_buffer    
    if len(data)>0:

        cBufTail = 0
        haveData = True
        weAlreadyProcessedBeginingOfTheFrame = False
        numberOfParsedChannels = 0
        
        while haveData:
            MSB  = input_buffer[cBufTail] & 0xFF
            
            if(MSB > 127):
                weAlreadyProcessedBeginingOfTheFrame = False
                numberOfParsedChannels = 0
                
                if checkIfHaveWholeFrame():
                    
                    while True:
                        
                        MSB  = input_buffer[cBufTail] & 0xFF
                        if(weAlreadyProcessedBeginingOfTheFrame and (MSB>127)):
                            #we have begining of the frame inside frame
                            #something is wrong
                            break #continue as if we have new frame
            
                        MSB  = input_buffer[cBufTail] & 0x7F
                        weAlreadyProcessedBeginingOfTheFrame = True
                        cBufTail = cBufTail +1
                        LSB  = input_buffer[cBufTail] & 0xFF

                        if LSB>127:
                            break #continue as if we have new frame

                        LSB  = input_buffer[cBufTail] & 0x7F
                        MSB = MSB<<7
                        writeInteger = LSB | MSB
                        numberOfParsedChannels = numberOfParsedChannels+1
                        if numberOfParsedChannels>numberOfChannels():
                            print(f'TOO MANY CHANNELS: {numberOfParsedChannels}')  #TODO
                            #we have more data in frame than we need
                            #something is wrong with this frame
                            break #continue as if we have new frame
            

                        sample_buffer = np.append(sample_buffer,writeInteger-512)
                        

                        if areWeAtTheEndOfFrame():
                            break
                        else:
                            cBufTail = cBufTail +1
                else:
                    haveData = False
                    break
            if(not haveData):
                break
            cBufTail = cBufTail +1
            if cBufTail==len(input_buffer):
                haveData = False
                break


def read_from_port(ser):
    global connected
    global input_buffer
    global thread_stop_signal
    while not connected:
        #serin = ser.read()
        connected = True

        while thread_should_run:
           
           reading = ser.read(1024)
           if(len(reading)>0):
                reading = list(reading)
                #here we overwrite if we left some parts of the frame
                # from previous processing should be changed             
                input_buffer = reading.copy()
                #print("len(reading)",len(reading))
                handle_data(reading)
           
           time.sleep(0.001)



#%% -------------------------------------------------------------------------------------


#%% Start user code

#Generate graphics

# decimal list generator, smooth pursuit
bound = 100
start = int(bound/2)
#start = 1
#step = 1

num_steps = 100
# fix_frame = 150

xff = np.concatenate(
    (np.full((50,),50),
     np.full((50,),80),
     np.full((50,),50),
     np.linspace(start,bound,num_steps)
    ) )
yf = np.full((len(xff),),bound/2)


#x = [start + (iii*step) for iii in range(start, int(bound/step)-int(start/step))]
#y = [bound/2]

#%% Start acquisition and display

thread = threading.Thread(target=read_from_port, args=(serial_port,))
thread.start()

xi = np.linspace(-display_size/sample_rate, 0, num=display_size)

t_old = time.time()
t_start = time.time()
t_old = t_start
breakFlag = False

plt.figure()

#this is the alleged high-pass filter... we tried our best :)
def high_pass_filter (emg, cutoff, fs, order=4):
    nyquist= 0.5 * fs
    normalCutoff = cutoff / nyquist 
    b,a = butter(order, normalCutoff, btype= 'high', analog= False)
    filtered_emg = lfilter (b,a, emg) 
    return filtered_emg
    
while True:
    t = time.time()
    #print(f'Loop took {1e3*(t-t_old)} msec')
    t_old=t
    
    # Get data
    if(len(sample_buffer)>0):
        #i = len(sample_buffer)
        #print(len(sample_buffer))
        emg = sample_buffer.copy()
        
        #print(f'{emg.shape} data array')
        #print(emg[-10::2])
        #print(emg[-9::2])
        
        # Don't change
        emg = emg[-display_size:]
        sample_buffer = sample_buffer[-display_size:]
        #print(eog[-10:])


        # TODO:
        #   high pass the raw emg
        # defining variables 
        fs= 10000
        cutoff= 20
        filtered_emg= high_pass_filter( emg, cutoff, fs, order=4)
        

    
        #   absolute value
        filtered_emg = np.abs(filtered_emg) 
        #   mean
        mean_emg= np.mean(filtered_emg[-200:])
        print(mean_emg)

        #plt.plot(emg)
        #plt.pause(1)
        #dehbjhbjhjhb
        # Compute eye position from EOG
        
        
        
        #curMean = np.mean(FILTERED)
    
    # Write data to file
    #FID.write(f'{t},{np.mean(eog[-300:])},{allChoices[trialNum]}\n') 
    #FID.write(f'{t},{np.mean(eog[-300:])},{xff[jjj]},{yf[jjj]}\n')        
        
    if (t-t_start>6):
        break

#Remove pet image
print(f'Trial took {t-t_start} seconds')
#plih.remove()

print('--- Out of loop ---\nClosing...')
    
#plt.text(0,200,'Congratulations on your new pets!!!!')

# Show All Choices

# Create new plot




#_ = input('waiting for return')

#plt.close('all')

thread_should_run = False
time.sleep(1)  # Give time for thread to close before closing port
serial_port.close()

print('... Closed')
#ser.close()

