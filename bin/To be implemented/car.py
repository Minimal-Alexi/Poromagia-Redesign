#/home/garage/pythenv is the location for python virtual library, where all modules should preferably be installed
#cmd -> cd pythenv -> source bin/activate -> pip install (the thing you want to install)

import numpy as np
import pytesseract as tes
from pytesseract import Output
import cv2 as cv
import re
from datetime import datetime
from FastDebugger import fd

# For windows computers, download TesseractOCR and add its path here
#tes.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#tes.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

# This code is WIP
# It will likely not work well with digital images as its been calibrated for photos

#DEBUGGING INSTRUCTIONS!
#To debug errors, especially cropping errors it will be helpful to start with these steps:

#Remove the image argument within parentheses in crop_and_read
#Uncomment  cv.imread at the start in crop_and_read and set file path where the image you want to read is
#Comment out return set_data at the end of crop_and_read
#Uncomment entire text block for cv.imshow below it
#Uncomment the function call at the very end of this entire script
#Uncomment drawrectangle() in find_text()
#Run script on image of your choice

#Remember to put everything back once you are done!

# TODO:
# define what functions do and what arguments they should take

def car(path:str, rotation:str = 'CW'):
    ''' Main card reading function. Takes a path to an image file and an optional rotation argument.
    
    Parameters:
    ----------
    path : str
        Path to the image file to be read.
    rotation : str
        Optional argument to correct for camera orientation. Default is clockwise rotation.
        accepted values: 'CW', 'CCW', 'UP', 'DOWN'

    Returns:
    -------
    dict
        A dictionary containing the collector number, rarity, set name and language of the card in the image.
    '''

    #Begin
    startTime = datetime.now()

    #read image file and check that it exists
    # img = cv.imread('/home/garage/Pictures/aven.jpg')
    img = cv.imread(path)
    assert img is not None, "file could not be read"

    #Corrects for the camera position, remove if upright OR upsidedown!
    match rotation:
        case 'CW':
            img = cv.rotate(img, cv.ROTATE_90_CLOCKWISE)
        
        case 'CCW':
            img = cv.rotate(img, cv.ROTATE_90_COUNTERCLOCKWISE)
        
        case 'UP':
            img = cv.rotate(img, cv.ROTATE_180)
        
        case 'DOWN':
            pass
        
        case _:
            print('Invalid rotation argument. Defaulting to clockwise rotation.')
    
    #Get card borders
    boundaries,_= _find_contours(img)

    #Fix potential problems with slightly angled cards in the picture
    fixed_image = _fix_rotation(img, boundaries[0], boundaries[2], img.shape[1], img.shape[0])

    #Recalculate card borders, but this time only get the bounding XY points
    _,new_corners = _find_contours(fixed_image)

    #Cropping and resizing the card out of the picture
    card, thumbnail= _crop_resize(fixed_image, new_corners)

    #Final check that the card is not upside down
    orientation = _check_orientation(thumbnail)
    assert orientation is not None, 'Problem occurred while OSDing. Card is likely upside down. Exiting program.'

    if orientation == 180:
        card = cv.rotate(card, cv.ROTATE_180)

    #Corresponds to roughly left edge to middle of the bottom part of a card
    bot_crop = card[1630:1770,60:700]
    gray_bot = cv.cvtColor(bot_crop, cv.COLOR_BGR2GRAY)
    blur_bot = cv.medianBlur(gray_bot,5)

    #Fetches all words in the crops
    text_block_list = _find_text(blur_bot, '--psm 3' )

    #Minor image sharpening to improve text contrast for reading the crops in the following loop
    sharpen = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv.filter2D(gray_bot, -1, sharpen)
    contrast = 1
    brightness = 5
    sharpened = cv.addWeighted(sharpened, contrast, np.zeros(gray_bot.shape, gray_bot.dtype), 0, brightness) 


    #sharpened = cv.threshold(sharpened, 0, 255,cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]

    #TODO: change this
    kernel = cv.getStructuringElement(cv.MORPH_ERODE, (2, 2))
    sharpened = cv.morphologyEx(sharpened, cv.MORPH_ERODE, kernel, iterations=1)
    
    #Stuff needed to build name bar cropping later
    ######################################
    #top_crop = card[40:200,60:1200]
    #gray_top = cv.cvtColor(top_crop, cv.COLOR_BGR2GRAY)
    #canny_top = cv.Canny(gray_top,80,220) 
    #name_block_list = find_text(gray_top, '--psm 7')
    #a,b,c,d = name_block_list[i]

    #Hackiest hack ever made, gets the box coordinates for collector number. As Tesseract goes from left to right pixel by pixel so likely its going to be some element of the list, this works to set a fixed cropping point for reading the text
    #Unless theres only artifacts, more hacky checks to prevent issues are TBD
    set_data = None
    for i in (0,1,2,3,4,5,6,7):
        try:
            x,y,w,h = text_block_list[i]
            cn_crop = sharpened[y-5:y+h+5, x-5:x+w+60]
            sn_crop = sharpened[y+25:y+65, x-5:x+w+25]
        except:
            raise IndexError('Cropping went wrong. There is a problem with crop coordinates. Contours were most likely not found. If the error persists, debug instructions can be found in the start of the script!')
        else:
            set_data = _get_strings(cn_crop,sn_crop)
            if set_data:
               print('Valid crop coordinates found on row:', i)
               print('Collector number coordinates <x,y,w,h>:',text_block_list[i])
               break
            else:
                print('Trying other coordinates.')

    # TODO: change this to look for other areas afterwards to add compatibility for older cards and other card types
    # Illustration & Name can be used to determine the card object of older magic cards
                
    if i == 7 and set_data is None:
        raise TimeoutError('No text found within 8 tries. Exiting program')
    else:
        print('Set data text found by tesseract:', set_data)
        print('Image recognition execution time: ', datetime.now() - startTime)

        # cv.namedWindow("bottom",cv.WINDOW_NORMAL)
        # cv.imshow("bottom", cn_crop)
        # cv.namedWindow("set name",cv.WINDOW_NORMAL)
        # cv.imshow("set name", sn_crop)
        # cv.namedWindow("card",cv.WINDOW_NORMAL)
        # cv.imshow("card", card)
        # cv.waitKey(0)


    return set_data

    # while True:
    #     cv.namedWindow("card",cv.WINDOW_NORMAL)
    #     cv.imshow("card", card)
    #     cv.namedWindow("card number",cv.WINDOW_NORMAL)
    #     cv.imshow("card number", cn_crop)
    #     cv.namedWindow("bottom",cv.WINDOW_NORMAL)
    #     cv.imshow("bottom", bot_crop)
    #     cv.namedWindow("set name",cv.WINDOW_NORMAL)
    #     cv.imshow("set name", sn_crop)
    #     cv.waitKey(0)
    #     sys.exit() # to exit from all the processes

# cv.destroyAllWindows() # destroy all windows

def _find_contours(image):

    # make a grayscale copy
    gray_img = cv.cvtColor(image, cv.COLOR_BGR2GRAY) 
    # Get rid of noise
    blur = cv.medianBlur(gray_img, 15)

    # Black magic math to get a binary image

    #Turns out canny is better but im leaving this here just in case, if you want to use it change MORPH_RECT to 5,5
    #thresh = cv.adaptiveThreshold(blur, 255,cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 21, 10)

    canny = cv.Canny(blur, 80, 120, L2gradient = True)
    # define a structuring element for manipulating white and black pixel areas
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (19, 19))
    # apply a dilation operation to the thresholded image
    dilate = cv.morphologyEx(canny, cv.MORPH_DILATE, kernel, iterations = 1)
    
    contours,_ = cv.findContours(dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    # #Arbitrary area for discarding contours, seems to work nicely
    min_area = 100000
    for cnt in contours:
        if cv.contourArea(cnt) > min_area:
            largest_contour = cnt

    #Note: minAreaRect returns -> (Center XY of rectangle, size of rectangle, angle)
    rect = cv.minAreaRect(largest_contour)
    #box elements start from bottom left and go clockwise
    box = cv.boxPoints(rect)

    #For debugging contours
    # cv.drawContours(image, largest_contour, -1, (0,255,0), 5)
    # cv.namedWindow("debug1",cv.WINDOW_NORMAL)
    # cv.imshow("debug1", dilate)
    # cv.namedWindow("debug2",cv.WINDOW_NORMAL)
    # cv.imshow("debug2", image)
    # cv.waitKey(0)
    return rect, box


def _fix_rotation(image, center:any, angle:float, width:int, height:int):
    
    # shitty check to make sure the angle has been properly calculated, sometimes MinAreaRect mistakes orientation
    # This works because most cards will hopefully be tilted by only a few degrees
    if angle > 45:
        angle = angle-90

    rotation_matrix = cv.getRotationMatrix2D(center, angle, 1)
    new = cv.warpAffine(image, rotation_matrix, (width, height))
    return new


def _crop_resize(image, corners):
    
    corners = corners.astype(int) 

    # Yoinks the corners from the array and crops 
    xmax, ymax = corners.max(axis = 0)
    xmin, ymin = corners.min(axis = 0)
    cropping = image[ymin:ymax,xmin:xmax]

    #Fixed width and height corresponding to MTG card aspect ratio (1:1.4)
    #Also get a small thumbnail roughly 1/3rd of size for later use with Tesseract OSD etc.
    w_h = (int(1270), int(1778))
    resized = cv.resize(cropping, w_h)
    t_w_h = (int(419), int(587))
    small = cv.resize(resized, t_w_h)

    return resized, small

def _check_orientation(small):
    
    check = cv.cvtColor(small, cv.COLOR_BGR2GRAY)
    check = cv.adaptiveThreshold(check, 255, cv.ADAPTIVE_THRESH_MEAN_C, cv.THRESH_BINARY_INV, 21, 10)

    # It will simply do tesseract black magic to calculate if the text is upside down or sideways. Actually, it also does a lot more. Very resource heavy.
    # Returning an error in the OSD process means in all likelihood that the card face is upside down. Crop and Read will return back to main and throw this card into the misc box.
    try:
        osd = tes.image_to_osd(check, output_type='dict', config = '--psm 0')
        orientation = osd['orientation']
    except tes.TesseractError as ch_or:
        print('Tesseract error: ', str(ch_or))
        return None
    else:
        return orientation

def _find_text(image, conf):

    # Reads the image and makes a large sorted list just like OSD with headers on top of columns of information for each item in the picture
    d = tes.image_to_data(image, output_type=Output.DICT, config = conf)
    n_boxes = len(d['level'])

    all_boxes = []
    for i in range(n_boxes):
        if d["text"][i] != "":
            text_boxes = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            all_boxes.append(text_boxes)

        # FOR DEBUGGING!
        # Rectangle will affect the tesseract reading if on! Remember to cv.imshow whatever picture you passed to find_text.
            #x,y,w,h = text_boxes
            #cv.rectangle(image, (x, y), (x + w, y + h), color=(255, 0, 255), thickness=1)
    
    return all_boxes


def _get_strings(number_crop, set_crop):

    try:
        num_string = tes.image_to_string(number_crop, config = "-c tessedit_char_whitelist=0123456789/tslcurmTSLCURM\\ --psm 7")
        set_string = tes.image_to_string(set_crop, config = "-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ*\\ --psm 7")

        num_string = num_string.strip()
        set_string = set_string.strip()

        collector_number = ''
        rarity =''

        for char in num_string:
            if char.isdigit() or char == '/':
                collector_number += char
            else:
                rarity = char

        set_name = set_string[0:3]
        language = set_string[-2:]
        card_text = {"collector_number": collector_number, "rarity": rarity, "set_name": set_name, "language": language}

        # return collector_number, rarity, set_name, language
        return card_text
    except:
        print('Failure to get string!')
        return False
#Only for debugging!!! (So you can run this script only)
car('/home/garage/Pictures/cler.jpg', 'CW')