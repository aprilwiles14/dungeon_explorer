"""
the Dungeon Explorer game logic
"""

# importing libraries
from pydantic import BaseModel
from typing import Callable
from moves import Move
from typing import Literal
import random
import time

def parse_level(level):
    return [list(row) for row in level]

# level 1 game
def start_game():
    
    return DungeonGame(
        x=18,
        y=2,
        current_level = LEVEL_ONE,
        level_number = 0
    )


# classes
class Move(BaseModel):
    tile: str
    from_x: int
    from_y: int
    speed_x: int
    speed_y: int
    progress: int = 0
    complete: bool = False
    finished: Callable = None
    
class Teleporter(BaseModel):
    x: int
    y: int
    target_x: int
    target_y: int

class Switch(BaseModel):
    x: int
    y: int
    switch_x: int
    switch_y: int
    
class Fireball(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None
    
class Explosion(BaseModel):
    x: int
    y: int
    max_frame: int = 16
    max_delay: int = 5
    delay: int = 0
    frame: int = 0
    complete: bool = False

class Skeleton(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None
    
class Giant(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None

class Box(BaseModel):
    x: int
    y: int

class Level(BaseModel):
    level: list[list[str]]
    moves: list[Move] = []
    teleporters: list[Teleporter] = []
    switch: list[Switch] = []
    fireball: list[Fireball] = []
    skeleton: list[Skeleton] = []
    giant: list[Giant] = []
    box: list[Box] = []
    last_damage_time: float = 0.0
    music: str
    
# define all possible items
Item = Literal["key", "potion", "shield"]

class DungeonGame(BaseModel):
    status: str = "running"
    x: int
    y: int
    coins: int = 0
    health: int = 5
    items: list[Item] = []
    current_level: Level
    level_number: int = 0
    explosions: list[Explosion] = []
    
# levels
LEVEL_ONE = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#.#.....#..........#",  #2
     "#....#####$$.t.t...#",  #3
     "#........###########",  #4
     "##c#t#.....#.$#k...#",  #5
     "#....#$....#.$#....#",  #6
     "#$$.k#$.f..#..#....#",  #7
     "############..D....#",  #8
     "#.t.....$#..####d###",  #9
     "#......t.d...ps..#.#",  #10
     "#........#..####.c.#",  #11
     "#x.$$t...#..$.k#p#s#",  #12
     "####################",  #13  
     ]),
    teleporters=[Teleporter(x=9, y=1, target_x=7, target_y=1),],
    switch=[Switch(x=1, y=1, switch_x=4, switch_y=11),],
    fireball = [Fireball(x=13, y=7, direction = "up"),
                Fireball(x=11, y=11, direction = "up"),
                Fireball(x=2, y=10, direction = "right")],
    skeleton = [Skeleton(x=17, y=6, direction = "left"),],
    giant = [Giant(x=7, y=11, direction = "right"),],
    
    music = "dungeon_theme.mp3"
)

LEVEL_TWO = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#..................#",  #2
     "#..................#",  #3
     "#..................#",  #4
     "#..................#",  #5
     "#..................#",  #6
     "#..................#",  #7
     "#..................#",  #8
     "#..................#",  #9
     "#..................#",  #10
     "#..................#",  #11
     "#..................#",  #12
     "####################",  #13  
     ]),
    box = [Box(x=3,y=3)],
    
    music = "grasslands_theme.mp3"
)

LEVELS = [LEVEL_ONE, LEVEL_TWO]

# function to take damage unless shield present. <0 lives = game over
def take_damage(game: DungeonGame) -> None:
    if "shield" in game.items:
        game.items.remove("shield")
    else:
        game.health -= 1
    if game.health <= 0:
        game.status = "game over"
        
# function to add health to player with maximum of 5 lives
def add_health(game):
    if game.health <5:
        game.health += 1

# function to check enemy collision with player
def check_collision(game):
    current_time = time.time()
    
    for fireball in game.current_level.fireball:
        if fireball.x == game.x and fireball.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            game.current_level.last_damage_time = current_time
            explosion_x = fireball.x
            explosion_y = fireball.y
            game.explosions.append(Explosion(x=explosion_x,y=explosion_y))
            take_damage(game)
            
    for skeleton in game.current_level.skeleton:
        if skeleton.x == game.x and skeleton.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
    
    # giant takes 2 lives
    for giant in game.current_level.giant:
        if giant.x == game.x and giant.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            take_damage(game)
        
# function to get next position of fireballs
def get_next_position(x, y, direction):
    if direction == "right":
        x += 1
    elif direction == "left":
        x -= 1
    elif direction == "down":
        y += 1
    elif direction == "up":
        y -= 1
    
    return x, y

# function to define speed of enemies depending on direction
def enemy_speed(direction):
    speed_x = 0
    speed_y = 0
    if direction == "right":
        speed_x = 2
        speed_y = 0
    elif direction == "left":
        speed_x = -2
        speed_y = 0
    elif direction == "up":
        speed_x = 0
        speed_y = -2
    elif direction == "down":
        speed_x = 0
        speed_y = 2
    
    return speed_x, speed_y

# function to move fireballs
def move_fireball(game, fireball):
    
    new_x, new_y = get_next_position(fireball.x, fireball.y, fireball.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kp":  # flies over coins and keys
        fire_x, fire_y = enemy_speed(fireball.direction)
        fireball.move = Move(
            tile = "fireball",
            from_x = fireball.x, 
            from_y = fireball.y,
            speed_x = fire_x, speed_y = fire_y
            )
        game.current_level.moves.append(fireball.move)
    
        fireball.x = new_x
        fireball.y = new_y
        
    elif fireball.direction == "right":
        fireball.direction = "left"
    elif fireball.direction == "up":
        fireball.direction = "down"
    elif fireball.direction == "down":
         fireball.direction = "up"
    elif fireball.direction == "left":
         fireball.direction = "right"

# function to move skeleton randomly
def move_skeleton(game, skeleton):  # called by update!
    skeleton.direction = random.choice(["up", "down", "left", "right"])
    
    new_x, new_y = get_next_position(skeleton.x, skeleton.y, skeleton.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kp":  # flies over coins and keys
        skeleton_x, skeleton_y = enemy_speed(skeleton.direction)
        skeleton.move = Move(
            tile = "skeleton",
            from_x = skeleton.x, 
            from_y = skeleton.y,
            speed_x = skeleton_x, speed_y = skeleton_y
            )
        game.current_level.moves.append(skeleton.move)
    
        skeleton.x = new_x
        skeleton.y = new_y
         
    # changes direction when skeleton runs into something unpassable
    elif skeleton.direction == "right":
        skeleton.direction = "left"
    elif skeleton.direction == "up":
        skeleton.direction = "down"
    elif skeleton.direction == "down":
         skeleton.direction = "up"
    elif skeleton.direction == "left":
         skeleton.direction = "right"
    

def move_giant(game, giant):  # called by update!
    giant.direction = random.choice(["up", "down", "left", "right"])
    
    new_x, new_y = get_next_position(giant.x, giant.y, giant.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kp":  # flies over coins and keys
        giant_x, giant_y = enemy_speed(giant.direction)
        giant.move = Move(
            tile = "giant",
            from_x = giant.x, 
            from_y = giant.y,
            speed_x = giant_x, speed_y = giant_y
            )
        game.current_level.moves.append(giant.move)
    
        giant.x = new_x
        giant.y = new_y
    
    # changes direction when giant runs into something unpassable
    elif giant.direction == "right":
        giant.direction = "left"
    elif giant.direction == "up":
        giant.direction = "down"
    elif giant.direction == "down":
         giant.direction = "up"
    elif giant.direction == "left":
         giant.direction = "right"

    
# updates game
def update(game):
    for fireball in game.current_level.fireball:
        if fireball.move == None or fireball.move.complete:
            move_fireball(game, fireball)
    for skeleton in game.current_level.skeleton:
        if skeleton.move == None or skeleton.move.complete:
            move_skeleton(game, skeleton)
    for giant in game.current_level.giant:
        if giant.move == None or giant.move.complete:
            move_giant(game, giant)
    
    check_collision(game)


def can_box_move(game, x, y, direction) -> bool:
    next_x, next_y = get_next_position(x, y, direction)

    # wall?
    if game.current_level.level[next_y][next_x] == "#":
        return False
    
    # another box?
    for box in game.current_level.box:
        if box.x == next_x and box.y == next_y:
            return False
    
    return True

def get_box_at(game, x, y):
    for box in game.current_level.box:
        if box.x == x and box.y == y:
            return box
    return None

def can_player_move(game, x, y, direction) -> bool:
    next_x, next_y = get_next_position(x, y, direction)
    
    # wall
    if game.current_level.level[next_y][next_x] == "#":
        return False
    
    # box
    box = get_box_at(game, next_x, next_y)
    if box is not None:
        return can_box_move(game, next_x, next_y, direction)
    
    return True

# function to move player
def move_player(game: DungeonGame, direction: str) -> None:
    """Things that happen when the player walks on stuff"""
    
    new_x = game.x
    new_y = game.y

    # player movement
    if direction == "right":
        new_x += 1
    elif direction == "left":
        new_x -= 1
    elif direction == "down":
        new_y += 1
    elif direction == "up":
        new_y -= 1
    
 #   new_x, new_y = get_next_position(game.x game.y, direction)
    box = get_box_at(game, new_x, new_y)
    
    if box is not None:
        # player is trying to push a box
        if not can_box_move(game, box.x, box.y, direction):
            return
        
        # move box one tile
        box.x, box.y = get_next_position(box.x, box.y, direction)
    
    
    # when player steps on stairs, level increases
    if game.current_level.level[new_y][new_x] == "x":
        game.level_number += 1
        if game.level_number < len(LEVELS):
        # move to next level
            game.current_level = LEVELS[game.level_number]
        else:
        # no more levels left
            game.status = "finished"
    
    # collect coins
    if game.current_level.level[new_y][new_x] == "$":
        game.current_level.level[new_y][new_x] = "."
        game.coins += 1
    
    # traps
    if game.current_level.level[new_y][new_x] == "t":
        game.current_level.level[new_y][new_x] = "."
        take_damage(game)
    
    # teleporters
    for t in game.current_level.teleporters:
        if game.x == t.x and game.y == t.y:
            game.x = t.target_x
            game.y = t.target_y
    
    # collect keys
    if game.current_level.level[new_y][new_x] == "k":
        game.items.append("key")
        game.current_level.level[new_y][new_x] = "."
    
    # health potion
    if game.current_level.level[new_y][new_x] == "p":
        game.current_level.level[new_y][new_x] = "."
        add_health(game)
    
    # shields
    if game.current_level.level[new_y][new_x] == "s":
        game.items.append("shield")
        game.current_level.level[new_y][new_x] = "."
    
    # open doors
    if "key" in game.items and game.current_level.level[new_y][new_x] == "d":  # check whether there is a door
        game.items.remove("key")           # key can be used once
        game.current_level.level[new_y][new_x] = "D"     # replace the closed door by an open one
    
    # secret doors
    if game.current_level.level[new_y][new_x] == "c":
        game.current_level.level[new_y][new_x] = "."
    
    # switches
    for s in game.current_level.switch:
        if game.x == s.x and game.y == s.y:
            game.current_level.level[4][11] = "d"
    
    # move player smoothly
    if game.current_level.level[new_y][new_x] in ".Dc":

        if direction == "left":
            move = Move(tile="player",
                        from_x=game.x, from_y=game.y,
                        speed_x = -4, speed_y = 0, finished = player_move_finished
                        )
            game.current_level.moves.append(move)
            
        elif direction == "right":
            move = Move(tile="player",
                        from_x=game.x, from_y=game.y,
                        speed_x = 4, speed_y = 0, finished = player_move_finished
                        )
            game.current_level.moves.append(move)
    
        elif direction == "down":
           move = Move(tile="player",
                       from_x=game.x, from_y=game.y,
                       speed_x = 0, speed_y = 4, finished = player_move_finished
                       )
           game.current_level.moves.append(move)
           
        elif direction == "up":
            move = Move(tile="player",
                        from_x=game.x, from_y=game.y,
                        speed_x = 0, speed_y = -4, finished = player_move_finished
                        )
            game.current_level.moves.append(move)

        game.x = new_x
        game.y = new_y
      
    # check player collision with enemies
    check_collision(game)

# testing prints
def player_move_finished(game):
    """outputs the coordinates of the player"""
    print(game.x, game.y)
