from PIL import Image
import numpy as np
import heapq


def load_map_data(biome_path, fertility_path):
    # Load images and convert to numpy arrays
    biome_img = Image.open(biome_path).convert('RGB')
    fertility_img = Image.open(fertility_path).convert('RGB')

    biome_pixels = np.array(biome_img)
    fertility_pixels = np.array(fertility_img)

    return biome_pixels, fertility_pixels


class WorldMap:
    def __init__(self, fertility_pixels,biome_pixels):
        self.height, self.width, _ = biome_pixels.shape
        self.biome_data = biome_pixels
        self.fertility_data = fertility_pixels

        # -1 means unowned. Otherwise, it holds a Settlement ID.
        self.ownership_grid = np.full((self.height, self.width), -1, dtype=int)
        self.settlements = {}

    # def get_pixel_value(self, x, y):
    #     # 1. Calculate Biome Multiplier based on color distance
    #     r, g, b = self.biome_data[y, x]
    #     # (You will need to write a small helper to map RGB to your specific biome multipliers)
    #     # Example: Plains = 1.2, Grassland = 1.0, Forest = 0.8, Swamp = 0.2
    #     biome_mult = self.calculate_biome_multiplier(r, g, b)
    #
    #     # 2. Calculate Fertility (Green is good, Red is bad)
    #     fr, fg, fb = self.fertility_data[y, x]
    #     # Rough estimate: High green relative to red = better fertility
    #     fertility_score = fg / (fr + fg + 1)  # +1 to avoid division by zero
    #
    #     return (biome_mult, fertility_score)
    def get_pixel_value(self, x, y):
        # 1. Calculate Habitability Score (from the heat map)
        # Assuming self.biome_data holds the Habitability map
        hab_r, hab_g, hab_b = self.biome_data[y, x]
        hab_score = self.calculate_habitability_score(hab_r, hab_g, hab_b)

        # 2. Calculate Biome/Swamp Score (from the actual terrain map)
        # Assuming self.fertility_data holds the Swamp/Greenery map
        swamp_r, swamp_g, swamp_b = self.fertility_data[y, x]
        swamp_score = self.calculate_swamp_score(swamp_r, swamp_g, swamp_b)

        # The final multiplier is the combined score (0.0 to 1.0)
        return hab_score * swamp_score


    def add_settlement(self, settlement, start_x, start_y, settlement_id):
        self.settlements[settlement_id] = settlement
        settlement.x = start_x
        settlement.y = start_y
        settlement.owned_pixels = []
        self.expand_territory(settlement_id)

    def expand_territory(self, settlement_id):
        settlement = self.settlements[settlement_id]
        target_pixels = settlement.arable_land * 435
        pq = []
        heapq.heappush(pq, (0, settlement.x, settlement.y))
        addedLand = 0
        claimed_count = len(settlement.owned_pixels)

        while pq and claimed_count < target_pixels:
            neg_val, cx, cy = heapq.heappop(pq)

            #if already owned skip
            if self.ownership_grid[cy, cx] != -1:
                continue
            #claim it
            self.ownership_grid[cy, cx] = settlement_id
            settlement.owned_pixels.append((cx, cy))
            claimed_count += 1
            addedLand+=1


            neighbors = [(cx, cy - 1), (cx, cy + 1), (cx - 1, cy), (cx + 1, cy)]
            for nx, ny in neighbors:
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.ownership_grid[ny, nx] == -1:
                        val = self.get_pixel_value(nx, ny)
                        heapq.heappush(pq, (-val, nx, ny))
        return [claimed_count, addedLand]


    def calculate_habitability_score(self, r, g, b):
        """stupid thing that likes to break"""
       # print("habit: " + str(r) + ", " + str(g)+ ", " + str(b))
        habitability_scale = [
            (np.array([214, 44, 32]), 0.01),  # #d62c20
            (np.array([219, 121, 0]), 0.2),  # #db7900
            (np.array([214, 199, 32]), 0.4),  # #d6c720
            (np.array([190, 214, 11]), 0.6),  # #bed60b
            (np.array([91, 191, 57]), 0.8),  # #5bbf39
            (np.array([19, 135, 19]), 1.0),  # #138713
        ]

        target_rgb = np.array([r, g, b], dtype=float)

        dists = [np.linalg.norm(target_rgb - scale_rgb) for scale_rgb, _ in habitability_scale]
        idx = np.argsort(dists)[:2]
        d1, d2 = dists[idx[0]], dists[idx[1]]
        v1, v2 = habitability_scale[idx[0]][1], habitability_scale[idx[1]][1]
        if d1 + d2 == 0:
            return (v1 + v2) / 2.0

        weight = d2 / (d1 + d2)
        return v1 * weight + v2 * (1 - weight)

    def calculate_swamp_score(self, r, g, b):
        """Penalizes pixels that are too close to the bad swamp color."""
        # BAD_SWAMP_COLOR = "#18400b"
        #print("swamp:" + str(r) + ", " + str(g)+ ", " + str(b))
        target_rgb = np.array([r, g, b], dtype=float)
        bad_color = np.array([24, 64, 11], dtype=float)

        dist = np.linalg.norm(target_rgb - bad_color)

        if dist < 40:
            return 0.01
        elif dist < 100:
            return (dist - 40) / 60.0
        else:
            return 1.0

        # habitability_scale = [
        #     ("#d62c20", 0.0),
        #     ("#db7900", 0.2),
        #     ("#d6c720", 0.4),wo
        #     ("#bed60b", 0.6),
        #     ("#5bbf39", 0.8),
        #     ("#138713", 1.0),
        # ]
