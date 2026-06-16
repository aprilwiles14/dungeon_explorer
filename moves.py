#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  8 09:56:18 2026

@author: april
"""

from typing import Callable
from pydantic import BaseModel

class Move(BaseModel):
    tile: str
    from_x: int
    from_y: int
    speed_x: int
    speed_y: int
    progress: int = 0
    complete: bool = False
    finished: Callable = None