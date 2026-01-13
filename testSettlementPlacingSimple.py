import random
import numpy as np
from PIL import Image
from math import sqrt

HABITABILITY_IMG = "testFast2.png"
SWAMP_IMG = "riverTest.png"
NUM_POINTS = 10000
MIN_DISTANCE = 300
TOP_RESULTS = 100
IMAGE_SIZE = 8192
RANDOM_VARIATION = 0.05
2
habitability_scale = [
    ("#d62c20", 0.0),
    ("#db7900", 0.2),
    ("#d6c720", 0.4),
    ("#bed60b", 0.6),
    ("#5bbf39", 0.8),
    ("#138713", 1.0),
]

BAD_SWAMP_COLOR = "#18400b"

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return np.array([int(hex_color[i:i+2], 16) for i in (0, 2, 4)], dtype=float)

def color_distance(c1, c2):
    c1 = np.array(c1, dtype=float)
    c2 = np.array(c2, dtype=float)
    return np.sqrt(np.sum((c1 - c2) ** 2))

def load_image_as_array(path):
    img = Image.open(path).convert("RGB")
    return np.array(img, dtype=float)

def interpolate_habitability(rgb, scale):
    scale_rgbs = [hex_to_rgb(c) for c, _ in scale]
    scale_vals = [v for _, v in scale]
    dists = [color_distance(rgb, s) for s in scale_rgbs]
    idx = np.argsort(dists)[:2]
    d1, d2 = dists[idx[0]], dists[idx[1]]
    v1, v2 = scale_vals[idx[0]], scale_vals[idx[1]]
    if d1 + d2 == 0:
        return (v1 + v2) / 2
    weight = d2 / (d1 + d2)
    return v1 * weight + v2 * (1 - weight)

def score_swamp(pixel):
    rgb = np.array(pixel, dtype=float)
    bad_color = hex_to_rgb(BAD_SWAMP_COLOR)
    dist = color_distance(rgb, bad_color)
    if dist < 40:
        return 0.0
    elif dist < 100:
        return (dist - 40) / 60
    else:
        return 1.0

def far_enough(p1, p2, min_distance):
    return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) >= min_distance



def mian():
    habitability = load_image_as_array(HABITABILITY_IMG)
    swamp = load_image_as_array(SWAMP_IMG)
    scores = []
    for _ in range(NUM_POINTS):
        x = random.randint(0, IMAGE_SIZE - 1)
        y = random.randint(0, IMAGE_SIZE - 1)
        hab_score = interpolate_habitability(habitability[y, x], habitability_scale)
        swamp_score = score_swamp(swamp[y, x])
        total_score = hab_score * swamp_score

        # a lil variation
        noise_factor = 1 + random.uniform(-RANDOM_VARIATION, RANDOM_VARIATION)
        total_score = max(0.0, min(1.0, total_score * noise_factor))

        scores.append(((x, y), total_score))
    all_vals = [s for _, s in scores]
    print(f"Score stats: min={min(all_vals):.3f}, max={max(all_vals):.3f}, mean={np.mean(all_vals):.3f}")
    scores.sort(key=lambda s: s[1], reverse=True)
    selected = []
    for point, score in scores:
        if all(far_enough(point, p, MIN_DISTANCE) for p, _ in selected):
            selected.append((point, score))
        if len(selected) >= TOP_RESULTS:
            break

    print("\n=== Top 100 Ideal Placements ===")
    finalls = []
    for i, ((x, y), s) in enumerate(selected, 1):
        print(f"{i}. ({x}, {y}) - Score: {s:.3f}")
        finalls.append([i, x, y, float(s)])
   # print(finalls)
    return finalls


mian()

