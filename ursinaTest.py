from ursina import *

# create a window
app = Ursina()

# most things in ursina are Entities. An Entity is a thing you place in the world.
# you can think of them as GameObjects in Unity or Actors in Unreal.
# the first parameter tells us the Entity's model will be a 3d-model called 'cube'.
# ursina includes some basic models like 'cube', 'sphere' and 'quad'.

# the next parameter tells us the model's color should be orange.

# 'scale_y=2' tells us how big the entity should be in the vertical axis, how tall it should be.
# in ursina, positive x is right, positive y is up, and positive z is forward.

sky = Sky(texture='sky_default')

ground = Entity(
    model='plane',
    texture='smallCroppedHamlet.png',
    collider='box',
    scale=(100, 1, 100),
    texture_scale=(50, 50)
)

player = Entity(model='longHouse',color = color.rgb32(92, 61, 21),scale_y=2)

def update():


    player.x += held_keys['d'] * time.dt *5
    player.x -= held_keys['a'] * time.dt *5
    player.y += held_keys['w'] * time.dt *5
    player.y -= held_keys['s'] * time.dt *5
    player.z -= held_keys['up arrow'] * time.dt *5
    player.z += held_keys['down arrow'] * time.dt *5
    player.rotation_y += held_keys["right arrow"] *time.dt*50
    player.rotation_y -= held_keys["left arrow"] * time.dt*50

# this part will make the player move left or right based on our input.
# to check which keys are held down, we can check the held_keys dictionary.
# 0 means not pressed and 1 means pressed.
# time.dt is simply the time since the last frame. by multiplying with this, the
# player will move at the same speed regardless of how fast the game runs.


def input(key):
    if key == 'space':
        player.y += 1
        invoke(setattr, player, 'y', player.y-1, delay=.25)


# start running the game
app.run()


