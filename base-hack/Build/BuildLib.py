"""Library functions for the build procedure."""
import struct
from typing import BinaryIO

main_pointer_table_offset = 0x101C50
BLOCK_COLOR_SIZE = 64  # Bytes allocated to a block 32x32 image. Brute forcer says we can go as low as 0x25 bytes, but leaving some room for me to have left out something


def intf_to_float(intf):
    """Convert float as int format to float."""
    if intf == 0:
        return 0
    else:
        return struct.unpack("!f", bytes.fromhex("{:08X}".format(intf)))[0]


def float_to_hex(f):
    """Convert float to hex."""
    if f == 0:
        return "0x00000000"
    return hex(struct.unpack("<I", struct.pack("<f", f))[0])


def getFileData(rom: BinaryIO, table_index: int, file_index: int) -> tuple:
    """Get data of file from pointer table."""
    rom.seek(main_pointer_table_offset + (table_index * 4))
    table_address = main_pointer_table_offset + int.from_bytes(rom.read(4), "big")
    rom.seek(table_address + (file_index * 4))
    file_address = main_pointer_table_offset + int.from_bytes(rom.read(4), "big")
    file_end = main_pointer_table_offset + int.from_bytes(rom.read(4), "big")
    file_size = file_end - file_address
    rom.seek(file_address)
    compressed = int.from_bytes(rom.read(2), "big") == 0x1F8B
    return file_address, file_size, compressed


icon_db = {
    0x0: "waterfall_tall",
    0x1: "waterfall_short",
    0x2: "water",
    0x3: "lava",
    0x4: "sparkles",
    0x5: "pop_explosion",
    0x6: "lava_explosion",
    0x7: "green_leaf?",
    0x8: "brown_smoke_explosion",
    0x9: "small_explosion",
    0xA: "solar_flare?",
    0xB: "splash",
    0xC: "bubble",
    0xD: "purple_sparkle",
    0xE: "yellow_sparkle",
    0xF: "green_sparkle",
    0x10: "purple_sparkle",
    0x11: "yellow_sparkle",
    0x12: "green_sparkle",
    0x13: "large_smoke_explosion",
    0x14: "pink_implosion",
    0x15: "brown_horizontal_spinning_plank",
    0x16: "birch_horizontal_spinning_plank",
    0x17: "brown_vertical_spinning_plank",
    0x18: "star_water_ripple",
    0x19: "circle_water_ripple",
    0x1A: "small_smoke_explosion",
    0x1B: "static_star",
    0x1C: "static_z",
    0x1D: "white_flare?",
    0x1E: "static_rain?",
    0x1F: "medium_smoke_explosion",
    0x20: "bouncing_melon",
    0x21: "vertical_rolling_melon",
    0x22: "red_flare?",
    0x23: "sparks",
    0x24: "peanut",
    0x25: "star_flare?",
    0x26: "peanut_shell",
    0x27: "small_explosion",
    0x28: "large_smoke_implosion",
    0x29: "blue_lazer",
    0x2A: "pineapple",
    0x2B: "fireball",
    0x2C: "orange",
    0x2D: "grape",
    0x2E: "grape_splatter",
    0x2F: "tnt_sparkle",
    0x30: "fire_explosion",
    0x31: "small_fireball",
    0x32: "diddy_coin",
    0x33: "chunky_coin",
    0x34: "lanky_coin",
    0x35: "dk_coin",
    0x36: "tiny_coin",
    0x37: "dk_coloured_banana",
    0x38: "film",
    0x39: "bouncing_orange",
    0x3A: "crystal_coconut",
    0x3B: "gb",
    0x3C: "banana_medal",
    0x3D: "diddy_coloured_banana",
    0x3E: "chunky_coloured_banana",
    0x3F: "lanky_coloured_banana",
    0x40: "dk_coloured_banana",
    0x41: "tiny_coloured_banana",
    0x42: "exploded_krash_barrel_enemy",
    0x43: "white_explosion_thing",
    0x44: "coconut",
    0x45: "coconut_shell",
    0x46: "spinning_watermelon_slice",
    0x47: "tooth",
    0x48: "ammo_crate",
    0x49: "race_coin",
    0x4A: "lanky_bp",
    0x4B: "cannonball",
    0x4C: "crystal_coconut",
    0x4D: "feather",
    0x4E: "guitar_gazump",
    0x4F: "bongo_blast",
    0x50: "saxophone",
    0x51: "triangle",
    0x52: "trombone",
    0x53: "waving_yellow_double_eighth_note",
    0x54: "waving_yellow_single_eighth_note",
    0x55: "waving_green_single_eighth_note",
    0x56: "waving_purple_double_eighth_note",
    0x57: "waving_red_double_eighth_note",
    0x58: "waving_red_single_eighth_note",
    0x59: "waving_white_double_eighth_note",
    0x5A: "diddy_bp",
    0x5B: "chunky_bp",
    0x5C: "dk_bp",
    0x5D: "tiny_bp",
    0x5E: "spinning_sparkle",
    0x5F: "static_rain?",
    0x60: "translucent_water",
    0x61: "unk61",
    0x62: "black_screen",
    0x63: "white_cloud",
    0x64: "thin_lazer",
    0x65: "blue_bubble",
    0x66: "white_faded_circle",
    0x67: "white_circle",
    0x68: "grape_particle?",
    0x69: "spinning_blue_sparkle",
    0x6A: "white_smoke_explosion",
    0x6B: "l-r_joystick",
    0x6C: "fire_wall",
    0x6D: "static_rain_bubble",
    0x6E: "a_button",
    0x6F: "b_button",
    0x70: "z_button",
    0x71: "c_down_button",
    0x72: "c_up_button",
    0x73: "c_left_button",
    0x74: "acid",
    0x75: "acid_explosion",
    0x76: "race_hoop",
    0x77: "acid_goop?",
    0x78: "unk78",
    0x79: "broken_bridge?",
    0x7A: "white_pole?",
    0x7B: "bridge_chip?",
    0x7C: "wooden_beam_with_rivets",
    0x7D: "chunky_bunch",
    0x7E: "diddy_bunch",
    0x7F: "lanky_bunch",
    0x80: "dk_bunch",
    0x81: "tiny_bunch",
    0x82: "chunky_balloon",
    0x83: "diddy_balloon",
    0x84: "dk_balloon",
    0x85: "lanky_balloon",
    0x86: "tiny_balloon",
    0x87: "r_button",
    0x88: "l_button",
    0x89: "fairy",
    0x8A: "boss_key",
    0x8B: "crown",
    0x8C: "rareware_coin",
    0x8D: "nintendo_coin",
    0x8E: "no_symbol",
    0x8F: "headphones",
    0x90: "opaque_blue_water",
    0x91: "start_button",
    0x92: "white_question_mark",
    0x93: "candy_face",
    0x94: "cranky_face",
    0x95: "snide_face",
    0x96: "funky_face",
    0x97: "left_arrow",
    0x98: "white_spark?",
    0x99: "black_boulder_chunk",
    0x9A: "green_boulder_chunk",
    0x9B: "wood_chip",
    0x9C: "snowflake/dandelion",
    0x9D: "static_water?",
    0x9E: "spinning_leaf",
    0x9F: "flashing_water?",
    0xA0: "rainbow_coin",
    0xA1: "shockwave_orange_particle",
    0xA2: "implosion?",
    0xA3: "rareware_employee_face",
    0xA4: "smoke",
    0xA5: "static_smoke?",
    0xA6: "barrel_bottom_chunk",
    0xA7: "scoff_face",
    0xA8: "multicoloured_bunch",
    0xA9: "dk_face",
    0xAA: "diddy_face",
    0xAB: "lanky_face",
    0xAC: "tiny_face",
    0xAD: "chunky_face",
    0xAE: "fairy_tick",
    0xAF: "wrinkly",
}
