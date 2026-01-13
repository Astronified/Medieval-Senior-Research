from PIL import Image, ImageDraw


def draw_pixels_on_map(input_path, output_path, pixel_data):

    img = Image.open(input_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    for x, y, color in pixel_data:
        if 0 <= x < img.width and 0 <= y < img.height:
            draw.point((x, y), fill=color)
    img.save(output_path)
    print(f"Saved modified map to {output_path}")


farms_to_draw = [
    (150, 150, (92, 61, 21)),
    (150, 151, (92, 61, 21)),
    (151, 151, (92, 61, 21)),
    (152, 151, (92, 61, 21)),
    (153, 151, (92, 61, 21)),
    (151, 150, (92, 61, 21)),
    (152, 150, (92, 61, 21)),
    (153, 150, (92, 61, 21)),
]

draw_pixels_on_map("smallCroppedHamlet.png", "drawTest.png", farms_to_draw)