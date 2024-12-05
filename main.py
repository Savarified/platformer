import pygame
import sys
import math
import random
import os

fullscreen = False

#Create new window
os.environ['SDL_VIDEO_WINDOW_POS'] = str(1000) + "," + str(0)
pygame.init()

#define window specifications
WIDTH = 600
HEIGHT = 400
if fullscreen:
    window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
else:
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Platformer')
font = pygame.font.Font(None, 16)
clock = pygame.time.Clock()
FPS = 60

_cam = [0,0,1]
null_image = pygame.image.load('textures/null.png')

#player sprites
s0 = pygame.image.load('textures/sprites/player/walk0000.png')
s1 = pygame.image.load('textures/sprites/player/walk0001.png')
s2 = pygame.image.load('textures/sprites/player/walk0002.png')
s3 = pygame.image.load('textures/sprites/player/walk0003.png')
s4 = pygame.image.load('textures/sprites/player/walk0004.png')
s5 = pygame.image.load('textures/sprites/player/walk0005.png')
s6 = pygame.image.load('textures/sprites/player/walk0006.png')
s7 = pygame.image.load('textures/sprites/player/walk0007.png')

#world textures
sky = (99,206,255, 255)
grass = 'textures/grass.png'
dirt = 'textures/dirt.png'
#stone = 'textures/stone.png'
stone = 'textures/sprites/blocks/stone.png'
brick = 'textures/brick.png'
void = [0,0,0]
light = 'textures/light.png'
lightwood_plank = 'textures/lightwood_plank.png'
darkwood_plank = 'textures/darkwood_plank.png'
oak_log = 'textures/oak_log.png'
leaves = 'textures/leaves.png'
blue_ore = 'textures/blue_ore.png'
glass = 'textures/glass.png'


red_concrete = [255, 94, 94]
blue_concrete = [77, 130, 255]
green_concrete = [0, 168, 6]
yellow_concrete = [251, 255, 122]
orange_concrete = [255, 167, 59]
purple_concrete = [199, 59, 255]
pink_concrete = [255, 143, 234]
lime_concrete = [187, 255, 128]


pickaxe_sprite = 'textures/sprites/blocks/pickaxe.png'
pickaxe_down = pygame.transform.rotate(pygame.image.load(pickaxe_sprite), 36)
material = 0 #refers to the index in the voxel_order
player_anim_sprites = [s0,s1,s2,s3,s4,s5,s6,s7]
voxel_order = [[grass, 1],
               [dirt, 2],
               [stone, 4],
               [brick,5],
               [oak_log,2],
               [leaves, 1],
               [glass, 1],
               [light, 1],
               [lightwood_plank, 3],
               [darkwood_plank, 3],
               [red_concrete, 4],
               [blue_concrete, 4],
               [green_concrete, 4],
               [yellow_concrete, 4],
               [orange_concrete, 4],
               [purple_concrete, 4],
               [pink_concrete, 4],
               [lime_concrete, 4],
               [blue_ore, 6],
               [void, 100000]]
mouseDown = False

class player:
    def __init__(self, x, y, dx, dy, animState, facing):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.facing = facing;
        self.animState = animState

class tool:
    def __init__(self, x, y, r, facing, sprite):
        self.x = x
        self.y = y
        self.dx = r
        self.facing = facing;
        self.sprite = pygame.image.load(sprite)
        self.sprite = pygame.transform.scale(self.sprite, (64 * _cam[2], 64 * _cam[2]))

class vox:
    _registry = []
    def __init__(self, x, y, texture, t, o, r):
        self.x = x
        self.y = y
        if(type(texture)==type('')):
            self.texture = pygame.image.load(texture)
            self.texture = pygame.transform.scale(self.texture, (32 * _cam[2],32 * _cam[2]))
        if(type(texture)==type([0,0,0])):
           self.texture = texture
        self.t = t
        self.o = o
        self.r = r
        self._registry.append(self)

def dist(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def get_voxel(screen_x,screen_y): #Returns which voxel is at a screen position
    vox_x = round((float(screen_x) + (_cam[0]*32) - (WIDTH/2) + 16) / 32 +.5) - 1
    vox_y = round( (float(screen_y) - (_cam[1]*32) - (HEIGHT/2) ) / -32 + .5)

    for i in range(len(vox._registry)):
        if (vox._registry[i].t <= 0):
            vox._registry.remove(vox._registry[i])
            break
        if (vox._registry[i].x == vox_x) and (vox._registry[i].y == vox_y):
                return vox._registry[i]

    return True
    #return [vox_x, vox_y]

def debug(var, position): #Draw text to screen in a list
    var = str(var)
    text = font.render(var, True, [0,0,0])
    textRect = pygame.Rect(0, position * 20, 2, 2)
    screen.blit(text, textRect)

def copysign(value): #returns the sign of any number
   if (value>0):
      return 1
   elif (value<0):
      return -1
   else:
      return 0

v = [] #list of all voxels
def initVoxes():
    #world generation
    world_width = 128
    world_height = 16
    a = 1 #rate of change by sin
    scale = [1, .05]
    offset = 0

    grass_height = 3
    dirt_height = 7
    for x in range(world_width):
        c = 0 #order in collumn 0 is top world_height is bottom
        y = round(math.sin(x*scale[0]) * a * scale[1]) + offset
        a = random.randrange(-1,1)
        offset += round(random.randint(-1,1))
        
        for c in range(world_height+8):
            if(y-c < -world_height): break
            if(c < random.randint(grass_height-1,grass_height+1)): v.append(vox(x, y-c, voxel_order[0][0], voxel_order[0][1], 0, random.randint(0,3)))
            elif(c < random.randint(dirt_height-1,dirt_height+1)): v.append(vox(x, y-c, voxel_order[1][0], voxel_order[1][1], 1, random.randint(0,3)))
            else:
                if random.randint(0,64)!=4:
                    v.append(vox(x, y-c, voxel_order[2][0], voxel_order[2][1],2,random.randint(0,3)))
                else:
                    v.append(vox(x,y-c, voxel_order[-2][0], voxel_order[-2][1],2,random.randint(0,3)))

        v.append(vox(x, -world_height - 1, voxel_order[-1][0], voxel_order[-1][1],4,0))

    v.append(vox(10, 8, voxel_order[3][0], voxel_order[3][1], 3,0))

                    
panda = player(64, 8, 0, 0, 0, 1)
pickaxe = tool(-12,-24,0,1, pickaxe_sprite)
pickaxe_down = pygame.transform.rotate(pickaxe.sprite, 45)

def render():
    for voxel in vox._registry: #draw all the voxels
        if(voxel.t > 0):
            if(type(voxel.texture)==type(null_image)):
                screen_x = round((voxel.x*32) - (_cam[0]*32) + (WIDTH/2 - 16))
                screen_y = round((-voxel.y*32) + (_cam[1]*32) + (HEIGHT/2))
                image = voxel.texture
                image = pygame.transform.rotate(image, voxel.r*90)
                screen.blit(image, (screen_x, screen_y))
            if(type(voxel.texture)==type([0,0,0])):
                screen_x = round((voxel.x*32) - (_cam[0]*32) + (WIDTH/2 - 16))
                screen_y = round((-voxel.y*32) + (_cam[1]*32) + (HEIGHT/2))

                x1 = screen_x
                y1 = screen_y
                x2 = screen_x + 31
                y2 = screen_y + 31
                p1 = [x1,y1]
                p2 = [x2,y1]
                p3 = [x2,y2]
                p4 = [x1,y2]
                quad = [p1,p2,p3,p4]
                pygame.draw.polygon(screen, voxel.texture, quad)

    #draw pickaxe

    screen_x = round(WIDTH/2) + pickaxe.x
    screen_y = round(HEIGHT/2) + pickaxe.y
    if not(mouseDown):
        if(panda.facing > 0):screen.blit(pickaxe.sprite, (screen_x, screen_y))
        if(panda.facing < 0):screen.blit(pickaxe.sprite, (screen_x-32, screen_y))
    else:
        if(panda.facing > 0):screen.blit(pygame.transform.flip(pickaxe_down, True, False), (screen_x-16, screen_y-16))
        if(panda.facing < 0):screen.blit(pickaxe_down, (screen_x-48, screen_y-12))

    
    #draw panda
    sprite = player_anim_sprites[round(panda.animState)]
    sprite = pygame.transform.scale(sprite, (128,128))
    if(panda.facing < 0): sprite = pygame.transform.flip(sprite, True, False)
    if(panda.facing > 0): sprite = pygame.transform.flip(sprite, False, False)
    screen.blit(sprite, (WIDTH/2 - 64, HEIGHT/2 - 64))
    
def moveCam(): #Move the camera with WASD
    moveSpeed = 0.055 * (1000/FPS)
    if (WASD[0] and not WASD[2]): _cam[1] += moveSpeed #+y
    if (WASD[2] and not WASD[0]): _cam[1] -= moveSpeed #-y
    if (WASD[3] and not WASD[1]): _cam[0] += moveSpeed #+x
    if (WASD[1] and not WASD[3]): _cam[0] -= moveSpeed #-x

'''
collisions[]:
 _______________________
 |Index | Position      |
 |0     | Left Bottom   |
 |1     | Left Top      |
 |2     | Right Bottom  |
 |3     | Right Top     |
 |4     | Bottom        |
 |5     | Top           |
 -----------------------'

'''

initial_ground_collision = False
collisions = [0,0, 0,0, 0,0]
def playerMovement():
    #collision check
    global collisions, initial_ground_collision

    collisions = [0,0, 0,0, 0,0]
    ground_collision = False
    if(panda.dx < 0): #if facing left: check bottom then top
        rx = round((WIDTH/2) - 18)
        ry = round((HEIGHT/2) + 26)
        col = screen.get_at((rx,ry))
        screen.set_at((rx,ry), [255,255,255, 255])
        if not (col==sky):collisions[0] = True
        
        rx = round((WIDTH/2) - 26)
        ry = round((HEIGHT/2) - 18)
        col = screen.get_at((rx,ry))
        screen.set_at((rx,ry), [255,255,255, 255])
        if not (col==sky):collisions[1] = True

    if(panda.dx > 0): #if facing right: check bottom then top
        rx = round((WIDTH/2) + 16)
        ry = round((HEIGHT/2) + 24)
        col = screen.get_at((rx,ry))
        if not (col==sky):collisions[2] = True
        
        rx = round((WIDTH/2) + 25)
        ry = round((HEIGHT/2) - 16)
        col = screen.get_at((rx,ry))
        if not (col==sky):collisions[3] = True

    #check top
    '''if(panda.facing > 0):
        rx = round((WIDTH/2)+6)
        ry = round((HEIGHT/2) -34)
        col = screen.get_at((rx,ry))
        if not (col==sky):collisions[5] = True
        screen.set_at((rx,ry), [255,255,255])
    else:
        rx = round((WIDTH/2)-6)
        ry = round((HEIGHT/2) -34)
        col = screen.get_at((rx,ry))
        if not (col==sky):collisions[5] = True
        screen.set_at((rx,ry), [255,255,255])'''

    #gravity
    rx = round((WIDTH/2))
    ry = round((HEIGHT/2) + 33)
    col = screen.get_at((rx,ry))

    #detect if colliding with the ground
    if not (col==sky):
        collisions[4] = True
        if not (initial_ground_collision): #if collision is initial, bounce
            initial_ground_collision = True
            panda.dy = panda.dy * -.2 
        else: #if collision is not initial, maintain y
            panda.y = round(panda.y)
    
    #if not colliding with the ground, accelerate towards ground
    else:
        collisions[4] = False
        initial_ground_collision = False
        panda.dy -= (9.81 / 512)
 
    if(abs(panda.dx)>0)and (collisions[4]): #if moving and on the ground, snap to the next voxel
        if not(collisions[1] and collisions[3]):
            if(collisions[0] or collisions[2]):
                panda.y += 1
                panda.x += copysign(panda.dx) * 0.5
                panda.dy = 0
                panda.dx = 0

    if collisions[5]:
        panda.dy *= -0.5
        panda.y -= 0.5
        print('hit')


    panda.y += panda.dy
    _cam[1] = panda.y

    #if any of the left or the right collisions are true, freeze the x position of the player 
    left_right_total = 0
    j = 0
    while (j < 3):
        if(collisions[j]==True): left_right_total += 1
        j+=1
    if (left_right_total == 0):
        panda.x += panda.dx
        _cam[0] = panda.x
        
    moveSpeed =  .1 * (1000/FPS) / 32
    if (WASD[3] and not WASD[1]):
        panda.dx = moveSpeed
    if (WASD[1] and not WASD[3]):
        panda.dx = -moveSpeed

def jump():
    global collisions
    if (collisions[4]):
        panda.dy += .45

def drawCurrentMat():
    bg = pygame.Rect(0,0,32+8,32+8)
    pygame.draw.rect(screen, [255,255,255], bg)
        
    if(type(voxel_order[material][0]) == type('')):
        currentMat = pygame.image.load(voxel_order[material][0])
        currentMat = pygame.transform.scale(currentMat, [32,32])
        icon = pygame.Rect(4,4,32,32)
        pygame.draw.rect(screen, sky, icon)
        screen.blit(currentMat, (4,4))
    else:
        currentMat = pygame.Rect(4,4,32,32)
        pygame.draw.rect(screen, voxel_order[material][0], currentMat)
 
initVoxes()

WASD = [0,0,0,0]
shiftDown = False
run = True
while run:
    screen.fill(sky)
    render()
    playerMovement()
    drawCurrentMat()
    if(abs(panda.dx)>0):
        panda.animState += .30
        if(panda.animState >= 7): panda.animState = 0 #reset player animation frame loop
        
    pygame.display.flip()
    clock.tick(FPS)
    pickaxe_flash = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

        if pygame.mouse.get_pressed()[0]: #left click
            mouse_pos = pygame.mouse.get_pos()
            temp_vox = get_voxel(mouse_pos[0], mouse_pos[1])
            if not shiftDown:
                if not (temp_vox == True): temp_vox.t -= 1
            else:
                if not (temp_vox == True):
                    material = temp_vox.o
            mouseDown = True
        else: mouseDown = False

        if pygame.mouse.get_pressed()[2]: #right click
            screen_x = pygame.mouse.get_pos()[0]
            screen_y = pygame.mouse.get_pos()[1]
            vox_x = round((float(screen_x) + (_cam[0]*32) - (WIDTH/2) + 16) / 32 +.5) - 1
            vox_y = round( (float(screen_y) - (_cam[1]*32) - (HEIGHT/2) ) / -32 + .5)
            temp_vox = get_voxel(screen_x, screen_y)
            voxe = 0
            if (temp_vox == True):
                screen.fill([255,0,0])
                v.append(vox(vox_x, vox_y, voxel_order[material][0], voxel_order[material][1], material, 0))
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
                pygame.quit()
                sys.exit()
                
            if event.key == pygame.K_w:  #Camera controls
                WASD[0] = True
            if event.key == pygame.K_a:
                WASD[1] = True
                if not(WASD[3]): 
                    panda.facing = -1
            if event.key == pygame.K_s:
                WASD[2] = True
            if event.key == pygame.K_d:
                WASD[3] = True
                if not(WASD[1]): 
                    panda.facing = 1

            if event.key == pygame.K_UP:
                _max = len(voxel_order)
                if material < _max:
                    material += 1
                if material >= _max:
                    material = 0

            if event.key == pygame.K_DOWN:
                if material > 0:
                    material -= 1
                    continue
                if material <= 0:
                    material = len(voxel_order)-1
            
            if event.key == pygame.K_SPACE:
                jump()

            if event.key == pygame.K_c: #camera position + scale
                print(f"POSITION x:{_cam[0]} y:{_cam[1]} z:{_cam[2]}\n")

            if event.key == pygame.K_p: #panda position
                print(f"POSITION x:{panda.x} y:{panda.y} dx:{panda.dx} dy:{panda.dy}\n")

            if event.key == pygame.K_r: #reset panda position
                panda.y = 6
                panda.dx = 0
                panda.dy = 0

            if event.key == pygame.K_t:
                global collisisons
                print("LB", collisions[0])
                print("LT", collisions[1])
                print("RB", collisions[2])
                print("RT", collisions[3])
                print("B", collisions[4])
                print("T", collisions[5])

            if event.key == pygame.K_LSHIFT: shiftDown = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w:  #CAM controls
                WASD[0] = False
            if event.key == pygame.K_a:
                WASD[1] = False
                panda.dx = 0
                panda.animState = 0
        
            if event.key == pygame.K_s:
                WASD[2] = False
            if event.key == pygame.K_d:
                WASD[3] = False
                panda.dx = 0
                panda.animState = 0
            if event.key == pygame.K_LSHIFT: shiftDown = False
