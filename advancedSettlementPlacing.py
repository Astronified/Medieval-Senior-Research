import testSettlementPlacingSimple
import numpy as np
from PIL import Image
# You'll need scipy for the distance transform
from scipy.ndimage import distance_transform_edt


def load_image_as_array(path="riverTest.png"):
    """Loads the image and returns it as a float numpy array."""
    img = Image.open(path).convert("RGB")
    # Returns a (height, width, 3) array with values from 0.0 to 255.0
    return np.array(img, dtype=float)


def create_river_distance_map(img):
    """
    Pre-processes the image to create a distance transform map.
    Each pixel's value is its distance to the nearest blue river pixel.
    """
    print("Pre-calculating river distance map...")

    # 1. Define the blue color.
    #    Assuming standard (0, 0, 255) from a PIL image loaded as float.
    blue = np.array([0.0, 0.0, 255.0])

    # 2. Create a 2D boolean mask.
    #    It will be 'True' where the pixel is blue, 'False' otherwise.
    river_mask = np.all(img == blue, axis=2)

    # 3. Handle the "on top of river" case.
    #    If the mask is empty (no blue pixels), return a map full of 'infinity'.
    if not river_mask.any():
        print("Warning: No blue river pixels found in image.")
        return np.full(river_mask.shape, float('inf'))

    # 4. Compute the Euclidean Distance Transform (EDT).
    #    distance_transform_edt() calculates the distance from each 'False'
    #    pixel to the nearest 'True' pixel. We want the opposite,
    #    so we invert the mask.
    #
    distance_map = distance_transform_edt(np.invert(river_mask))

    print("Distance map calculated.")
    return distance_map


def distanceToRiver(distance_map, x, y):
    """
    Looks up the pre-calculated distance to the river at (x, y).
    """
    # Ensure coordinates are integers for array indexing
    xi, yi = int(round(x)), int(round(y))

    # Boundary check
    if 0 <= yi < distance_map.shape[0] and 0 <= xi < distance_map.shape[1]:
        return distance_map[yi, xi]
    else:
        # Point is off-map, return a very large distance
        return float('inf')


def mian():
    # --- Pre-processing Step ---
    # 1. Load the image with rivers
    img = load_image_as_array("riverTest.png")

    # 2. Create the distance map ONCE
    river_dist_map = create_river_distance_map(img)

    # --- Ranking Step ---
    # 3. Get the top 100 locations from your simple test
    print("Running simple placement test...")
    currentTop = testSettlementPlacingSimple.mian()

    ranked_by_river = []

    # 4. Re-rank the top 100 locations
    print("Running intensive river proximity test...")
    for i in currentTop:
        x = i[1]
        y = i[2]
        original_rank = i[0]

        # Get the distance from our pre-processed map
        dist = distanceToRiver(river_dist_map, x, y)

        # This is the key logic:
        # If distance is 0, it's ON the river, which is bad.
        # We set its sorting distance to 'inf' (infinity) so it goes
        # to the bottom of the list when we sort.
        if dist == 0:
            sortable_dist = float('inf')
        else:
            sortable_dist = dist

        # Store as [sortable_dist, x, y, original_rank]
        # We put 'sortable_dist' first to make sorting easy.
        ranked_by_river.append([sortable_dist, x, y, original_rank])

    # 5. Sort the list by 'sortable_dist' (item[0]), from smallest to largest


    finalls = []
    print("\nfinal 3:")
    for item in range(len( ranked_by_river)):
        # item = [distance, x, y, original_rank]
        if ranked_by_river[item][0] < 528 and ranked_by_river[item][0] > 132:
            finalls.append(ranked_by_river[item])
     #   print(f"  Dist: {item[0]:.2f}, X: {item[1]}, Y: {item[2]} (Original Rank: {item[3]})")
    finalls.sort(key=lambda x: x[3])
    print(finalls[0])
    print(finalls[1])
    print(finalls[2])

    return [finalls[0],finalls[1],finalls[2]] #3 for testing atm


# if __name__ == "__main__":
mian()

