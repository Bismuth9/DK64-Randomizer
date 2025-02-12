"""Convert RGB colors into a kong color palette."""
import gzip
import zlib
import math
import os
from PIL import Image
from BuildLib import main_pointer_table_offset

color_palettes = [
    {"kong": "dk", "zones": [{"zone": "base", "image": 3724, "colors": ["#2da1ad"], "fill_type": "block"}]},  # 2da1ad
    {"kong": "diddy", "zones": [{"zone": "cap_shirt", "image": 3686, "colors": ["#00ff37"], "fill_type": "block"}]},
    {"kong": "lanky", "zones": [{"zone": "overalls", "image": 3689, "colors": ["#3e1c73"], "fill_type": "block"}, {"zone": "patch", "image": 3734, "colors": ["#3e1c73"], "fill_type": "patch"}]},
    {"kong": "tiny", "zones": [{"zone": "overalls", "image": 6014, "colors": ["#ff3beb"], "fill_type": "block"}]},
    {
        "kong": "chunky",
        "zones": [
            {"zone": "shirt_back", "image": 3769, "colors": ["#FF0000", "#FFFFFF"], "fill_type": "checkered"},
            {"zone": "shirt_front", "image": 3687, "colors": ["#000000"], "fill_type": "block"},
        ],
    },
    {
        "kong": "discochunky",
        "zones": [{"zone": "shirt", "image": 3777, "colors": ["#00237D"], "fill_type": "sparkle"}, {"zone": "gloves", "image": 3778, "colors": ["#FFFFFF"], "fill_type": "sparkle"}],
    },
    {"kong": "krusha", "zones": [{"zone": "skin", "image": 4971, "colors": ["#003631"], "fill_type": "block"}, {"zone": "belt", "image": 4966, "colors": ["#FFD700"], "fill_type": "block"}]},
    {"kong": "rambi", "zones": [{"zone": "top", "image": 3826, "colors": ["#070657"], "fill_type": "block"}]},
    {"kong": "enguarde", "zones": [{"zone": "top", "image": 3847, "colors": ["FF0000"], "fill_type": "block"}]},
]


def convertRGBAToBytearray(rgba_lst):
    """Convert RGBA list with 4 items (r,g,b,a) to a two-byte array in RGBA5551 format."""
    twobyte = (rgba_lst[0] << 11) | (rgba_lst[1] << 6) | (rgba_lst[2] << 1) | rgba_lst[3]
    lower = twobyte % 256
    upper = int(twobyte / 256) % 256
    return [upper, lower]


def convertColors():
    """Convert color into RGBA5551 format."""
    for palette in color_palettes:
        for zone in palette["zones"]:
            rgba_list = []
            if zone["fill_type"] == "checkered" or zone["fill_type"] == "radial":
                lim = 2
            else:
                lim = 1
            for x in range(lim):
                rgba = [0, 0, 0, 1]
                for i in range(3):
                    if zone["fill_type"] == "radial":
                        val = int(int(f"0x{zone['colors'][0][(2*i)+1:(2*i)+3]}", 16) * (1 / 8))
                        if x == 1:
                            val = int(val * 2)
                    else:
                        val = int(int(f"0x{zone['colors'][x][(2*i)+1:(2*i)+3]}", 16) * (1 / 8))
                    if val < 0:
                        val = 0
                    elif val > 31:
                        val = 31
                    rgba[i] = val
                rgba_list.append(rgba)
            bytes_array = []
            if zone["fill_type"] in ("block", "kong"):
                ext = convertRGBAToBytearray(rgba_list[0])
                for x in range(32 * 32):
                    bytes_array.extend(ext)
            elif zone["fill_type"] == "radial":
                cen_x = 15.5
                cen_y = 15.5
                max_dist = (cen_x * cen_x) + (cen_y * cen_y)
                channel_diffs = [0, 0, 0]
                for i in range(3):
                    channel_diffs[i] = rgba_list[1][i] - rgba_list[0][i]
                for y in range(32):
                    for x in range(32):
                        dx = cen_x - x
                        dy = cen_y - y
                        dst = (dx * dx) + (dy * dy)
                        proportion = 1 - (dst / max_dist)
                        prop = [0, 0, 0, 1]
                        for i in range(3):
                            val = int((channel_diffs[i] * proportion) + rgba_list[0][i])
                            if val < 0:
                                val = 0
                            elif val > 31:
                                val = 31
                            prop[i] = val
                        ext = convertRGBAToBytearray(prop)
                        bytes_array.extend(ext)
            elif zone["fill_type"] == "checkered":
                for size_mult in range(3):
                    dim_s = int(32 / math.pow(2, size_mult))
                    pol_s = int(dim_s / 8)
                    for y in range(dim_s):
                        for x in range(dim_s):
                            y_offset = 0
                            if size_mult == 1:
                                y_offset = 1
                            color_polarity_x = int(x / pol_s) % 2
                            color_polarity_y = int((y + y_offset) / pol_s) % 2
                            color_polarity = (color_polarity_x + color_polarity_y) % 2
                            ext = convertRGBAToBytearray(rgba_list[color_polarity])
                            bytes_array.extend(ext)
                for i in range(18):
                    ext = convertRGBAToBytearray(rgba_list[1])
                    bytes_array.extend(ext)
                for i in range(4):
                    ext = convertRGBAToBytearray([0, 0, 0, 0])
                    bytes_array.extend(ext)
                for i in range(3):
                    ext = convertRGBAToBytearray(rgba_list[1])
                    bytes_array.extend(ext)
                for i in range(3):
                    ext = convertRGBAToBytearray([0, 0, 0, 0])
                    bytes_array.extend(ext)
            elif zone["fill_type"] == "patch":
                for size_mult in range(3):
                    patch_start_x = int(6 / math.pow(2, size_mult))
                    patch_start_y = int(8 / math.pow(2, size_mult))
                    # print(f"{patch_start_x} | {patch_start_y}")
                    patch_size = 3 - size_mult
                    if patch_size == 3:
                        patch_size = 5
                    dim_s = int(32 / math.pow(2, size_mult))
                    for y in range(dim_s):
                        for x in range(dim_s):
                            is_block = True  # Set to false to generate patch
                            if x < patch_start_x:
                                is_block = True
                            elif x >= patch_start_x + (4 * patch_size):
                                is_block = True
                            elif y < patch_start_y:
                                is_block = True
                            elif y >= patch_start_y + (3 * patch_size):
                                is_block = True
                            if is_block:
                                ext = convertRGBAToBytearray(rgba_list[0])
                            else:
                                delta_x = x - patch_start_x
                                delta_y = y - patch_start_y
                                color_polarity_x = int(delta_x / patch_size) % 2
                                color_polarity_y = int(delta_y / patch_size) % 2
                                color_polarity = (color_polarity_x + color_polarity_y) % 2
                                patch_rgba = [31, 31, 31, 1]
                                if color_polarity == 1:
                                    patch_rgba = [31, 0, 0, 1]
                                ext = convertRGBAToBytearray(patch_rgba)
                            bytes_array.extend(ext)
                for i in range(18):
                    ext = convertRGBAToBytearray(rgba_list[0])
                    bytes_array.extend(ext)
                for i in range(4):
                    ext = convertRGBAToBytearray([0, 0, 0, 0])
                    bytes_array.extend(ext)
                for i in range(3):
                    ext = convertRGBAToBytearray(rgba_list[0])
                    bytes_array.extend(ext)
                for i in range(3):
                    ext = convertRGBAToBytearray([0, 0, 0, 0])
                    bytes_array.extend(ext)
            elif zone["fill_type"] == "sparkle":
                dim_rgba = []
                for channel_index, channel in enumerate(rgba_list[0]):
                    if channel_index == 3:
                        dim_rgba.append(1)
                    else:
                        dim_channel = 0.8 * channel
                        dim_rgba.append(int(dim_channel))
                for y in range(32):
                    for x in range(32):
                        pix_rgba = []
                        if x == 31:
                            pix_rgba = rgba_list[0].copy()
                        else:
                            for channel_index in range(4):
                                if channel_index == 3:
                                    pix_channel = 1
                                else:
                                    diff = rgba_list[0][channel_index] - dim_rgba[channel_index]
                                    applied_diff = int(diff * (x / 31))
                                    pix_channel = dim_rgba[channel_index] + applied_diff
                                    if pix_channel < 0:
                                        pix_channel = 0
                                    if pix_channel > 31:
                                        pix_channel = 31
                                pix_rgba.append(pix_channel)
                        sparkle_px = [[28, 5], [27, 10], [21, 11], [25, 14], [23, 15], [23, 16], [26, 18], [20, 19], [25, 25]]
                        for px in sparkle_px:
                            if px[0] == x and px[1] == y:
                                pix_rgba = [0xFF, 0xFF, 0xFF, 1]
                        bytes_array.extend(convertRGBAToBytearray(pix_rgba))

            with open(f"{palette['kong']}{zone['zone']}.bin", "wb") as fh:
                fh.write(bytearray(bytes_array))

            with open("rom/dk64-randomizer-base-dev.z64", "r+b") as fh:
                fh.seek(main_pointer_table_offset + (25 * 0x4))
                texture_table = main_pointer_table_offset + int.from_bytes(fh.read(4), "big")
                fh.seek(texture_table + (zone["image"] * 4))
                write_point = main_pointer_table_offset + int.from_bytes(fh.read(4), "big")
                fh.seek(write_point)
                comp = gzip.compress(bytearray(bytes_array), compresslevel=9)
                fh.write(comp)


def hueShift(im, amount):
    """Apply a hue shift on an image."""
    hsv_im = im.convert("HSV")
    im_px = im.load()
    w, h = hsv_im.size
    hsv_px = hsv_im.load()
    for y in range(h):
        for x in range(w):
            old = list(hsv_px[x, y]).copy()
            old[0] = (old[0] + amount) % 360
            hsv_px[x, y] = (old[0], old[1], old[2])
    rgb_im = hsv_im.convert("RGB")
    rgb_px = rgb_im.load()
    for y in range(h):
        for x in range(w):
            new = list(rgb_px[x, y])
            new.append(list(im_px[x, y])[3])
            im_px[x, y] = (new[0], new[1], new[2], new[3])
    return im


def applyMelonMask(shift: int):
    """Apply a mask to the melon sprites."""
    with open("rom/dk64-randomizer-base-dev.z64", "r+b") as fh:
        data = {
            7: (0x13C, 0x147),
            14: (0x5A, 0x5D),
            25: (0x17B2, 0x17B2),
        }
        for table in data:
            fh.seek(main_pointer_table_offset + (table * 0x4))
            texture_table = main_pointer_table_offset + int.from_bytes(fh.read(4), "big")
            table_data = list(data[table])
            for img in range(table_data[0], table_data[1] + 1):
                fh.seek(texture_table + (img * 4))
                file_start = main_pointer_table_offset + int.from_bytes(fh.read(4), "big")
                file_end = main_pointer_table_offset + int.from_bytes(fh.read(4), "big")
                file_size = file_end - file_start
                fh.seek(file_start)
                file_data = fh.read(file_size)
                if table != 7:
                    file_data = zlib.decompress(file_data, (15 + 32))
                temp_name = "temp.bin"
                with open(temp_name, "wb") as fg:
                    fg.write(file_data)
                if table == 25 and img == 0x17B2:
                    dims = (32, 32)
                else:
                    dims = (48, 42)
                melon_im = Image.new(mode="RGBA", size=dims)
                px = melon_im.load()
                with open(temp_name, "rb") as fg:
                    for y in range(dims[1]):
                        for x in range(dims[0]):
                            px_info = int.from_bytes(fg.read(2), "big")
                            px_red = int(((px_info >> 11) << 3) & 0xFF)
                            px_green = int(((px_info >> 6) << 3) & 0xFF)
                            px_blue = int(((px_info >> 1) << 3) & 0xFF)
                            px_alpha = int((px_info & 1) * 255)
                            px[x, y] = (px_red, px_green, px_blue, px_alpha)
                    melon_im = hueShift(melon_im, shift)
                with open(temp_name, "wb") as fg:
                    for y in range(dims[1]):
                        for x in range(dims[0]):
                            px_info = list(px[x, y])
                            px_red = (px_info[0] >> 3) << 11
                            px_green = (px_info[1] >> 3) << 6
                            px_blue = (px_info[2] >> 3) << 1
                            px_alpha = 1 if px_info[3] > 0 else 0
                            px_word = px_red | px_green | px_blue | px_alpha
                            fg.write(px_word.to_bytes(2, "big"))
                with open(temp_name, "rb") as fg:
                    new_data = fg.read()
                    if table != 7:
                        new_data = gzip.compress(new_data, compresslevel=9)
                    fh.seek(file_start)
                    fh.write(new_data)
                if os.path.exists(temp_name):
                    os.remove(temp_name)


applyMelonMask(60)
convertColors()
