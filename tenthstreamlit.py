import numpy as np
import streamlit as sl
import pydicom
import random
import matplotlib.pyplot as plt
import matplotlib as mpl
from PIL import ImageColor
def pixs(img):
    img.seek(0)
    dataset = pydicom.read_file(img)
    m=dataset.RescaleSlope
    b= dataset.RescaleIntercept
    x = dataset.pixel_array
    p = x*m + b 
    pixels = p.astype(np.int16)
    return pixels

def colorize(img, bounds, colors, trfa, x1, x2, y1, y2):
    pixels = pixs(img)
    pixels = np.asarray(pixels)
    boundaries = bounds   
    r, c = pixels.shape
    newpixels = np.zeros((r, c, 3), dtype=np.int16)            
    if trfa:
        color = []
        for i in colors:
            c = ImageColor.getcolor(i, "RGB")
            color.append(c)
        for r in range(len(pixels)):
                for c in range(len(pixels[0])):
                    for l in range(len(color)):
                        if c>=x1 and c<=x2 and r>=y1 and r<=y2:
                            if pixels[r, c] >= boundaries[l] and pixels[r,c] < boundaries[l+1]:
                                newpixels[r,c, :] = color[l]
    if trfa == False:
        sl.text("Pick colors")
        color = 0

 
    return newpixels,color, boundaries, pixels

def colorbar(color,boundaries):
    color = np.array(color)
    figure, axes = plt.subplots(figsize=(len(boundaries)-1, 1))
    colormap = (mpl.colors.ListedColormap(color/255))
    norm = mpl.colors.BoundaryNorm(boundaries, len(boundaries)-1)
    figure.colorbar(mpl.cm.ScalarMappable(cmap=colormap, norm=norm),cax=axes, ticks=boundaries, spacing='proportional', orientation='horizontal', label='colorbar')
    sl.pyplot(figure)
    
def findminmax(img, x1, x2, y1, y2):
    p = pixs(img)
    rows, cols = p.shape
    min = 2000
    max = -2048
    for r in range(rows):
        for c in range(cols):
            if c>=x1 and c<=x2 and r>=y1 and r<=y2:
                b = p[r,c]
                if b<min and b!=-2048:
                    min = b
                if b>max:
                    max=b

    return min, max
def percentoccurence(img, b1, b2, x1, x2, y1, y2):
    pixels = pixs(img)
    c1 = 0
    c2= 0
    rows, cols = pixels.shape
    for r in range(rows):
        for c in range(cols):
            pix = pixels[r, c]
            #greater than or equal to
            if c>=x1 and c<=x2 and r>=y1 and r<=y2:
                if pix>=b1 and pix<=b2:
                    c1 = c1 +1
                if pix!=-2048:
                    c2 = c2+1
    per = (c1/c2)* 100
    return per

sl.write("Colorize a DICOM image")
fnext = sl.sidebar.file_uploader("Load file", type='dcm')
tf = True
if fnext is None:
    sl.text("No Image Yet")
else:
    if tf==True:
        pixels = pixs(fnext)
        fig = plt.figure()
        plt.imshow(pixels, cmap="gray")
        sl.pyplot(fig)
        sl.text("Enter coordinates for region of interest (rectange shaped)")
        x1= sl.number_input("X coordinate for top left corner of rectangle", min_value = 0, max_value = 512)
        y1= sl.number_input("Y coordinate for top left corner of rectangle", min_value = 0, max_value = 512)
        x2 = sl.number_input("X coordinate for bottom right corner of rectangle", min_value = 0, max_value = 512)
        y2 = sl.number_input("Y coordinate for bottom right corner of rectangle", min_value = 0, max_value = 512)
        #roi = sl.checkbox("Click if finsihed entering region of interest")
        
        min, max= findminmax(fnext, x1, x2, y1, y2)
        sl.text("Minimum HU value: ")
        if min == 2000:
            sl.text("?")
        else :
            sl.text(min)
        sl.text("Maximum HU value: ")
        if max == -2048:
            sl.text("?")
        else :
            sl.text(max)
        groupnumber= sl.number_input("How many color groups", min_value=2)
        bounds = np.zeros(groupnumber+1)
        for i in range(groupnumber-1):
            bounds[i+1] = sl.number_input("Internal Boundary", value=0, key=str(i))
            #min_value = min, max_value = max
        bounds[0] = min
        bounds[groupnumber] = max
        sl.text("Color chooser")
        bnc = sl.checkbox("Click to pick colors")
        if bnc == True:
            color = []
            for i in range(groupnumber):
                l = str(i+1)
                label = "Color group " + l
                cp = sl.color_picker(label, key=label)
                color.append(cp)
        
        bn = sl.checkbox("Click if finsihed entering boundaries and/or colors")
        if bn:
            sl.text("Colorized Image")
            if bnc:
                s,col,_, _= colorize(fnext, bounds, color, True, x1, x2, y1, y2)
                sl.image(s, use_column_width=False, clamp=True)
                colorbar(col,bounds)
                sl.text("Find percent occurence of pixels between two values")
                b1 = sl.number_input("Value 1 (lower value)")
                b2 = sl.number_input("Value 2 (higher value)")
                b = sl.checkbox("Click to find percent occurence")
                if b:
                    p = percentoccurence(fnext, b1, b2, x1, x2, y1, y2)
                    per = round(p, 2)
                    sl.text(str(per)+"%")
            if bnc == False:
                s,col,_, _= colorize(fnext, bounds, [0,0,0], False, x1, x2, y1, y2)
            
                
            