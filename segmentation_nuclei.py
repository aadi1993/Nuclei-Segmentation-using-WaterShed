# -*- coding: utf-8 -*-
"""
Created on Sun Jul 25 16:20:06 2021

@author: Abdul Rahman
"""


import cv2
import numpy as np
from matplotlib import pyplot as plt
from scipy import ndimage
from skimage import measure, color, io


img = cv2.imread('C:/Users/Lenovo/Desktop/img1.png')
cv2.imshow('img', img)
cv2.waitKey(0)


cells=img[:,:,0]
cv2.imshow('cells', cells)
cv2.waitKey(0)


pixels_to_um = 0.454
ret1, thresh = cv2.threshold(cells, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)


kernel = np.ones((3,3),np.uint8)
opening = cv2.morphologyEx(thresh,cv2.MORPH_OPEN,kernel, iterations = 2)

from skimage.segmentation import clear_border
opening = clear_border(opening) #Remove edge touching grains
#Check the total regions found before and after applying this. 


sure_bg = cv2.dilate(opening,kernel,iterations=10)

cv2.imshow('sure_bg', sure_bg)
cv2.waitKey(0)



dist_transform = cv2.distanceTransform(opening,cv2.DIST_L2,5)



ret2, sure_fg = cv2.threshold(dist_transform,0.5*dist_transform.max(),255,0)



sure_fg = np.uint8(sure_fg)
cv2.imshow('sure_fg', sure_fg)
cv2.waitKey(0)

unknown = cv2.subtract(sure_bg,sure_fg)



ret3, markers = cv2.connectedComponents(sure_fg)


markers = markers+10
markers[unknown==255] = 0

markers = cv2.watershed(img,markers)
#Let us color boundaries in yellow. 
img[markers == -1] = [0,255,255]  

img2 = color.label2rgb(markers, bg_label=0)
cv2.imshow('img2', img2)
cv2.waitKey(0)


regions = measure.regionprops(markers, intensity_image=cells)

#Can print various parameters for all objects
for prop in regions:
    print('Label: {} Area: {}'.format(prop.label, prop.area))

#Best way is to output all properties to a csv file
#Let us pick which ones we want to export. 

propList = ['Area',
            'equivalent_diameter', #Added... verify if it works
            'orientation', #Added, verify if it works. Angle btwn x-axis and major axis.
            'MajorAxisLength',
            'MinorAxisLength',
            'Perimeter',
            'MinIntensity',
            'MeanIntensity',
            'MaxIntensity']    
    

output_file = open('C:/Users/Lenovo/Desktop/cell_measurements.csv', 'w')
output_file.write(',' + ",".join(propList) + '\n') #join strings in array by commas, leave first cell blank
#First cell blank to leave room for header (column names)

for region_props in regions:
    #output cluster properties to the excel file
    output_file.write(str(region_props['Label']))
    for i,prop in enumerate(propList):
        if(prop == 'Area'): 
            to_print = region_props[prop]*pixels_to_um**2   #Convert pixel square to um square
        elif(prop == 'orientation'): 
            to_print = region_props[prop]*57.2958  #Convert to degrees from radians
        elif(prop.find('Intensity') < 0):          # Any prop without Intensity in its name
            to_print = region_props[prop]*pixels_to_um
        else: 
            to_print = region_props[prop]     #Reamining props, basically the ones with Intensity in its name
        output_file.write(',' + str(to_print))
    output_file.write('\n')

