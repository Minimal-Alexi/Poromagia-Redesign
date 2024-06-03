import sys
import serial
import time
import car
import CardDataFetch
import cv2 as cv
import traceback
#Box choices for Poromagia:
#Box 1: Lands with low value
#Box 2: Cheap cards
#Box 3: Valuable cards
#Box 4: Error box

SerialObj = serial.Serial(port='COM9', baudrate=9600,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE, timeout=5, write_timeout=5)
num_of_cards_sorted = [0,0,0,0]
box_choice = 0

def main():
    try:
        set_data = car(cv.imread('/home/garage/Pictures/aven.jpg'))
    except:
        print(traceback.format_exc())
        box_choice = 4
        set_data = None
        num_of_cards_sorted[3] = num_of_cards_sorted[3]+1
    else:
        if set_data is not None:
            match set_data[1]: #Match rarity 
                case 'C':
                    box_choice = 2
                    num_of_cards_sorted[1] = num_of_cards_sorted[1]+1
                case 'L':
                    box_choice = 1
                    num_of_cards_sorted[0] = num_of_cards_sorted[0]+1
                case 'M':
                    box_choice = 3
                    num_of_cards_sorted[2] = num_of_cards_sorted[2]+1

    print('Card goes into box:',box_choice)
    print('Number of cards sorted in box #',box_choice,': ', num_of_cards_sorted[box_choice-1], sep='')

    box_choice = int(box_choice)
    box_choice = box_choice.to_bytes(length=1,byteorder='little',signed=False)
    SerialObj.write(box_choice)
    response = SerialObj.readline().decode('utf-8').rstrip()  # Decode bytes to string and strip newline character
    print(response)
main()