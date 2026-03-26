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
    def __init__(self, fertility_pixels, biome_pixels):
        self.height, self.width, _ = biome_pixels.shape
        self.biome_data = biome_pixels
        self.fertility_data = fertility_pixels

        # -1 means unowned. Otherwise, it holds a Settlement ID.
        self.ownership_grid = np.full((self.height, self.width), -1, dtype=int)
        self.settlements = {}

        # CRITICAL: Each settlement maintains its own persistent frontier heap
        # This allows efficient incremental expansion without re-traversing from center
        self.settlement_frontiers = {}  # settlement_id -> priority queue of frontier pixels

    def get_pixel_value(self, x, y):
        # 1. Calculate Habitability Score (from the heat map)
        hab_r, hab_g, hab_b = self.biome_data[y, x]
        hab_score = self.calculate_habitability_score(hab_r, hab_g, hab_b)

        # 2. Calculate Biome/Swamp Score (from the actual terrain map)
        swamp_r, swamp_g, swamp_b = self.fertility_data[y, x]
        swamp_score = self.calculate_swamp_score(swamp_r, swamp_g, swamp_b)

        # The final multiplier is the combined score (0.0 to 1.0)
        return hab_score * swamp_score

    def add_settlement(self, settlement, start_x, start_y, settlement_id):
        """Initialize a new settlement and set up its frontier heap"""
        self.settlements[settlement_id] = settlement
        settlement.x = start_x
        settlement.y = start_y
        settlement.owned_pixels = []

        # Initialize the persistent frontier heap for this settlement
        self.settlement_frontiers[settlement_id] = []

        # Start expansion from the initial position
        self._initialize_frontier(settlement_id, start_x, start_y)
        self.expand_territory(settlement_id)

    def _initialize_frontier(self, settlement_id, x, y):
        """Initialize the frontier heap with the starting position"""
        frontier = self.settlement_frontiers[settlement_id]
        val = self.get_pixel_value(x, y)
        heapq.heappush(frontier, (-val, x, y))

    def _add_neighbors_to_frontier(self, settlement_id, cx, cy):
        """Add unclaimed neighbors of a newly claimed pixel to the frontier"""
        frontier = self.settlement_frontiers[settlement_id]
        neighbors = [(cx, cy - 1), (cx, cy + 1), (cx - 1, cy), (cx + 1, cy)]

        for nx, ny in neighbors:
            # Check bounds
            if 0 <= nx < self.width and 0 <= ny < self.height:
                # Only add if unclaimed
                if self.ownership_grid[ny, nx] == -1:
                    val = self.get_pixel_value(nx, ny)
                    heapq.heappush(frontier, (-val, nx, ny))

    def expand_territory(self, settlement_id):
        """
        Expand territory using the persistent frontier heap.
        This method can be called multiple times - it will continue from where it left off.
        """
        settlement = self.settlements[settlement_id]
        target_pixels = settlement.arable_land * 435

        # Use the persistent frontier heap
        frontier = self.settlement_frontiers[settlement_id]

        claimed_count = len(settlement.owned_pixels)
        added_land = 0

        # Continue expanding until we reach target or run out of frontier
        while frontier and claimed_count < target_pixels:
            neg_val, cx, cy = heapq.heappop(frontier)

            # Skip if already owned (could be duplicates in heap)
            if self.ownership_grid[cy, cx] != -1:
                continue

            # Claim the pixel
            self.ownership_grid[cy, cx] = settlement_id
            settlement.owned_pixels.append((cx, cy))
            claimed_count += 1
            added_land += 1

            # Add all unclaimed neighbors to the frontier
            self._add_neighbors_to_frontier(settlement_id, cx, cy)

        return [claimed_count, added_land]

    def calculate_habitability_score(self, r, g, b):
        """Calculate habitability based on color gradient"""
        habitability_scale = [
            (np.array([214, 44, 32]), 0.01),  # #d62c20 - uninhabitable
            (np.array([219, 121, 0]), 0.2),  # #db7900
            (np.array([214, 199, 32]), 0.4),  # #d6c720
            (np.array([190, 214, 11]), 0.6),  # #bed60b
            (np.array([91, 191, 57]), 0.8),  # #5bbf39
            (np.array([19, 135, 19]), 1.0),  # #138713 - ideal
        ]

        target_rgb = np.array([r, g, b], dtype=float)

        # Find two closest colors and interpolate
        dists = [np.linalg.norm(target_rgb - scale_rgb) for scale_rgb, _ in habitability_scale]
        idx = np.argsort(dists)[:2]
        d1, d2 = dists[idx[0]], dists[idx[1]]
        v1, v2 = habitability_scale[idx[0]][1], habitability_scale[idx[1]][1]

        if d1 + d2 == 0:
            return (v1 + v2) / 2.0

        weight = d2 / (d1 + d2)
        return v1 * weight + v2 * (1 - weight)

    def calculate_swamp_score(self, r, g, b):
        """Penalizes pixels that are too close to the bad swamp color"""
        target_rgb = np.array([r, g, b], dtype=float)
        bad_color = np.array([24, 64, 11], dtype=float)  # #18400b

        dist = np.linalg.norm(target_rgb - bad_color)

        if dist < 40:
            return 0.01
        elif dist < 100:
            return (dist - 40) / 60.0
        else:
            return 1.0