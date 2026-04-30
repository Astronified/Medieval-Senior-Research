from ursina import *
from PIL import Image, ImageDraw
import math

# ─────────────────────────────────────────────
#  SAVE FILE
# ─────────────────────────────────────────────
SAVE_FILE = "saveState.txt"
saved = False
saved_seed = None
try:
    with open(SAVE_FILE, 'r') as f:
        line = f.read().strip().split(',')
        if line[0]:
            saved = True
            saved_seed = line[0]
except FileNotFoundError:
    pass

# ─────────────────────────────────────────────
#  APP + SHARED STYLE
# ─────────────────────────────────────────────
app = Ursina()

SETTLEMENT_COLORS_PIL = [
    (220, 60,  60,  120),   # red   – settlement 0
    (60,  130, 220, 120),   # blue  – settlement 1
    (60,  200, 80,  120),   # green – settlement 2
]
SETTLEMENT_COLORS_URSINA = [
    color.rgb(220, 60,  60),
    color.rgb(60,  130, 220),
    color.rgb(60,  200, 80),
]


class MenuButton(Button):
    def __init__(self, text='', **kwargs):
        kwargs.setdefault('scale', (.25, .075))
        kwargs.setdefault('highlight_color', color.azure)
        super().__init__(text, **kwargs)
        for k, v in kwargs.items():
            setattr(self, k, v)


# ─────────────────────────────────────────────
#  AUDIO + LAYOUT
# ─────────────────────────────────────────────
background_music = Audio('darkFantasy.mp3', loop=True, autoplay=True, volume=0.5)
button_spacing   = .075 * 1.25
menu_parent      = Entity(parent=camera.ui, y=.15)

main_menu    = Entity(parent=menu_parent)
load_menu    = Entity(parent=menu_parent)
options_menu = Entity(parent=menu_parent)

state_handler = Animator({
    'main_menu'    : main_menu,
    'load_menu'    : load_menu,
    'options_menu' : options_menu,
})

# ─────────────────────────────────────────────
#  MAIN MENU
# ─────────────────────────────────────────────
main_menu.buttons = [
    MenuButton('start',   on_click=Func(setattr, state_handler, 'state', 'load_menu')),
    MenuButton('options', on_click=Func(setattr, state_handler, 'state', 'options_menu')),
    MenuButton('quit',    on_click=Sequence(Wait(.01), Func(application.quit))),
]
title2 = Text(parent=main_menu, text='Medieval Simulation',
              y=(-button_spacing * 0.5), scale=3.5, color=color.white,
              origin=(0, 0), x=0, font="angel.ttf")
for i, e in enumerate(main_menu.buttons):
    e.parent = main_menu
    e.y = (-i - 2) * button_spacing


# ─────────────────────────────────────────────
#  TERRITORY PAINTING
# ─────────────────────────────────────────────
def paint_territories(coords, territory_radius=60, out_path='mapWithTerritories.png'):
    """
    Draw semi-transparent coloured blobs on a copy of the biome map
    for each settlement location, then save to out_path.
    coords : list of [x, y]  (pixel coords in the full map image)
    """
    try:
        base = Image.open('riverTest.png').convert('RGBA')
    except FileNotFoundError:
        print("[WARN] riverTest.png not found; skipping territory paint.")
        return 'riverTest.png'

    overlay = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)

    for idx, (x, y) in enumerate(coords):
        col = SETTLEMENT_COLORS_PIL[idx % len(SETTLEMENT_COLORS_PIL)]
        r   = territory_radius
        # Dot for settlement centre (fully opaque)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=col)
        # Bright centre marker
        mr = 8
        centre_col = col[:3] + (255,)
        draw.ellipse([x - mr, y - mr, x + mr, y + mr], fill=centre_col)

    combined = Image.alpha_composite(base, overlay).convert('RGB')
    combined.save(out_path)
    return out_path


# ─────────────────────────────────────────────
#  HABITABILITY → REGIONAL MULTIPLIER
# ─────────────────────────────────────────────
def sample_regional_multipliers(coords, map_path='riverTest.png'):
    """
    Sample the biome map at each settlement's spawn coordinate and convert
    the pixel colour to a regional fertility multiplier.

    The biome map (riverTest.png) uses colour to encode terrain:
      - High green, low red/blue  → fertile grassland/forest  → high multiplier
      - High blue                 → water/coast               → low (can't farm)
      - Low all channels (dark)   → barren/mountain           → low multiplier
      - High red                  → arid/desert               → low multiplier

    Returns a list of floats, one per coord, clamped to [0.4, 2.0].
    Also returns a list of human-readable terrain labels for display.
    """
    try:
        img = Image.open(map_path).convert('RGB')
    except FileNotFoundError:
        print(f"[WARN] {map_path} not found; defaulting multipliers to 1.0")
        return [1.0] * len(coords), ['unknown'] * len(coords)

    w, h   = img.size
    multis = []
    labels = []

    for (x, y) in coords:
        # PIL origin is top-left; clamp to image bounds
        px = max(0, min(int(x), w - 1))
        py = max(0, min(int(y), h - 1))
        r, g, b = img.getpixel((px, py))

        # Normalise channels to [0, 1]
        rn = r / 255.0
        gn = g / 255.0
        bn = b / 255.0

        # Fertility score: reward green, penalise blue (water) and red (arid)
        # and very dark pixels (rock/mountain).
        brightness = (rn + gn + bn) / 3.0
        fertility  = gn - 0.5 * bn - 0.3 * rn

        # Map fertility [-0.5 … 1.0] → multiplier [0.4 … 2.0]
        raw_multi = 0.4 + (fertility + 0.5) / 1.5 * 1.6
        multi     = round(max(0.4, min(2.0, raw_multi)), 2)

        # Human-readable label
        if bn > 0.55 and bn > gn:
            label = 'water'
        elif brightness < 0.18:
            label = 'barren'
        elif rn > 0.6 and gn < 0.45:
            label = 'arid'
        elif gn > 0.45 and gn >= rn and gn >= bn:
            label = 'fertile'
        else:
            label = 'mixed'

        multis.append(multi)
        labels.append(label)
        print(f"  [habitability] coord=({x},{y})  rgb=({r},{g},{b})  "
              f"fertility={fertility:.3f}  multiplier={multi}  terrain={label}")

    return multis, labels


# ─────────────────────────────────────────────
#  START GAME  (map generation)
# ─────────────────────────────────────────────
def start_game():
    menu_parent.enabled = False
    import habitabilitymapping

    if not saved:
        habitabilitymapping.makeMap()
        seed = habitabilitymapping.get_seed()
    else:
        seed = str(saved_seed)

    map_texture = 'testFast2.png'

    map_entity = Entity(
        parent=camera.ui, model='quad',
        texture=map_texture, scale=(0.8, 0.8), z=0
    )
    seed_text = Text(
        parent=camera.ui, text=f'Seed: {seed}',
        y=.45, scale=2, color=color.white, origin=(0, 0)
    )
    background = Entity(
        parent=camera.ui, model='quad', texture='middleAges2',
        scale=(camera.aspect_ratio, 1), color=color.gray, z=1, world_y=0
    )
    save_button = MenuButton(
        parent=camera.ui, text='Save This Seed', y=-0.35,
        on_click=Func(lambda: save_current_seed(seed))
    )
    back_button = MenuButton(
        parent=camera.ui, text='Back to Menu', y=-0.45,
        on_click=Func(lambda: return_to_menu(
            map_entity, seed_text, back_button, save_button, create_biome_btn
        ))
    )
    create_biome_btn = MenuButton(
        parent=camera.ui, text='Create Biome Map',
        y=-0.45, x=0.5,
        on_click=Func(lambda: make_biome(
            map_entity, seed_text, back_button, save_button, create_biome_btn
        ))
    )


# ─────────────────────────────────────────────
#  BIOME MAP
# ─────────────────────────────────────────────
def make_biome(map_entity, seed_text, back_button, save_button, create_biome_btn):
    import testFastPerlinNoise

    for e in (map_entity, seed_text, back_button, save_button, create_biome_btn):
        e.disable()

    testFastPerlinNoise.overall()

    map_entity2 = Entity(
        parent=camera.ui, model='quad',
        texture='riverTest.png', scale=(0.8, 0.8), z=0.05
    )
    topthree_btn = MenuButton(
        parent=camera.ui, text='Place Top 3', y=-0.45,
        on_click=Func(lambda: place_settlements(topthree_btn, map_entity2))
    )


# ─────────────────────────────────────────────
#  SETTLEMENT PLACEMENT
# ─────────────────────────────────────────────
def place_settlements(topthree_btn, map_entity2):
    import advancedSettlementPlacing
    info = advancedSettlementPlacing.mian()

    topthree_btn.disable()

    placement_text = Text(
        parent=camera.ui,
        text=("(" + str(info[0][1]) + ", " + str(info[0][2]) + ")  " +
              "(" + str(info[1][1]) + ", " + str(info[1][2]) + ")  " +
              "(" + str(info[2][1]) + ", " + str(info[2][2]) + ")  "),
        y=.45, scale=1, color=color.white, origin=(0, 0)
    )
    coord_input = InputField(
        parent=camera.ui,
        default_value='x1,y1,x2,y2,x3,y3',
        y=-0.35,
        limit_content_to='0123456789,',
        color=color.black,
        scale=(.8, .05),
        character_limit=60
    )
    confirm_btn = MenuButton(
        parent=camera.ui, text='Confirm Coords', y=-0.45,
        on_click=Func(lambda: validate_coords(
            coord_input, info, placement_text, confirm_btn, map_entity2
        ))
    )


def validate_coords(input_field, original_info, text_entity, confirm_btn, map_entity2):
    confirm_btn.disable()
    input_field.disable()

    user_text  = input_field.text
    final_coords = None

    if "," in user_text:
        try:
            parts = user_text.split(',')
            if len(parts) == 6:
                vals = [int(p) for p in parts]
                if all(0 <= v <= 8192 for v in vals):
                    final_coords = [
                        [vals[0], vals[1]],
                        [vals[2], vals[3]],
                        [vals[4], vals[5]],
                    ]
        except ValueError:
            pass

    if final_coords is None:
        final_coords = [
            [original_info[0][1], original_info[0][2]],
            [original_info[1][1], original_info[1][2]],
            [original_info[2][1], original_info[2][2]],
        ]

    text_entity.disable()

    # Sample the biome map NOW, while riverTest.png is freshly generated
    regional_multis, terrain_labels = sample_regional_multipliers(
        [[c[0], c[1]] for c in final_coords]
    )
    print(f"[habitability] final multipliers: {regional_multis}  terrains: {terrain_labels}")

    # Move on to population setup
    show_population_ui(final_coords, map_entity2, regional_multis, terrain_labels)


# ─────────────────────────────────────────────
#  POPULATION / OCCUPATION UI
# ─────────────────────────────────────────────
_pop_ui_entities = []   # track everything so we can clean up

SETTLEMENT_NAMES = ["Settlement 1", "Settlement 2", "Settlement 3"]


def show_population_ui(final_coords, map_entity2, regional_multis, terrain_labels):
    """
    Show a panel for each of the 3 settlements:
      - Population input
      - Optional occupation breakdown toggle
      - Per-occupation inputs (hidden unless toggled)
    Confirm launches the sim.
    """
    global _pop_ui_entities
    _pop_ui_entities.clear()

    JOBS = ['Farmer', 'Soldier', 'Clergy', 'Child']
    # We store InputField references per settlement
    pop_inputs  = []    # one InputField per settlement
    job_inputs  = []    # list of dicts per settlement  {job: InputField}
    job_panels  = []    # Entity containers (hidden by default)

    header = Text(
        parent=camera.ui,
        text='Configure Settlements  (leave job fields blank = random)',
        y=0.47, scale=1.6, color=color.white, origin=(0, 0)
    )
    _pop_ui_entities.append(header)

    col_x = [-0.55, 0.0, 0.55]   # x-positions for the 3 settlements

    for s_idx in range(3):
        cx = col_x[s_idx]
        col = SETTLEMENT_COLORS_URSINA[s_idx]

        # Settlement label (with live multiplier)
        lbl = Text(
            parent=camera.ui,
            text=f'{SETTLEMENT_NAMES[s_idx]}\n{terrain_labels[s_idx]}  ×{regional_multis[s_idx]}',
            x=cx, y=0.37, scale=1.2,
            color=col, origin=(0, 0)
        )
        _pop_ui_entities.append(lbl)

        # Population field
        pop_lbl = Text(
            parent=camera.ui,
            text='Population:',
            x=cx - 0.11, y=0.28, scale=1.1,
            color=color.white, origin=(-.5, 0)
        )
        _pop_ui_entities.append(pop_lbl)

        pop_field = InputField(
            parent=camera.ui,
            default_value='200',
            x=cx, y=0.20,
            limit_content_to='0123456789',
            color=color.black,
            scale=(.22, .05),
            character_limit=5
        )
        _pop_ui_entities.append(pop_field)
        pop_inputs.append(pop_field)

        # Toggle for occupation breakdown
        # We use a simple Button that shows/hides the job panel
        job_panel = Entity(parent=camera.ui, enabled=False)
        job_panels.append(job_panel)

        job_fields_for_s = {}

        job_y_start = 0.10
        for j_idx, job in enumerate(JOBS):
            jlbl = Text(
                parent=job_panel,
                text=job + ':',
                x=cx - 0.11, y=job_y_start - j_idx * 0.08,
                scale=1.0, color=color.light_gray, origin=(-.5, 0)
            )
            jfield = InputField(
                parent=job_panel,
                default_value='',
                x=cx, y=job_y_start - j_idx * 0.08 - 0.055,
                limit_content_to='0123456789',
                color=color.black,
                scale=(.22, .045),
                character_limit=5
            )
            job_fields_for_s[job] = jfield
            _pop_ui_entities.extend([jlbl, jfield])

        job_inputs.append(job_fields_for_s)

        # Toggle button (closure captures s_idx)
        def make_toggle(panel):
            def _toggle():
                panel.enabled = not panel.enabled
            return _toggle

        toggle_btn = MenuButton(
            parent=camera.ui,
            text='Custom Jobs ▾',
            x=cx, y=0.13,
            scale=(.22, .055),
            on_click=Func(make_toggle(job_panel))
        )
        _pop_ui_entities.extend([job_panel, toggle_btn])

    # Regional multiplier note (now derived from actual map data)
    note_str = '  '.join(
        f'S{i+1}={regional_multis[i]} ({terrain_labels[i]})' for i in range(3)
    )
    note = Text(
        parent=camera.ui,
        text=f'Fertility: {note_str}',
        y=-0.38, scale=1.0, color=color.light_gray, origin=(0, 0)
    )
    _pop_ui_entities.append(note)

    # Confirm button
    confirm = MenuButton(
        parent=camera.ui,
        text='Start Simulation',
        y=-0.46,
        on_click=Func(lambda: confirm_population(
            pop_inputs, job_inputs, final_coords, map_entity2, confirm, regional_multis
        ))
    )
    _pop_ui_entities.append(confirm)


def confirm_population(pop_inputs, job_inputs, final_coords, map_entity2, confirm_btn, regional_multis):
    confirm_btn.disable()

    JOBS = ['Farmer', 'Soldier', 'Clergy', 'Child']
    LAND = 1500

    settlement_configs = []
    for s_idx in range(3):
        # Parse population
        try:
            pop = max(10, int(pop_inputs[s_idx].text))
        except ValueError:
            pop = 200

        # Parse occupation overrides
        job_counts = {}
        any_job_set = False
        for job in JOBS:
            raw = job_inputs[s_idx][job].text.strip()
            if raw:
                try:
                    job_counts[job] = int(raw)
                    any_job_set = True
                except ValueError:
                    pass

        settlement_configs.append({
            'name'                : SETTLEMENT_NAMES[s_idx],
            'land'                : LAND,
            'population'          : pop,
            'regional_multiplier' : regional_multis[s_idx],
            'spawn_x'             : final_coords[s_idx][0],
            'spawn_y'             : final_coords[s_idx][1],
            'job_counts'          : job_counts if any_job_set else None,
        })

    # Clean up population UI
    for e in _pop_ui_entities:
        try:
            destroy(e)
        except Exception:
            pass

    # Paint territories on the map
    coords_xy = [[c['spawn_x'], c['spawn_y']] for c in settlement_configs]
    out_path  = paint_territories(coords_xy, territory_radius=80)

    # Swap the biome map entity to the painted version
    map_entity2.texture = out_path

    # Legend
    for i, cfg in enumerate(settlement_configs):
        leg = Text(
            parent=camera.ui,
            text=f'■ {cfg["name"]}  pop={cfg["population"]}',
            x=-0.38 + i * 0.38,
            y=-0.38,
            scale=1.1,
            color=SETTLEMENT_COLORS_URSINA[i],
            origin=(0, 0)
        )

    status_text = Text(
        parent=camera.ui,
        text='Running simulation… (check console for progress)',
        y=-0.46, scale=1.2, color=color.yellow, origin=(0, 0)
    )

    # Defer sim start so Ursina can render the map first
    invoke(run_simulation, settlement_configs, status_text, delay=0.1)


# ─────────────────────────────────────────────
#  SIMULATION RUNNER
# ─────────────────────────────────────────────
def run_simulation(settlement_configs, status_text):
    """
    Build settlements from configs (respecting optional job_counts),
    run 200 seasons, generate report.
    """
    import mapCoordination
    import simulationManager as simulation_manager
    import firstPythonMapTest as sim_module   # contains createSettlement / Settlement classes

    map_data  = mapCoordination.load_map_data("riverTest.png", "testFast2.png")
    world_map = mapCoordination.WorldMap(map_data[0], map_data[1])
    sim       = simulation_manager.SimulationManager(world_map)
    monitor   = simulation_manager.SimulationMonitor(sim)

    for cfg in settlement_configs:
        s = _build_settlement(cfg, sim_module)
        # Register the pre-built settlement directly — no need for a new factory method.
        sid = sim.next_settlement_id
        sim.next_settlement_id += 1
        sim.world_map.add_settlement(s, cfg['spawn_x'], cfg['spawn_y'], sid)
        sim.settlement_registry[sid] = {
            'name'           : cfg['name'],
            'founded_year'   : sim.current_year,
            'founded_season' : sim.current_season,
            'culture'        : 'default',
            'settlement_ref' : s,
            'spawn_location' : (cfg['spawn_x'], cfg['spawn_y']),
            'is_active'      : True,
        }

    for i in range(4000):
        sim.advance_all_settlements()
        if sim.total_seasons_passed % 4 == 0:
            monitor.take_snapshot()
        if sim.total_seasons_passed % 40 == 0:
            monitor.print_status()

    monitor.print_status(detailed=True)
    monitor.plot_population_over_time(save_path='population_chart.png')
    monitor.generate_report('simulation_report.txt')

    if status_text:
        status_text.text = 'Simulation complete!  See population_chart.png & simulation_report.txt'


def _build_settlement(cfg, sim_module):
    """
    Create a Settlement using sim_module primitives.
    If cfg['job_counts'] is set, honour those counts; otherwise use
    the same random distribution as createSettlement().
    """
    import random, numpy as np

    s = sim_module.Settlement()
    s.setRegionalMultiplier(cfg['regional_multiplier'])
    s.setLand(cfg['land'])

    job_counts = cfg.get('job_counts')
    pop        = cfg['population']

    peop = []

    if job_counts:
        # --- User-specified breakdown ---
        farmer_count  = job_counts.get('Farmer',  0)
        soldier_count = job_counts.get('Soldier', 0)
        clergy_count  = job_counts.get('Clergy',  0)
        child_count   = job_counts.get('Child',   0)

        # Fill remainder as Farmers
        specified = farmer_count + soldier_count + clergy_count + child_count
        if specified < pop:
            farmer_count += pop - specified

        for _ in range(farmer_count):
            age = np.random.normal(20, 13.75)
            peop.append(sim_module.Farmer(age=max(13, age) * 12))

        for _ in range(soldier_count):
            age = np.random.normal(22, 8)
            peop.append(sim_module.Solider(age=max(13, age) * 12))

        for _ in range(clergy_count):
            age = np.random.normal(30, 10)
            peop.append(sim_module.Clergy(age=max(13, age) * 12))

        for _ in range(child_count):
            age = abs(np.random.normal(6, 3))
            c   = sim_module.Child(age=age * 12)
            peop.append(c)
            s.childrenBorn += 1

    else:
        # --- Original random distribution ---
        for _ in range(pop):
            job_seed = random.random()
            age      = np.random.normal(20, 13.75)
            if age < 0:
                age = 0
            if age > 12:
                if job_seed <= 0.9:
                    peop.append(sim_module.Farmer(age=age * 12))
                elif 0.90 < job_seed < 0.97:
                    peop.append(sim_module.Solider(age=age * 12))
                else:
                    peop.append(sim_module.Clergy(age=age * 12))
            else:
                peop.append(sim_module.Child(age=age * 12))
                s.childrenBorn += 1

    s.setPeople(peop)
    s.setFood(len(peop) * 8)
    s.setBirth(0.13)
    s.setDeath(0.006)
    s.setHarvest_std(0.4)
    return s


# ─────────────────────────────────────────────
#  LOAD MENU + SAVE
# ─────────────────────────────────────────────
def return_to_menu(map_entity, seed_text, back_button, save_button, create_biome_btn):
    for e in (map_entity, seed_text, back_button, save_button, create_biome_btn):
        e.disable()
    menu_parent.enabled = True


def save_current_seed(seed):
    global saved_seed, saved
    saved_seed = seed
    if saved_seed:
        saved = True
        with open(SAVE_FILE, 'w') as f:
            f.write(f'{saved_seed}')
        print(f'Seed {saved_seed} saved!')
    slot_button.text = f'{saved_seed}'


if not saved_seed:
    slot_button = MenuButton(parent=load_menu, text='Empty Slot 1',
                             y=-1 * button_spacing, on_click=start_game)
else:
    slot_button = MenuButton(parent=load_menu, text=f'{saved_seed}',
                             y=-1 * button_spacing, on_click=start_game)

load_menu.back_button = MenuButton(
    parent=load_menu, text='back',
    y=((-3 - 2) * button_spacing),
    on_click=Func(setattr, state_handler, 'state', 'main_menu')
)


# ─────────────────────────────────────────────
#  OPTIONS MENU
# ─────────────────────────────────────────────
review_text = Text(parent=options_menu, x=.275, y=.25,
                   text='Preview text', origin=(-.5, 0))
for t in [e for e in scene.entities if isinstance(e, Text)]:
    t.original_scale = t.scale

text_scale_slider = Slider(0, 2, default=1, step=.1, dynamic=True,
                           text='Text Size:', parent=options_menu, x=-.25)

def set_text_scale():
    for t in [e for e in scene.entities if isinstance(e, Text) and hasattr(t, 'original_scale')]:
        t.scale = t.original_scale * text_scale_slider.value

text_scale_slider.on_value_changed = set_text_scale

volume_slider = Slider(
    0, 1, default=Audio.volume_multiplier, step=.1,
    text='Master Volume:', parent=options_menu, x=-.25,
    on_value_changed=lambda: setattr(Audio, 'volume_multiplier', volume_slider.value)
)

options_back = MenuButton(
    parent=options_menu, text='Back', x=-.25, origin_x=-.5,
    on_click=Func(setattr, state_handler, 'state', 'main_menu')
)

for i, e in enumerate((text_scale_slider, volume_slider, options_back)):
    e.y = -i * button_spacing


for menu in (main_menu, load_menu, options_menu):
    def animate_in_menu(menu=menu):
        for i, e in enumerate(menu.children):
            e.original_x = e.x
            e.x += .1
            e.animate_x(e.original_x, delay=i * .05, duration=.1, curve=curve.out_quad)
            e.alpha = 0
            e.animate('alpha', .7, delay=i * .05, duration=.1, curve=curve.out_quad)
            if hasattr(e, 'text_entity'):
                e.text_entity.alpha = 0
                e.text_entity.animate('alpha', 1, delay=i * .05, duration=.1)
    menu.on_enable = animate_in_menu

background = Entity(
    parent=menu_parent, model='quad', texture='middleAges2',
    scale=(camera.aspect_ratio, 1), color=color.gray, z=1, world_y=0
)

print("About to run app")
app.run()
print("App closed")