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
    def __init__(self, biome_pixels, fertility_pixels):
        self.height, self.width, _ = biome_pixels.shape
        self.biome_data = biome_pixels
        self.fertility_data = fertility_pixels

        # -1 means unowned. Otherwise, it holds a Settlement ID.
        self.ownership_grid = np.full((self.height, self.width), -1, dtype=int)
        self.settlements = {}

    def get_pixel_value(self, x, y):
        # 1. Calculate Biome Multiplier based on color distance
        r, g, b = self.biome_data[y, x]
        # (You will need to write a small helper to map RGB to your specific biome multipliers)
        # Example: Plains = 1.2, Grassland = 1.0, Forest = 0.8, Swamp = 0.2
        biome_mult = self.calculate_biome_multiplier(r, g, b)

        # 2. Calculate Fertility (Green is good, Red is bad)
        fr, fg, fb = self.fertility_data[y, x]
        # Rough estimate: High green relative to red = better fertility
        fertility_score = fg / (fr + fg + 1)  # +1 to avoid division by zero

        return (biome_mult, fertility_score)

    def add_settlement(self, settlement, start_x, start_y, settlement_id):
        self.settlements[settlement_id] = settlement
        settlement.x = start_x
        settlement.y = start_y
        settlement.owned_pixels = []

        # Start the expansion process
        self.expand_territory(settlement_id)

    def expand_territory(self, settlement_id):
        settlement = self.settlements[settlement_id]
        target_pixels = settlement.arable_land * 435  # Convert acres to pixels

        # Priority queue: stores (-value, x, y) so highest value pops first
        pq = []
        heapq.heappush(pq, (0, settlement.x, settlement.y))

        claimed_count = len(settlement.owned_pixels)

        while pq and claimed_count < target_pixels:
            neg_val, cx, cy = heapq.heappop(pq)

            # If already owned, skip
            if self.ownership_grid[cy, cx] != -1:
                continue

            # Claim it
            self.ownership_grid[cy, cx] = settlement_id
            settlement.owned_pixels.append((cx, cy))
            claimed_count += 1

            # Add neighbors to queue (Up, Down, Left, Right)
            neighbors = [(cx, cy - 1), (cx, cy + 1), (cx - 1, cy), (cx + 1, cy)]
            for nx, ny in neighbors:
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.ownership_grid[ny, nx] == -1:
                        val = self.get_pixel_value(nx, ny)
                        # Push negative value because heapq is a min-heap
                        heapq.heappush(pq, (-val, nx, ny))

    def calculate_biome_multiplier(self, r, g, b):
        habitability_scale = [
            ((214, 44, 32), 0.0),  # #d62c20
            ((219, 121, 0), 0.2),  # #db7900
            ((214, 199, 32), 0.4),  # #d6c720
            ((190, 214, 11), 0.6),  # #bed60b
            ((91, 191, 57), 0.8),  # #5bbf39
            ((19, 135, 19), 1.0),  # #138713
        ]

        closest_multiplier = 0.0
        min_distance = float('inf')

        for (cr, cg, cb), multiplier in habitability_scale:
            distance = (r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2

            if distance < min_distance:
                min_distance = distance
                closest_multiplier = multiplier

        return closest_multiplier

        # habitability_scale = [
        #     ("#d62c20", 0.0),
        #     ("#db7900", 0.2),
        #     ("#d6c720", 0.4),wo
        #     ("#bed60b", 0.6),
        #     ("#5bbf39", 0.8),
        #     ("#138713", 1.0),
        # ]
