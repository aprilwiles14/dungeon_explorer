#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 16:02:08 2026

@author: april
"""

# importing libraries
from pygame import mixer
import cv2

# displays
def show_cutscene():
    img = cv2.imread("title_april.png")
    
    img[-100:] = 0  # last 100 pixel rows are black
    img = cv2.putText(
        img,
        "Dungeon Explorer",
        org=(300, 490),  # x/y position of the text
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=3,
        color=(255, 255, 255),  # white
        thickness=2,
    )
    
    cv2.imshow("Cutscene", img)
    
    mixer.music.load("worldmap_theme.mp3")
    mixer.music.play(-1)
    
    # checks for space button to be pressed
    while True:
        key = cv2.waitKey(30) # checks for a key being pressed every 30 mS
                
        if key == 32:
            break
    
    # closes screen and stops music
    cv2.destroyWindow("Cutscene")
    mixer.music.stop()
    
    return True