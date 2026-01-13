import PIL.Image
from PIL import Image


def get_crop_strict(input_path, center_x, center_y, size=100):
    """
    Crops a square of 'size' around (center_x, center_y).
    Raises ValueError if the crop area goes out of bounds.
    Returns the cropped PIL Image object.
    """
    img = Image.open(input_path)
    img_w, img_h = img.size
    half_size = size // 2

    left = center_x - half_size
    upper = center_y - half_size
    right = left + size
    lower = upper + size
    if left < 0:
        raise ValueError(f"Error: Crop extends past LEFT edge by {abs(left)} pixels.")
    if upper < 0:
        raise ValueError(f"Error: Crop extends past TOP edge by {abs(upper)} pixels.")
    if right > img_w:
        raise ValueError(f"Error: Crop extends past RIGHT edge by {right - img_w} pixels.")
    if lower > img_h:
        raise ValueError(f"Error: Crop extends past BOTTOM edge by {lower - img_h} pixels.")

    crop_box = (left, upper, right, lower)
    cropped_img = img.crop(crop_box)
    cropped_img.save("smallCroppedHamlet.png")




try:
    my_crop = get_crop_strict("riverTest.png", center_x=571, center_y=1747, size=300)

except ValueError as e:
    print(e)
