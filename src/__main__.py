#!/usr/bin/env python3
# coding: utf-8

from PIL import Image, ImageDraw, ImageFont, ImageChops
import numpy as np
from decimal import Decimal, ROUND_HALF_UP
from time import time

_round = lambda f, r=ROUND_HALF_UP: int(Decimal(str(f)).quantize(Decimal("0"), rounding=r))
rgb = lambda r, g, b: (r, g, b)


def get_gradient_2d(start, stop, width, height, is_horizontal=False):
    if is_horizontal:
        return np.tile(np.linspace(start, stop, width), (height, 1))
    else:
        return np.tile(np.linspace(start, stop, height), (width, 1)).T


def get_gradient_3d(width, height, start_list, stop_list, is_horizontal_list=(False, False, False)):
    result = np.zeros((height, width, len(start_list)), dtype=np.float)
    for i, (start, stop, is_horizontal) in enumerate(zip(start_list, stop_list, is_horizontal_list)):
        result[:, :, i] = get_gradient_2d(start, stop, width, height, is_horizontal)
    return result


def createLinearGradient(steps, width, height):
    result = np.zeros((0, width, len(steps[0])), dtype=np.float)
    for i, k in enumerate(steps.keys()):
        if i == 0:
            continue
        pk = list(steps.keys())[i-1]
        h = _round(height*(k-pk))
        array = get_gradient_3d(width, h, steps[pk], steps[k])
        result = np.vstack([result, array])
    return result


def genBaseImage(width=1500, height=150):
    downerSilverArray = createLinearGradient({
        0.0: rgb(0, 15, 36),
        0.10: rgb(255, 255, 255),
        0.18: rgb(55, 58, 59),
        0.25: rgb(55, 58, 59),
        0.5: rgb(200, 200, 200),
        0.75: rgb(55, 58, 59),
        0.85: rgb(25, 20, 31),
        0.91: rgb(240, 240, 240),
        0.95: rgb(166, 175, 194),
        1: rgb(50, 50, 50)
    }, width=width, height=height)
    goldArray = createLinearGradient({
        0: rgb(253, 241, 0),
        0.25: rgb(245, 253, 187),
        0.4: rgb(255, 255, 255),
        0.75: rgb(253, 219, 9),
        0.9: rgb(127, 53, 0),
        1: rgb(243, 196, 11)
    }, width=width, height=height)
    redArray = createLinearGradient({
        0: rgb(230, 0, 0),
        0.5: rgb(123, 0, 0),
        0.51: rgb(240, 0, 0),
        1: rgb(5, 0, 0)
    }, width=width, height=height)
    strokeRedArray = createLinearGradient({
        0: rgb(255, 100, 0),
        0.5: rgb(123, 0, 0),
        0.51: rgb(240, 0, 0),
        1: rgb(5, 0, 0)
    }, width=width, height=height)
    silver2Array = createLinearGradient({
        0: rgb(245, 246, 248),
        0.15: rgb(255, 255, 255),
        0.35: rgb(195, 213, 220),
        0.5: rgb(160, 190, 201),
        0.51: rgb(160, 190, 201),
        0.52: rgb(196, 215, 222),
        1.0: rgb(255, 255, 255)
    }, width=width, height=height)
    navyArray = createLinearGradient({
        0: rgb(16, 25, 58),
        0.03: rgb(255, 255, 255),
        0.08: rgb(16, 25, 58),
        0.2: rgb(16, 25, 58),
        1: rgb(16, 25, 58)
    }, width=width, height=height)
    result = {
        "downerSilver": Image.fromarray(np.uint8(downerSilverArray)).crop((0, 0, width, height)),
        "gold": Image.fromarray(np.uint8(goldArray)).crop((0, 0, width, height)),
        "red": Image.fromarray(np.uint8(redArray)).crop((0, 0, width, height)),
        "strokeRed": Image.fromarray(np.uint8(strokeRedArray)).crop((0, 0, width, height)),
        "silver2": Image.fromarray(np.uint8(silver2Array)).crop((0, 0, width, height)),
        "strokeNavy": Image.fromarray(np.uint8(navyArray)).crop((0, 0, width, height)),  # Width: 7
        "baseStrokeBlack": Image.new("RGBA", (width, height), rgb(0, 0, 0)).crop((0, 0, width, height)),  # Width: 17
        "strokeBlack": Image.new("RGBA", (width, height), rgb(16, 25, 58)).crop((0, 0, width, height)),  # Width: 17
        "strokeWhite": Image.new("RGBA", (width, height), rgb(221, 221, 221)).crop((0, 0, width, height)),  # Width: 8
        "baseStrokeWhite": Image.new("RGBA", (width, height), rgb(255, 255, 255)).crop((0, 0, width, height))  # Width: 8
    }
    for k in result.keys():
        result[k].putalpha(255)
    return result


def genimage(word_a="5000兆円", word_b="欲しい!", max_width=1500, height=300,
             bg="white", subset=70, base=genBaseImage()):
    width = max_width
    alpha = (0, 0, 0, 0)
    leftmargin = 50
    font_upper = ImageFont.truetype("fonts/notobk-subset.otf", 100)
    font_downer = ImageFont.truetype("fonts/notoserifbk-subset.otf", 100)

    # Prepare mask
    mask_base = Image.new("L", (width, _round(height/2)), 0)
    # Prepare mask - Upper
    mask_img_upper = list()
    upper_data = [
        [
            (4, 4), (4, 4), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)
        ], [
            22, 20, 16, 10, 6, 6, 4, 0
        ], [
            "baseStrokeBlack",
            "downerSilver",
            "baseStrokeBlack",
            "gold",
            "baseStrokeBlack",
            "baseStrokeWhite",
            "strokeRed",
            "red",
        ]
    ]
    for pos, stroke, color in zip(upper_data[0], upper_data[1], upper_data[2]):
        mask_img_upper.append(mask_base.copy())
        mask_draw_upper = ImageDraw.Draw(mask_img_upper[-1])
        mask_draw_upper.text((pos[0]+leftmargin, pos[1]), word_a, font=font_upper, fill=255, stroke_width=stroke)

    # Prepare mask - Downer
    mask_img_downer = list()
    downer_data = [
        [
            (5, 2), (5, 2), (0, 0), (0, 0), (0, 0), (0, -3)
        ], [
            22, 19, 17, 8, 7, 0
        ], [
            "baseStrokeBlack",
            "downerSilver",
            "strokeBlack",
            "strokeWhite",
            "strokeNavy",
            "silver2"
        ]
    ]
    for pos, stroke, color in zip(downer_data[0], downer_data[1], downer_data[2]):
        mask_img_downer.append(mask_base.copy())
        mask_draw_downer = ImageDraw.Draw(mask_img_downer[-1])
        mask_draw_downer.text((pos[0]+leftmargin, pos[1]), word_b, font=font_downer, fill=255, stroke_width=stroke)

    # Draw text - Upper
    img_upper = Image.new("RGBA", (width, _round(height/2)), alpha)

    for i, (pos, stroke, color) in enumerate(zip(upper_data[0], upper_data[1], upper_data[2])):
        img_upper_part = Image.new("RGBA", (width, _round(height/2)), alpha)
        img_upper_part.paste(base[color], (0, 0), mask=mask_img_upper[i])
        img_upper.alpha_composite(img_upper_part)

    # Draw text - Downer
    img_downer = Image.new("RGBA", (width, _round(height/2)), alpha)
    for i, (pos, stroke, color) in enumerate(zip(downer_data[0], downer_data[1], downer_data[2])):
        img_downer_part = Image.new("RGBA", (width, _round(height/2)), alpha)
        img_downer_part.paste(base[color], (0, 0), mask=mask_img_downer[i])
        img_downer.alpha_composite(img_downer_part)

    # finish
    previmg = Image.new("RGBA", (width, height), alpha)
    previmg.alpha_composite(img_upper, (0, 0), (0, 0))
    previmg.alpha_composite(img_downer, (subset, _round(height/2)), (0, 0))
    croprange = previmg.convert("RGB").getbbox()
    img = previmg.crop(croprange)

    return img


def main():
    t = time()
    width = 1500
    height = 300
    base = genBaseImage(width=width, height=_round(height/2))
    i = genimage("5000兆円", max_width=width, height=height, bg=(0, 0, 0, 0), base=base)
    i.save("test.png")
    print("Time :", time()-t)


if __name__ == "__main__":
    main()