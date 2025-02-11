import serial
import numpy as np
import time
from scipy.signal import butter, lfilter

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
    print("USB thread initiated")
    global connected
    global input_buffer
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
    print("USB thread quitting")
    

# ---------------------------------------------------------------------------------------------------
# User code


#this is the alleged high-pass filter... we tried our best :)
def high_pass_filter (emg, cutoff, fs, order=4):
    nyquist= 0.5 * fs
    normalCutoff = cutoff / nyquist 
    b,a = butter(order, normalCutoff, btype= 'high', analog= False)
    filtered_emg = lfilter (b,a, emg) 
    return filtered_emg
    

def get_emg_activation():
    global sample_buffer
    emg = sample_buffer.copy()
    
    # Don't change
    emg = emg[-display_size:]
    sample_buffer = sample_buffer[-display_size:]


    # Can change
    fs= 10000
    cutoff= 70
    emg = emg - emg.mean()
    filtered_emg= high_pass_filter( emg, cutoff, fs, order=3)

    #   absolute value
    filtered_emg = np.abs(filtered_emg) 
    #   mean
    mean_emg = np.mean(filtered_emg[-200:])
    return mean_emg
