from ursina import *


SAVE_FILE = "saveState.txt"
saved = False
saved_seed=None
with open(SAVE_FILE, 'r') as f:
    line = f.read().strip().split(',')
    if line[0]:
        saved=True
        saved_seed=line[0]

app = Ursina()
class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        super().__init__(text, scale=(.25, .075), highlight_color=color.azure, **kwargs)

        for key, value in kwargs.items():
            setattr(self, key ,value)


# button_size = (.25, .075)
background_music = Audio('darkFantasy.mp3', loop=True, autoplay=True, volume=0.5)
button_spacing = .075 * 1.25
menu_parent = Entity(parent=camera.ui, y=.15)
title = Entity(parent=menu_parent)
main_menu = Entity(parent=menu_parent)
load_menu = Entity(parent=menu_parent)
options_menu = Entity(parent=menu_parent)
state_handler = Animator({
    # 'title' : title,
    'main_menu' : main_menu,
    'load_menu' : load_menu,
    'options_menu' : options_menu,
    }
)


# main menu content
main_menu.buttons = [
    MenuButton('start', on_click=Func(setattr, state_handler, 'state', 'load_menu')),
    MenuButton('options', on_click=Func(setattr, state_handler, 'state', 'options_menu')),
    MenuButton('quit', on_click=Sequence(Wait(.01), Func(application.quit))),
]
title2 = Text(parent=main_menu, text='Medieval Simulation',y=(-button_spacing * 0.5), scale=3.5, color=color.white, origin=(0,0), x=0, font = "angel.ttf")
for i, e in enumerate(main_menu.buttons):
    e.parent = main_menu
    e.y = (-i-2) * button_spacing


def start_game():
    menu_parent.enabled = False
    import habitabilitymapping

    if saved==False:
        habitabilitymapping.makeMap()
        seed = habitabilitymapping.get_seed()

        map_texture = 'testFast2.png'
    else:
        map_texture = 'testFast2.png'
        seed = str(saved_seed)

    map_entity = Entity( #THIS IS USED PYCHARM IS JUST CONFUSED
        parent=camera.ui,
        model='quad',
        texture=map_texture,
        scale=(0.8, 0.8),
        z=0  # in front of the background
    )


    seed_text = Text( #THIS IS USED PYCHARM IS JUST CONFUSED
        parent=camera.ui,
        text=f'Seed: {seed}',
        y=.45,
        scale=2,
        color=color.white,
        origin=(0,0)
    )
    background = Entity(parent=camera.ui, model='quad', texture='shore', scale=(camera.aspect_ratio, 1),
                        color=color.gray, z=1, world_y=0)
    background.texture = "middleAges2"
    save_button = MenuButton(
        parent=camera.ui,
        text='Save This Seed',
        y=-0.35,
        on_click=Func(lambda: save_current_seed(seed))
    )
    back_button = MenuButton(
        parent=camera.ui,
        text='Back to Menu',
        y=-0.45,
        on_click=Func(lambda: return_to_menu(map_entity, seed_text, back_button,save_button, createBiomeMap))
    )
    createBiomeMap = MenuButton(
        parent=camera.ui,
        text='Create Biome Map',
        y=-0.45,
        x=0.5,
        on_click=Func(lambda: makeBiome(map_entity, seed_text, back_button, save_button,createBiomeMap))
    )
def makeBiome(map_entity, seed_text, back_button,save_button,createBiomeMap):
    import testFastPerlinNoise


    map_entity.disable()
    seed_text.disable()
    back_button.disable()
    save_button.disable()
    createBiomeMap.disable()
    testFastPerlinNoise.overall()
    map_texture = "riverTest.png"
    map_entity2 = Entity(  # THIS IS USED PYCHARM IS JUST CONFUSED
        parent=camera.ui,
        model='quad',
        texture=map_texture,
        scale=(0.8, 0.8),
        z=0  # in front of the background
    )
    topthree = MenuButton(
        parent=camera.ui,
        text='Place Top 3',
        y=-0.45,
        on_click=Func(lambda: placeSettlements(topthree))
    )

def placeSettlements(topthree):
    import advancedSettlementPlacing
    info = advancedSettlementPlacing.mian()
    settlementPlacementText = Text(  # THIS IS USED PYCHARM IS JUST CONFUSED
        parent=camera.ui,
        text= "("+str(info[0][1])+", "+str(info[0][2])+")  " + "("+str(info[1][1])+", "+str(info[1][2])+")  " +"("+str(info[2][1])+", "+str(info[2][2])+")  ",
        y=.45,
        scale=1,
        color=color.white,
        origin=(0, 0)
    )
    topthree.disable()
    # 1. Input Field
    # We restrict input to '0123456789,' so they cannot type letters or spaces.
    # Format expected: x1,y1,x2,y2,x3,y3
    user_coord_input = InputField(
        parent=camera.ui,
        default_value='x1,y1,x2,y2,x3,y3',
        y=-0.35,
        limit_content_to='0123456789,',
        color=color.black,
        scale=(.8, .05),
        character_limit = 60
    )

    # 2. Confirm Button
    InputNew = MenuButton(
        parent=camera.ui,
        text='Confirm Coords',
        y=-0.45,
        # Pass the button itself (InputNew) so we can disable it inside the function
        on_click=Func(lambda: returnInputData(user_coord_input, info, settlementPlacementText, InputNew))
    )


def returnInputData(input_field, original_info, text_entity, confirm_button):
    # 1. Immediately disable UI elements to prevent double clicks
    import simulation
    confirm_button.disable()
    input_field.disable()
    # text_entity.disable() # Optional: keep text visible or hide it

    user_text = input_field.text
    final_coords = []
    valid_input = False

    print(f"User Input: {user_text}")

    # 2. Validation Logic
    if "," in user_text:
        try:
            parts = user_text.split(',')

            # Check if we have exactly 6 numbers (3 pairs)
            if len(parts) == 6:
                temp_coords = []
                all_in_bounds = True

                # Loop through all inputs to check validity
                for part in parts:
                    val = int(part)  # Will error if empty
                    if 0 <= val <= 8192:
                        temp_coords.append(val)
                    else:
                        all_in_bounds = False
                        print(f"Value {val} is out of bounds (0-8192).")
                        break

                # If loop finished successfully
                if all_in_bounds:
                    # Group into pairs [[x1,y1], [x2,y2], [x3,y3]]
                    final_coords = [
                        [temp_coords[0], temp_coords[1]],
                        [temp_coords[2], temp_coords[3]],
                        [temp_coords[4], temp_coords[5]]
                    ]
                    valid_input = True
                    print("User override successful.")
            else:
                print(f"Incorrect amount of coordinates. Expected 6 numbers, got {len(parts)}.")

        except ValueError:
            print("Formatting error (did you leave a trailing comma or empty space?)")

    pixelval = 1.1
    if not valid_input:
        print("Invalid input. Reverting to generated coordinates.")
        # Extract x,y from the original info list
        final_coords = [
            [original_info[0][1], original_info[0][2]],
            [original_info[1][1], original_info[1][2]],
            [original_info[2][1], original_info[2][2]]
        ]

    print(f"Final Output: {final_coords}")
    imgtexture = load_texture("riverTest.png")
    pixel = imgtexture.get_pixel(original_info[0][1], original_info[0][2])
    print("the pixel is " + str(pixel))


    simulation.startSim(pixelval)
    return final_coords

def return_to_menu(map_entity, seed_text, back_button,save_button,createBiomeMap):
    map_entity.disable()
    seed_text.disable()
    back_button.disable()
    save_button.disable()
    createBiomeMap.disable()
    menu_parent.enabled = True
def save_current_seed(seed):
    global saved_seed, saved
    saved_seed=seed
    if saved_seed:
        saved = True
        with open(SAVE_FILE, 'w') as f:
            f.write(f'{saved_seed}')
        print(f'Seed {saved_seed} saved!')
    else:
        print("blah")
    slot_button.text = f'{saved_seed}'

#for i in range(3):
if not saved_seed:
    slot_button = MenuButton(parent=load_menu, text=f'Empty Slot 1', y=-1 * button_spacing, on_click=start_game)
else:
    slot_button = MenuButton(parent=load_menu, text=f'{saved_seed}', y=-1 * button_spacing, on_click=start_game)

load_menu.back_button = MenuButton(parent=load_menu, text='back', y=((-3-2) * button_spacing), on_click=Func(setattr, state_handler, 'state', 'main_menu'))


# options menu content
review_text = Text(parent=options_menu, x=.275, y=.25, text='Preview text', origin=(-.5,0))
for t in [e for e in scene.entities if isinstance(e, Text)]:
    t.original_scale = t.scale

text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True, text='Text Size:', parent=options_menu, x=-.25)
def set_text_scale():
    for t in [e for e in scene.entities if isinstance(e, Text) and hasattr(e, 'original_scale')]:
        t.scale = t.original_scale * text_scale_slider.value
text_scale_slider.on_value_changed = set_text_scale


def update_volume_for_currently_playing():
    for e in scene.entities:
        if isinstance(e, Audio):
            e.volume = e.volume

volume_slider = Slider(0, 1, default=Audio.volume_multiplier, step=.1, text='Master Volume:', parent=options_menu, x=-.25,
    on_value_changed = lambda: (
        setattr(Audio, 'volume_multiplier', volume_slider.value),
        update_volume_for_currently_playing()
    )
)

options_back = MenuButton(parent=options_menu, text='Back', x=-.25, origin_x=-.5, on_click=Func(setattr, state_handler, 'state', 'main_menu'))

for i, e in enumerate((text_scale_slider, volume_slider, options_back)):
    e.y = -i * button_spacing

for menu in (main_menu, load_menu, options_menu):
    def animate_in_menu(menu=menu):
        for i, e in enumerate(menu.children):
            e.original_x = e.x
            e.x += .1
            e.animate_x(e.original_x, delay=i*.05, duration=.1, curve=curve.out_quad)

            e.alpha = 0
            e.animate('alpha', .7, delay=i*.05, duration=.1, curve=curve.out_quad)

            if hasattr(e, 'text_entity'):
                e.text_entity.alpha = 0
                e.text_entity.animate('alpha', 1, delay=i*.05, duration=.1)

    menu.on_enable = animate_in_menu


background = Entity(parent=menu_parent, model='quad', texture='shore', scale=(camera.aspect_ratio,1), color=color.gray, z=1, world_y=0)
background.texture="middleAges2"
app.run()