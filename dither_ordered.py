# https://github.com/mies47/MM-ordered_dithering/blob/master/main.py

import bpy
import numpy as np
import sys

render = bpy.context.scene.render
scale = render.resolution_percentage / 100
WIDTH = int(render.resolution_x * scale)
HEIGHT = int(render.resolution_y * scale)
n = int(8)

DIR = '/Users/owenroberts/gd/art/remember/diarrhea/vfx'

FILE_NAME = '/OrderedDitherExample_' + str(n) + '.png'
FILE_PATH = '//{}'.format(FILE_NAME)
FILE_PATH_MODIFIED = '//OrderedDitherExample_' + str(n) + '.png'
FILE_NAME_MODIFIED = '//OrderedDitherExample_' + str(n) + '.png'

def render_and_modify():
    render()
    dm = dither_matrix(n)
    image = load_image()
    image_pixels = np.array(image.pixels[:])
    new_pixels = ordered_dithering(image_pixels, dm)
    image.pixels = new_pixels
    save_image(image)

def render():
    previous_path = bpy.context.scene.render.filepath
    bpy.context.scene.render.filepath = FILE_PATH
    bpy.ops.render.render(write_still= True)
    bpy.context.scene.render.filepath = previous_path

def load_image():
    try:
        bpy.data.images.remove(bpy.data.images[FILE_NAME])
    except:
        pass
    return bpy.data.images.load(FILE_PATH)

def save_image(image):
    image.filepath_raw = FILE_PATH_MODIFIED
    image.scale( WIDTH * 2, HEIGHT * 2)
    image.save()

def dither_matrix(n:int):
    if n == 1:
        return np.array([[0]])
    else:
        first = (n ** 2) * dither_matrix(int(n/2))
        second = (n ** 2) * dither_matrix(int(n/2)) + 2
        third = (n ** 2) * dither_matrix(int(n/2)) + 3
        fourth = (n ** 2) * dither_matrix(int(n/2)) + 1
        first_col = np.concatenate((first, third), axis=0)
        second_col = np.concatenate((second, fourth), axis=0)
        return (1/n**2) * np.concatenate((first_col, second_col), axis=1)

def set_arr_val(arr, idx, val):
    arr[idx] = val
    arr[idx+1] = val
    arr[idx+2] = val

def get_pixel_index(x, y):
    return (y * WIDTH + x) * 4

def ordered_dithering(img_pixel:np.array, dither_m:np.array):
    n = np.size(dither_m, axis=0)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            i = x % n
            j = y % n
            pidx = get_pixel_index(x, y)
            if img_pixel[pidx] > dither_m[i][j]:
                set_arr_val(img_pixel, pidx, 1)
            else:
                set_arr_val(img_pixel, pidx, 0)
    return img_pixel

render_and_modify()



