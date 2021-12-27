def make_top_frame(
    song_path, bg_img_path, bar_color, bar_count, space_fraction, height_fraction,
    bar_heights, outpath):

    from PIL import Image, ImageDraw

    bg_img = Image.open(bg_img_path)
    bg_img.convert("RGB")

    size_x = bg_img.size[0]
    size_y = bg_img.size[1]

    max_bar_height = height_fraction * size_y

    bars_img = Image.new("RGBA", [size_x, size_y])
    draw = ImageDraw.Draw(bars_img)

    space_per_bar = size_x / bar_count
    spacing = int(space_fraction * space_per_bar)
    bar_width = space_per_bar - (2 * spacing)

    for i in range(0, bar_count):
        bar_height = int(max_bar_height * bar_heights[i])

        left = (space_per_bar * i) + spacing
        bottom = bar_height
        right = left + bar_width
        top = 0

        draw.rectangle([left, bottom, right, top], fill=bar_color)

    bg_img.paste(bars_img, [0, 0], mask=bars_img)
    bg_img.save(outpath)