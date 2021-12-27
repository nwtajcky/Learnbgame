def make_vertical_center_frame(
    song_path, bg_img_path, bar_color, bar_count, space_fraction, height_fraction,
    bar_heights, outpath):

    from PIL import Image, ImageDraw

    bg_img = Image.open(bg_img_path)
    bg_img.convert("RGB")

    size_x = bg_img.size[0]
    size_y = bg_img.size[1]

    max_bar_height = height_fraction * size_x / 2

    bars_img = Image.new("RGBA", [size_x, size_y])
    draw = ImageDraw.Draw(bars_img)

    space_per_bar = size_y / bar_count
    spacing = int(space_fraction * space_per_bar)
    bar_width = space_per_bar - (2 * spacing)


    for i in range(0, bar_count):
        bar_height = int(max_bar_height * bar_heights[i])

        left = size_x / 2
        right = size_x / 2 + bar_height
        top = space_per_bar * i + spacing
        bottom = top + bar_width

        draw.rectangle([left, bottom, right, top], fill=bar_color)

    for i in range(0, bar_count):
        bar_height = int(max_bar_height * bar_heights[i])

        right = size_x / 2
        left = size_x / 2 - bar_height
        top = space_per_bar * i + spacing
        bottom = top + bar_width

        draw.rectangle([left, bottom, right, top], fill=bar_color)

    bg_img.paste(bars_img, [0, 0], mask=bars_img)
    bg_img.save(outpath)