#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 14:21:39 2026

@author: april
"""
# import libraries
import numpy as np
from pydantic import BaseModel
import cv2
import os
from pygame import mixer

# constants as pixels
SCREEN_SIZE_X, SCREEN_SIZE_Y = 700, 400
TILE_SIZE = 128

# shop defenitions
shop_item = ["water_breathing", "fire_potion", "mushroom_soup", "sword"]
item_descriptions = {"water_breathing": "Allows breathing underwater", "fire_potion": "Allows walking on lava", "mushroom_soup": "+2 lives", "sword":"kills giants and trolls" }
item_costs = {"water_breathing": "4", "fire_potion": "2", "mushroom_soup": "2", "sword": "3"}

# define class
class Shop(BaseModel):
    size: int
    items: list[str]
    frame_x: int
    x: int
    y: int
    status: str = "shopping"

def read_image(filename: str) -> np.ndarray:
    """
    Reads an image from the given filename and doubles its size.
    If the image file does not exist, an error is created.
    """
    img = cv2.imread(filename)  # sometimes returns None
    if img is None:
        raise IOError(f"Image not found: '{filename}'")
    img = np.kron(img, np.ones((3, 3, 1), dtype=img.dtype))  # double image size
    return img

TILE_PATH = os.path.split(__file__)[0] + '/tiles'

def read_images():
    return {
        filename[:-4]: read_image(os.path.join(TILE_PATH, filename))
        for filename in os.listdir(TILE_PATH)
        if filename.endswith(".png")
    }

def draw_tile(frame, x, y, image, xbase=0, ybase=0):
    # calculate screen position in pixels
    xpos = xbase + x * TILE_SIZE
    ypos = ybase + y * TILE_SIZE
    # copy the image to the screen
    frame[ypos : ypos + TILE_SIZE, xpos : xpos + TILE_SIZE] = image

def draw_tile(frame, x, y, image, xbase=0, ybase=0, scale=1.0):
    # Resize the image based on the scale factor
    if scale != 1.0:
        width = int(image.shape[1] * scale)
        height = int(image.shape[0] * scale)
        image = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

    # calculate screen position in pixels
    xpos = xbase + x * TILE_SIZE
    ypos = ybase + y * TILE_SIZE

    # determine the placement (centered)
    x_offset = (TILE_SIZE - image.shape[1]) // 2
    y_offset = (TILE_SIZE - image.shape[0]) // 2

    # copy the scaled image to the screen
    frame[ypos + y_offset : ypos + y_offset + image.shape[0],
          xpos + x_offset : xpos + x_offset + image.shape[1]] = image

def handle_keyboard():
    """keys are mapped to move commands"""
    key = chr(cv2.waitKey(1) & 0xFF)
    MOVES = {
    "a": "left",
    "d": "right",
    "x": "exit",
    "b": "buy",
    }
    if key in MOVES:
        return MOVES[key]

def shop_move(shop, move) -> None:
    # shop movement
    if move == "right":
        shop.x += 1
    elif move == "left":
        shop.x -= 1
    
def draw(game, shop, images):
    # initialize screen
    img = cv2.imread("shop_background.png")
    
    # resize and display shelves
    shelves_img = cv2.imread("shelves_shorter.png")
    resized_shelves = cv2.resize(shelves_img, (580, 300))
    img[360:660, 210:790] = resized_shelves
    
    # display text
    cv2.putText(img,
        "Welcome Traveller!",
        org=(500, 100),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=2,
        color=(255, 255, 255),
        thickness=3,
        )
    
    cv2.putText(img,
        "Press 'x' to exit shop",
        org=(650, 900),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),
        thickness=3,
        )
    
    # display coin count
    cv2.putText(img,
        str(game.coins),
        org=(1390, 130),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.5,
        color=(255, 128, 128),
        thickness=3,
        )
    # display coins
    draw_tile(img, xbase=1300, ybase=50,x=1,y=0, image=images[("coin")])
    
    # display inventory
    cv2.putText(img,
        "Inventory:",
        org=(1100, 690),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1,
        color=(255, 255, 255),
        thickness=3,
        )
    
    # display inventory items
    for i, item in enumerate(game.items):
        y = i // 4  # floor division: rounded down
        x = i % 4   # modulo: remainder of an integer division
        image=images[item]
        image_resized = cv2.resize(image, (80, 80))
        draw_tile(img, xbase=1070, ybase=700, x=x, y=y, image= image_resized)
    
    # displays for shop items
    for x, item in enumerate(shop.items):
        y = 3
        # display item
        draw_tile(img, x=x+2, y=y, image = images[item])
        
        # display price for item
        draw_tile(img, xbase=(x+1)*TILE_SIZE, ybase= (y+1)*TILE_SIZE ,x=1,y=0, image=images[("coin")], scale=0.7)
        cv2.putText(img,
                    str(item_costs[item]),
                    org = ((x+2)*TILE_SIZE, (y+2)*TILE_SIZE),
                    fontFace = cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale = 1,
                    color = (255, 225, 225),
                    thickness = 3,
                    )
    
        if (shop.x == x) and (shop.y == y):
           #  draw frame
            yellow = 0, 255, 255
            
            x_min = (x+2)*TILE_SIZE + 12
            x_max = (x+2)*TILE_SIZE + 97 + 12
            
            # horizontal
            img[400:405, x_min: x_max] = yellow # draws top highlight
            img[490:495, x_min: x_max] = yellow
            
            # vertical
            img[400:495, x_min : x_min + 5]  = yellow
            img[400:495, x_max : x_max + 5] = yellow
            
            # display item description
            cv2.putText(img,
                str(item_descriptions[item]),
                org=(350, 700),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=1,
                color=(255, 200, 0),
                thickness=3,
                )
           
            # display not enough coins if player doesn't have enough
            if int(game.coins) < int(item_costs[item]):
                cv2.putText(img,
                    str("not enough coins!"),
                    org=(350, 800),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 200, 250),
                    thickness=3,
                    )
                
            # display how to buy item
            else:
                cv2.putText(img,
                    str("press 'b' to buy!"),
                    org=(350, 800),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 200, 250),
                    thickness=3,
                    )
            
    cv2.imshow("shop", img)

def buy_shop(shop, game):
    for x, item in enumerate(shop.items):
        if shop.x == x:
            if int(game.coins) >= int(item_costs[item]):
                # adds item to game items and removes cost from coins
                game.items.append(shop_item[x])
                game.coins = game.coins - int(item_costs[item])
                sound_effect = mixer.Sound('coinsplash.ogg')
                sound_effect.play()
        if "mushroom_soup" in game.items:
            # adds health to player if they buy mushroom soup
            game.health += 2
            game.items.remove("mushroom_soup")

def visit_shop(game, shop):
    images = read_images()
    while shop.status == "shopping":
        draw(game, shop, images)
        move = handle_keyboard()
        if move == "right":
            shop.x += 1
        elif move == "left":
            shop.x -= 1
        elif move == "buy":
            buy_shop(shop, game)

        elif move == "exit":
            sound_effect = mixer.Sound('Cure3.wav')
            sound_effect.play()
            shop.status = "closed"
    
    cv2.destroyWindow("shop")