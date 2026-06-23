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
from effects import Effect
from effects import FlashEffectWhite
from effects import FlashEffectRed
from shop import visit_shop
from shop import Shop
from pygame import mixer
from wardrobe import visit_wardrobe
from wardrobe import Wardrobe


def parse_level(level):
    return [list(row) for row in level]

# starts game
def start_game():
    
    return DungeonGame(
        x=18,
        y=1,
        current_level = LEVEL_ONE,
        level_number = 0,
    )

# classes defintions
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

class Troll(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None

class Snake(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None
    
class Giant(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None
    
class Water_nymph(BaseModel):
    x: int
    y: int
    direction: str
    move: Move = None

class Box(BaseModel):
    x: int
    y: int

class DisappearingTile(BaseModel):
    x: int
    y: int
    time_step: float

class Level(BaseModel):
    level: list[list[str]]
    moves: list[Move] = []
    teleporters: list[Teleporter] = []
    switch: list[Switch] = []
    fireball: list[Fireball] = []
    skeleton: list[Skeleton] = []
    giant: list[Giant] = []
    box: list[Box] = []
    snake: list[Snake] = []
    troll: list[Troll] = []
    last_damage_time: float = 0.0
    music: str
    water_nymph: list[Water_nymph] = []
    disappearing: list[DisappearingTile] = []
    
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
    effects: list[Effect] = []
    character: str = "player"


# level setouts
LEVEL_ONE = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#.#.....#..........#",  #2
     "#.......#....t.....#",  #3
     "#.......############",  #4
     "##c#t#.....#..#k...#",  #5
     "#....#.....#.$#...$#",  #6
     "#$$W.#..f..#..#....#",  #7
     "############..D....#",  #8
     "#.t$....#...####d###",  #9
     "#.....t.d........#.#",  #10
     "###.....#...####.c.#",  #11
     "#xd..t..#S..$.k#p#s#",  #12
     "####################",  #13  
     ]),
    teleporters=[Teleporter(x=9, y=1, target_x=7, target_y=1),],
    switch=[Switch(x=1, y=1, switch_x=11, switch_y=4),],
    fireball = [Fireball(x=13, y=7, direction = "up"),
                Fireball(x=11, y=11, direction = "up"),
                Fireball(x=2, y=10, direction = "right")],
    skeleton = [Skeleton(x=17, y=6, direction = "left"),],
    giant = [Giant(x=7, y=11, direction = "right"),],
    box = [Box(x=4,y=2)],
    
    music = "dungeon_theme.mp3"
)

LEVEL_TWO = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#W$........#$.#....#",  #2
     "####.#.######.#.#k.#",  #3
     "#S.#.#.#$#.d.....#.#",  #4
     "##.....#$#.#.......#",  #5
     "##..##.#c#.#.#..#..#",  #6
     "#..........#...#...#",  #7
     "#.############d#####",  #8
     "#.t...t....#.......#",  #9
     "#...t...t..#.......#",  #10
     "#########.##.......#",  #11
     "#..........#......x#",  #12
     "####################",  #13  
     ]),
    box = [Box(x=3,y=11),
           Box(x=3,y=5)],
    skeleton = [Skeleton(x=14, y=5, direction = "left"),
                Skeleton(x=17, y=2, direction = "left")],
    switch=[Switch(x=10, y=1, switch_x=11, switch_y=3),],
    fireball = [Fireball(x=12, y=8, direction = "left"),
                Fireball(x=12, y=9, direction = "right"),
                Fireball(x=12, y=11, direction = "left")],
    
    music = "grasslands_theme.mp3"
)
LEVEL_THREE = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#x...#www#w#w#www#p#",  #2
     "#....#ww##wwwww#kww#",  #3
     "#....#w#wwww#ww#ww##",  #4
     "#..f.#www##wwwww##w#",  #5
     "#..###w#ww#ww##wwww#",  #6
     "#s.#..w#w##www#w#w##",  #7
     "#..#.#wwwp##wwwwwww#",  #8
     "##d#.###############",  #9
     "S..t.#...$.....$..W#",  #10
     "#t.t.d.............#",  #11
     "#$.c.#......$......#",  #12
     "####################",  #13  
     ]),
    teleporters=[Teleporter(x=8, y=1, target_x=18, target_y=11),],
    fireball = [Fireball(x=15, y=10, direction = "up"),
                Fireball(x=12, y=11, direction = "down"),
                Fireball(x=9, y=10, direction = "up")],
    box = [Box(x=17,y=11)],
    switch=[Switch(x=6, y=11, switch_x=5, switch_y=10),],
    water_nymph = [Water_nymph(x=9,y=3, direction = 'left'),
                   Water_nymph(x=15,y=6, direction = 'right'),
                   Water_nymph(x=16,y=3, direction = 'up')],
    skeleton = [Skeleton(x=3, y=3, direction = "left")],
    
    music = "mushroom_theme.mp3"
)

LEVEL_FOUR = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#.i.iii$i.iikii.ii$#",  #2
     "#.i.i.ii..iiiii.$.i#",  #3
     "#iii$iii.i.i.i.i...#",  #4
     "#i.ii.ii..iii..iii.#",  #5
     "############d#####S#",  #6
     "#...p.........W#...#",  #7
     "##d#############c#c#",  #8
     "#i.i.i.#...#...c.#.#",  #9
     "#.ii...#.#...#.#####",  #10
     "#i...i.d....#...#..#",  #11
     "#.i.i..#..#...#.#.x#",  #12
     "####################",  #13  
     ]),
    teleporters=[Teleporter(x=18, y=8, target_x=17, target_y=10)],
    fireball = [Fireball(x=4, y=1, direction = "down"),
                Fireball(x=7, y=4, direction = "up"),
                Fireball(x=12, y=2, direction = "up"),
                Fireball(x=16, y=3, direction = "up")],
    skeleton = [Skeleton(x=13, y=10, direction = "left")],
    switch=[Switch(x=1, y=6, switch_x=2, switch_y=7),],
    box = [Box(x=9,y=6)],
    snake = [Snake(x=12, y=6,direction = "left")],
    troll = [Troll(x=5, y=10, direction = "left")],
    music = "strange_dungeon.wav"
)

LEVEL_FIVE = Level(
    level = parse_level([
      #12345678901234567890   
     "####################",  #1
     "#WS.#llllllllllll#F#",  #2
     "#...#llll$lllllll#.#",  #3
     "#...Dllllllllllll#d#",  #4
     "#...#lllllllll$llll#",  #5
     "#...#llllll$lllllll#",  #6
     "#d##################",  #7
     "#ylykytyy$yly$tlll#",  #8
     "#yltlyllollyyylyytl#",  #9
     "#yl$yyytyllylylllyl#",  #10
     "#yylolololyotyyyyyl#",  #11
     "#lyyylyyyyyll$lllyo#",  #12
     "####################",  #13
     ]),
    
    fireball = [
                Fireball(x=6, y=4, direction = "up"),
                Fireball(x=7, y=3, direction = "up"),
                Fireball(x=8, y=1, direction = "down"),
                Fireball(x=10, y=3, direction = "up"),
                Fireball(x=11, y=3, direction = "down"),
                Fireball(x=13, y=1, direction = "up"),
                Fireball(x=14, y=1, direction = "down"),],
    giant = [Giant(x=9, y=3, direction = "left")],
    teleporters=[Teleporter(x=18, y=5, target_x=1, target_y=2)],
                
    
    music = "lava_dungeon.ogg"
)


LEVELS = [LEVEL_ONE, LEVEL_TWO, LEVEL_THREE, LEVEL_FOUR, LEVEL_FIVE]

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
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('lava.flac')
            sound_effect.play()

            
    for skeleton in game.current_level.skeleton:
        if skeleton.x == game.x and skeleton.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('hurt_03.mp3')
            sound_effect.play()
    
    for snake in game.current_level.snake:
        if snake.x == game.x and snake.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            if 'sword' in game.items:
                snake_y = snake.y
                snake_x = snake.x
                game.current_level.level[snake_y][snake_x + 1] = "b"
                game.items.remove('sword')
                game.current_level.snake.remove(snake)
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('hurt_03.mp3')
            sound_effect.play()
    
    # giant takes 2 lives
    for giant in game.current_level.giant:
        if giant.x == game.x and giant.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            if 'sword' in game.items:
                giant_y = giant.y
                giant_x = giant.x
                game.current_level.level[giant_y -1][giant_x + 1] = "k"
                game.items.remove('sword')
                game.current_level.giant.remove(giant)
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            take_damage(game)
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('hurt_03.mp3')
            sound_effect.play()
    
    for troll in game.current_level.troll:
        if troll.x == game.x and troll.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            if 'posion' in game.items:
                troll_y = troll.y
                troll_x = troll.x
                game.current_level.level[troll_y][troll_x + 1] = "k"
                game.items.remove('posion')
                game.current_level.troll.remove(troll)
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            take_damage(game)
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('hurt_03.mp3')
            sound_effect.play()
            
    for nymph in game.current_level.water_nymph:
        if nymph.x == game.x and nymph.y == game.y:
            if current_time - game.current_level.last_damage_time < 1.0:
                return
            game.current_level.last_damage_time = current_time
            take_damage(game)
            take_damage(game)
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('hurt_03.mp3')
            sound_effect.play()
    
    # player drowns in water unless they have water breathing in items
    player_y = game.y
    player_x = game.x
    while game.current_level.level[player_y][player_x] == "w":
        if current_time - game.current_level.last_damage_time < 2.0:
            return
        if "water_breathing" in game.items:
            return
        else: 
            game.current_level.last_damage_time = current_time
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            take_damage(game)
            
    # player dies in lava unless they have fire potion
    while game.current_level.level[player_y][player_x] == "l":
        if current_time - game.current_level.last_damage_time < 2.0:
            return
        if "fire_potion" in game.items:
            return
        else: 
            game.current_level.last_damage_time = current_time
            game.effects.append(FlashEffectRed(x=8, y=1, countdown=100))
            take_damage(game)
    
    # tiles disappear 2 seconds after stepping on them
    for d in game.current_level.disappearing:
        time_on_tile = time.time() - d.time_step
        if time_on_tile > 2.5:
            game.current_level.level[d.y][d.x] = "l"
            
        
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
    
    if game.current_level.level[new_y][new_x] in ".$kpil":  # flies over coins and keys
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
    
    if game.current_level.level[new_y][new_x] in ".$kpilw":  # flies over coins and keys
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

# function to move snake
def move_snake(game, snake):
    
    new_x, new_y = get_next_position(snake.x, snake.y, snake.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kpi":  # flies over coins and keys
        snake_x, snake_y = enemy_speed(snake.direction)
        snake.move = Move(
            tile = "snake",
            from_x = snake.x, 
            from_y = snake.y,
            speed_x = snake_x, speed_y = snake_y
            )
        game.current_level.moves.append(snake.move)
    
        snake.x = new_x
        snake.y = new_y
        
    elif snake.direction == "right":
        snake.direction = "left"
    elif snake.direction == "up":
        snake.direction = "down"
    elif snake.direction == "down":
         snake.direction = "up"
    elif snake.direction == "left":
         snake.direction = "right"

# function to move troll randomly
def move_troll(game, troll):  # called by update!
    troll.direction = random.choice(["up", "down", "left", "right"])
    
    new_x, new_y = get_next_position(troll.x, troll.y, troll.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kilwp":  # flies over coins and keys
        troll_x, troll_y = enemy_speed(troll.direction)
        troll.move = Move(
            tile = "troll",
            from_x = troll.x, 
            from_y = troll.y,
            speed_x = troll_x, speed_y = troll_y
            )
        game.current_level.moves.append(troll.move)
    
        troll.x = new_x
        troll.y = new_y
         
    # changes direction when snake runs into something unpassable
    elif troll.direction == "right":
        troll.direction = "left"
    elif troll.direction == "up":
        troll.direction = "down"
    elif troll.direction == "down":
         troll.direction = "up"
    elif troll.direction == "left":
         troll.direction = "right"
    
# function to move giant randomly
def move_giant(game, giant):  # called by update!
    giant.direction = random.choice(["up", "down", "left", "right"])
    
    new_x, new_y = get_next_position(giant.x, giant.y, giant.direction)
    
    if game.current_level.level[new_y][new_x] in ".$kilwp":  # flies over coins and keys
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

# function to move nymph randomly
def move_nymph(game, nymph):  # called by update!
    nymph.direction = random.choice(["up", "down", "left", "right"])
    
    new_x, new_y = get_next_position(nymph.x, nymph.y, nymph.direction)
    
    if game.current_level.level[new_y][new_x] in "$kilwp":  # flies over coins and keys
        nymph_x, nymph_y = enemy_speed(nymph.direction)
        nymph.move = Move(
            tile = "water_nymph",
            from_x = nymph.x, 
            from_y = nymph.y,
            speed_x = nymph_x, speed_y = nymph_y
            )
        game.current_level.moves.append(nymph.move)
    
        nymph.x = new_x
        nymph.y = new_y
    
    # changes direction when giant runs into something unpassable
    elif nymph.direction == "right":
        nymph.direction = "left"
    elif nymph.direction == "up":
        nymph.direction = "down"
    elif nymph.direction == "down":
         nymph.direction = "up"
    elif nymph.direction == "left":
         nymph.direction = "right"

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
    for snake in game.current_level.snake:
        if snake.move == None or snake.move.complete:
            move_snake(game, snake)
    for troll in game.current_level.troll:
        if troll.move == None or troll.move.complete:
            move_troll(game, troll)
    for nymph in game.current_level.water_nymph:
        if nymph.move == None or nymph.move.complete:
            move_nymph(game, nymph)
    for effect in game.effects:
        update_effects(game)
    
    check_collision(game)

# function to display effects
def update_effects(game):
    new_effects = []

    # add a loop that decreases the countdown for all effects
    for effect in game.effects:
        effect.countdown -= 1 
        if effect.countdown > 0:
            new_effects.append(effect)

    game.effects = new_effects

# function to see if the pushable box is able to move
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

# finds location of box
def get_box_at(game, x, y):
    for box in game.current_level.box:
        if box.x == x and box.y == y:
            return box
    return None

# checks for walls or boxes
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
    
    speed_x = 4
    speed_y = 4
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
    
    # box movement
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
        sound_effect = mixer.Sound('coinsplash.ogg')
        sound_effect.play()
    
    # traps do damage
    if game.current_level.level[new_y][new_x] == "t":
        game.current_level.level[new_y][new_x] = "."
        take_damage(game)
        sound_effect = mixer.Sound('hurt_03.mp3')
        sound_effect.play()
    
    # teleporters
    for t in game.current_level.teleporters:
        if game.x == t.x and game.y == t.y:
            game.x = t.target_x
            game.y = t.target_y
            game.effects.append(FlashEffectWhite(x=8, y=1, countdown=100))
            sound_effect = mixer.Sound('Cure2.wav')
            sound_effect.play()
    
    # collect keys
    if game.current_level.level[new_y][new_x] == "k":
        game.items.append("key")
        game.current_level.level[new_y][new_x] = "."
        sound_effect = mixer.Sound('key.flac')
        sound_effect.play()
    
    # collect posion
    if game.current_level.level[new_y][new_x] == "b":
        game.items.append("posion")
        game.current_level.level[new_y][new_x] = "."
        sound_effect = mixer.Sound('bubbles.wav')
        sound_effect.play()
    
    # health potion
    if game.current_level.level[new_y][new_x] == "p":
        game.current_level.level[new_y][new_x] = "."
        add_health(game)
        sound_effect = mixer.Sound('Cure7.wav')
        sound_effect.play()
    
    # shields
    if game.current_level.level[new_y][new_x] == "s":
        game.items.append("shield")
        game.current_level.level[new_y][new_x] = "."
        sound_effect = mixer.Sound('Cure4.wav')
        sound_effect.play()
    
    # slime slows player down
    if game.current_level.level[new_y][new_x] == "i":
        # insert code to make player slower on slime here
        speed_x = 2
        speed_y = 2
    
    # shop enter
    if game.current_level.level[new_y][new_x] == "S":
        from shop import shop_item
        shop = Shop(size=600,items= shop_item, frame_x = 0, x=0, y= 3, status = "shopping")
        visit_shop(game, shop)
        sound_effect = mixer.Sound('Cure4.wav')
        sound_effect.play()
    
    # wardrobe enter
    if game.current_level.level[new_y][new_x] == "W":
        from wardrobe import wardrobe_item
        wardrobe = Wardrobe(size=600,items= wardrobe_item, frame_x = 0, x=1, y= 3, status = "open")
        visit_wardrobe(game, wardrobe)
        sound_effect = mixer.Sound('Cure4.wav')
        sound_effect.play()
    
    # open doors
    if "key" in game.items and game.current_level.level[new_y][new_x] == "d":  # check whether there is a door
        game.items.remove("key")           # key can be used once
        game.current_level.level[new_y][new_x] = "D"     # replace the closed door by an open one
        sound_effect = mixer.Sound('door_open.ogg')
        sound_effect.play()
    
    # secret doors
    if game.current_level.level[new_y][new_x] == "c":
        game.current_level.level[new_y][new_x] = "."
    
    # disappearing tiles
    if game.current_level.level[new_y][new_x] == "y":
        game.current_level.disappearing.append(DisappearingTile(x=new_x, y=new_y, time_step = time.time()))

    # switches
    for s in game.current_level.switch:
        if game.x == s.x and game.y == s.y:
            game.current_level.level[s.switch_y][s.switch_x] = "D"
            sound_effect = mixer.Sound('door_open.ogg')
            sound_effect.play()
        else:
            game.current_level.level[s.switch_y][s.switch_x] = "d"
        for box in game.current_level.box:
            if box.x == s.x and box.y == s.y:
                game.current_level.level[s.switch_y][s.switch_x] = "D"
    
    # move player smoothly
    if game.current_level.level[new_y][new_x] in ".DciwloyF":

        if direction == "left":
            move = Move(tile=game.character,
                        from_x=game.x, from_y=game.y,
                        speed_x = -speed_x, speed_y = 0, finished = player_move_finished
                        )
            game.current_level.moves.append(move)
            
        elif direction == "right":
            move = Move(tile=game.character,
                        from_x=game.x, from_y=game.y,
                        speed_x = speed_x, speed_y = 0, finished = player_move_finished
                        )
            game.current_level.moves.append(move)
    
        elif direction == "down":
           move = Move(tile=game.character,
                       from_x=game.x, from_y=game.y,
                       speed_x = 0, speed_y = speed_y, finished = player_move_finished
                       )
           game.current_level.moves.append(move)
           
        elif direction == "up":
            move = Move(tile=game.character,
                        from_x=game.x, from_y=game.y,
                        speed_x = 0, speed_y = -speed_y, finished = player_move_finished
                        )
            game.current_level.moves.append(move)

        game.x = new_x
        game.y = new_y
      
    # check player collision with enemies
    check_collision(game)

# testing prints
def player_move_finished(game):
    """outputs the coordinates of the player"""
    

