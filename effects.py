#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:49:37 2026

@author: april
"""
# import libraries
import numpy as np
from pydantic import BaseModel
import cv2

TILE_SIZE = 64

class Effect(BaseModel):
    x: int
    y: int
    countdown: int

    def draw(self, frame):
        pass
    
class RandomBlur(Effect):

    def draw(self, frame):
        random_tile = np.random.randint(0, 255, size=(TILE_SIZE, TILE_SIZE, 3), dtype=np.uint8)
        frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE] = random_tile

class FadeIn(Effect):

    def draw(self, frame):
        tile = frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE]
        tile[tile > (255 - self.countdown)] = 0
        frame[self.y * TILE_SIZE: self.y * TILE_SIZE + TILE_SIZE,
            self.x * TILE_SIZE: self.x * TILE_SIZE + TILE_SIZE] = tile
        
class ColorText(Effect):
    text: str
    def draw(self, frame):
        if self.countdown % 2 == 0:
            color = (255, 0, 255)
        else:
            color = (0, 255, 255)
        cv2.putText(frame,
            self.text,
            org=(self.y * TILE_SIZE, self.x * TILE_SIZE),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=color,
            thickness=2,
        )

class FlashEffectWhite(Effect):
    """Entire screen goes white, then fades to normal"""
    def draw(self, frame):
        frame[frame < self.countdown] = self.countdown

class FlashEffectRed(Effect):
    """Entire screen goes white, then fades to normal"""
    def draw(self, frame):
        red = frame[:,:,2]
        red[red < self.countdown] = self.countdown