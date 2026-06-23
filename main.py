"""
graphics engine for 2D games
"""
# import libraries
import os
import numpy as np
import cv2
from game import start_game, move_player
from game import update
import game
from pygame import mixer

TILE_PATH = os.path.split(__file__)[0] + '/tiles'

# title of the game window
GAME_TITLE = "Dungeon Explorer"

# map keyboard keys to move commands
MOVES = {
    "a": "left",
    "d": "right",
    "w": "up",
    "s": "down",
    " ": "start",
    "m": "mushroom_soup"
}


# constants measured in pixels
SCREEN_SIZE_X, SCREEN_SIZE_Y = 850, 416
TILE_SIZE = 32

def read_image(filename: str) -> np.ndarray:
    """
    Reads an image from the given filename and doubles its size.
    If the image file does not exist, an error is created.
    """
    img = cv2.imread(filename)  # sometimes returns None
    if img is None:
        raise IOError(f"Image not found: '{filename}'")
   # img = np.kron(img, np.ones((2, 2, 1), dtype=img.dtype))  # double image size
    return img


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

def draw_move(frame, move, images):
    draw_tile(frame, x=move.from_x, y=move.from_y, image=images[move.tile], xbase=move.progress * move.speed_x, ybase=move.progress * move.speed_y)
    move.progress += 1

def clean_moves(game, moves):
    result = []
    for m in moves:
        if m.progress * max(abs(m.speed_x), abs(m.speed_y)) < TILE_SIZE:
            result.append(m)
        else:
            m.complete = True
            if m.finished is not None:
                m.finished(game)
    return result

def is_player_moving(game, moves):
    return any([m for m in moves if m.tile == game.character])

SYMBOLS = {".": "floor", "#": "wall", "f": "fountain", "x": "stairs_down", \
           "$": "coin", "t": "trap", "c": "cracked_wall", "k": "key", "D": \
               "open_door", "d": "closed_door", "p": "potion", "s":"shield", \
                   "explosion": "explosion_pixelfield", "S": "enter_shop" , \
                   "i": "slime", "w": "water", "l":"lava_old", "b": "posion", \
                       "W": "portal", "o": "crystal_wall_2", "y": "crystal_wall_3",\
                           "v": "pedestal_full", "F": "wandering_mushroom_new"}
# displays
def draw(game, images, moves):
    # initialize screen
    frame = np.zeros((SCREEN_SIZE_Y, SCREEN_SIZE_X, 3), np.uint8)
    
    # draw dungeon tiles
    for y, row in enumerate(game.current_level.level):
        for x, tile in enumerate(row):
            draw_tile(frame, x=x, y=y, image = images[SYMBOLS[tile]])
        
    # draw teleporters
    for t in game.current_level.teleporters:
        draw_tile(frame, x=t.x, y = t.y, image = images["teleporter"])
    
    # draw switches
    for s in game.current_level.switch:
        draw_tile(frame, x=s.x, y = s.y, image = images["slot"])
    
    # draw boxes
    for b in game.current_level.box:
        draw_tile(frame, x=b.x, y = b.y, image = images["wooden_box"])
    
    # draw explotions
    for explosion in game.explosions:
        if not explosion.complete:
            draw_explosion(frame, explosion, images)
    
    game.explosions = [e for e in game.explosions if not e.complete]
    
    # draw special effects
    for e in game.effects:
        e.draw(frame)
        
    ### DISPLAYS
    
    # display level:
    cv2.putText(frame,
        f"Level {game.level_number + 1}",
        org=(650, 30),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.9,
        color=(255, 255, 255),
        thickness=3,
        )
    
    # display coin count
    cv2.putText(frame,
        str(game.coins),
        org=(690, 80),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.5,
        color=(255, 128, 128),
        thickness=3,
        )
    draw_tile(frame, xbase=620, ybase=50,x=1,y=0, image=images[("coin")])
        
    # display life count
    cv2.putText(frame,
        str("lives left:"),
        org=(650, 130),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.9,
        color=(255, 255, 255),
        thickness=3,
        )
    
    # display hearts
    for i in range(game.health):
        draw_tile(frame, xbase=650, ybase=140, x=i, y=0, image=images[("heart")])
        
    # hints for level 4
    if game.level_number == 3:
        # display life count
        cv2.putText(frame,
            str("hint: poision"),
            org=(650, 375),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.8,
            color=(0, 128, 0),
            thickness=3,
            )
    if game.level_number == 3:
        # display life count
        cv2.putText(frame,
            str("kills trolls!"),
            org=(650, 400),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=0.8,
            color=(0, 128, 0),
            thickness=3,
            )
    
    # display inventory text
    cv2.putText(frame,
        str("Inventory:"),
        org=(650, 220),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.8,
        color=(255, 255, 255),
        thickness=3,
        )
         
    # display inventory items
    for i, item in enumerate(game.items):
        y = i // 4  # floor division: rounded down
        x = i % 4   # modulo: remainder of an integer division
        image=images[item]
        image_resized = cv2.resize(image, (TILE_SIZE, TILE_SIZE))
        draw_tile(frame, xbase=660, ybase=230, x=x, y=y, image= image_resized)

    # draw player
    while game.current_level.moves:
        moves.append(game.current_level.moves.pop()) 
    if not is_player_moving(game, moves):
        draw_tile(frame=frame, x=game.x, y=game.y, image=images[game.character])
    
    # draw everything that moves
    for m in moves:
        draw_move(frame=frame, move=m, images=images)

    # display complete image
    cv2.imshow(GAME_TITLE, frame)

# fireball explosion function
def draw_explosion(frame, explosion, images):
    if "explosion" not in images:
        print("error: 'explosion' images not loaded")
        return
    
    framex = explosion.frame % 4
    framey = explosion.frame // 4
    tile = images["explosion"][framey * TILE_SIZE:(framey + 1) * TILE_SIZE,
                               framex * TILE_SIZE:(framex + 1) * TILE_SIZE]
    draw_tile(frame, x=explosion.x, y=explosion.y, image=tile)

    # delay between frames
    explosion .delay += 1
    if explosion.delay >= explosion.max_delay:
        explosion.delay = 0
        explosion.frame += 1
    
    # Mark complete when all frames have played
    if explosion.frame >= explosion.max_frame:
        explosion.complete = True

def handle_keyboard(key):
    """keys are mapped to move commands"""
    key = chr(cv2.waitKey(1) & 0xFF)
    if key == "q":
        game.current_level.status = "exited"
    return MOVES.get(key) 

def main():
    # import music
    mixer.init()
    
    # show cutscene
    from cutscene import show_cutscene
    if not show_cutscene():
        return
    
    # read images
    images = read_images()
    images["explosion"] = read_image("tiles/animation/explosion_pixelfield.png") #[::2,::2]
    
    # start game
    game = start_game()
     
    # play music
    current_music = game.current_level.music
    mixer.music.load(current_music)
    mixer.music.play(-1)
    
    # display moves
    queued_move = None
    moves = []
    
    # while game runs
    while game.status == "running":
        
        # display levels, moves, updates
        draw(game, images, moves)
        moves = clean_moves(game, moves)
        queued_move = handle_keyboard(game)
        update(game)
        
        #  check for level change
        if game.current_level.music != current_music:
            current_music = game.current_level.music
            mixer.music.load(current_music)
            mixer.music.play(-1)
        
        # player move
        if not is_player_moving(game, moves) and queued_move:
            move_player(game, queued_move)
         
        # check for game victory
        new_y = game.y
        new_x = game.x
        if game.current_level.level[new_y][new_x] == "F":
            game.status == "win"
            break
        
    # display winning screen
    if game.status == "win":
        img = cv2.imread("victory.png")
        
        cv2.putText(img,
            "Press 'space' to exit",
            org=(650, 900),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=3,
            )
        
        mixer.music.load("victory.ogg")
        mixer.music.play(-1)
        
        cv2.imshow(GAME_TITLE, img)
    
    # display losing screen
    elif game.status == "game over":
        img = cv2.imread("loser.png")
        
        cv2.putText(img,
            "Press 'space' to exit",
            org=(650, 900),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(255, 255, 255),
            thickness=3,
            )
        
        mixer.music.load("loser.mp3")
        mixer.music.play(-1)
        
        cv2.imshow(GAME_TITLE, img)
    
    # screens close when space is pressed
    while True:
        key = cv2.waitKey(30) # checks for a key being pressed every 30 mS
                
        if key == 32:
            break

    # closes all windows and stops music
    cv2.destroyAllWindows()
    mixer.music.stop()

if __name__ == '__main__':
    main()

        
