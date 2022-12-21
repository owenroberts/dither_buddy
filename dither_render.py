# algos based on https://tannerhelland.com/2012/12/28/dithering-eleven-algorithms-source-code.html

import bpy
import numpy
from time import perf_counter
from math import floor
from random import randint
import os

render = bpy.context.scene.render
scale = render.resolution_percentage / 100

WIDTH = int(render.resolution_x * scale)
HEIGHT = int(render.resolution_y * scale)

FILE_NAME = 'DitherExample.png'
FILE_PATH = '//{}'.format(FILE_NAME)
FILE_PATH_MODIFIED = '//DitherExampleModified.png'

algo_types = {
    '2d': {
        'dist_total': 1,
        'dist': [ [1, 1, 0] ]
    },
    'floyd_stein': {
        'dist_total': 16,
        'dist': [
            [7, 1, 0],
            [3, -1, 1], [5, 0, 1], [1, 1, 1]
        ]
    },
    'jjn': {
        'dist_total': 48,
        'dist': [
            [7, 1, 0], [5, 2, 0],
            [3, -2, 1], [5, -1, 1], [7, 0, 1], [5, 1, 1], [3, 2, 1],
            [1, -2, 2], [3, -1, 2], [5, 0, 2], [3, 1, 2], [1, 2, 2]
        ]
    },
    'stucki': {
        'dist_total': 42,
        'dist': [
            [8, 1, 0], [4, 2, 0],
            [2, -2, 1], [4, -1, 1], [8, 0, 1], [4, 1, 1], [2, 2, 1],
            [1, -2, 2], [2, -1, 2], [4, 0, 2], [2, 1, 2], [1, 2, 2]
        ]
    },
    'atkinson': {
        'dist_total': 8,
        'dist': [
            [1, 1, 0], [1, 2, 0],
            [1, -1, 1], [1, 0, 1], [1, 1, 1],
            [1, 0, 2], 
        ]
    },
    'burkes': {
        'dist_total': 32,
        'dist': [
            [8, 1, 0], [4, 2, 0],
            [2, -2, 1], [4, -1, 1], [8, 0, 1], [4, 1, 1], [2, 2, 1]
        ]
    },
    'sierra16': {
        'dist_total': 16,
        'dist': [
            [4, 1, 0], [3, 2, 0],
            [1, -2, 1], [2, -1, 1], [3, 0, 1], [2, 1, 1], [1, 2, 1],
        ]
    },
    'sierra4': {
        'dist_total': 4,
        'dist': [
            [2, 1, 0], 
            [2, -1, 1], [1, 0, 1],
        ]
    }
}

def render_and_modify(algo_type='floyd_stein', factor=4, rand_dist=False):
    render()
    image = load_image()
    pixel_array = numpy.array(image.pixels[:])
    new_pixels = dither(pixel_array, factor, algo_type=algo_type, rand_dist=rand_dist)
    image.pixels = new_pixels
    save_image(image, algo_type, factor, )
    
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

def get_rand_dist(tot, dist_num, max_dist=8):
    dist = [0] * dist_num
    for idx in range(dist_num):
        if tot <= idx:
            for i in range(idx, dist_num):
                dist[i] = 1
            break
        n = randint(1, max(1, min(tot - 1, max_dist)))
        dist[idx] = n
        tot = tot - n
    return dist

def get_dist_vals(dists, tot):
    dist_vals = {}
    for dist in dists:
        d = dist[0]
        dist_vals[d] = d / tot
    return dist_vals

def get_closest_color(val, max_val, factor):
    return round((factor * val / max_val)) * (max_val / factor)

def dither(arr, factor, algo_type="floyd_stein", rand_dist=False):

    if algo_type == 'ordered':
        dm = dither_matrix(factor)
        return ordered_dithering(arr, dm)

    tot = algo_types[algo_type]['dist_total']
    dist = algo_types[algo_type]['dist']

    if rand_dist:
        t = tot - 2 if algo_type == 'atkinson' else tot
        new_dists = get_rand_dist(t, len(dist))
        for idx in range(len(dist)):
            dist[idx][0] = new_dists[idx]

    dist_vals = get_dist_vals(dist, tot)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            i = get_pixel_index(x, y)
            val = arr[i]
            new_val = get_closest_color(val, 1, factor)
            set_arr_val(arr, i, new_val)          
            
            err =  val - new_val
            for d in dist:
                [_d, _x, _y] = d
                if _x > 0 and x >= WIDTH - abs(_x):
                    continue
                if _x < 0 and x <= abs(_x):
                    continue
                if _y > 0 and y >= HEIGHT - abs(_y):
                    continue

                pidx = get_pixel_index(x + _x, y + _y)
                v = arr[pidx] + err * dist_vals[_d]
                set_arr_val(arr, pidx, v)
    return arr

def set_arr_val(arr, idx, val):
    arr[idx] = val
    arr[idx+1] = val
    arr[idx+2] = val

def get_pixel_index(x, y):
    return (y * WIDTH + x) * 4

def dither_matrix(n:int):
    if n == 1:
        return numpy.array([[0]])
    else:
        first = (n ** 2) * dither_matrix(int(n/2))
        second = (n ** 2) * dither_matrix(int(n/2)) + 2
        third = (n ** 2) * dither_matrix(int(n/2)) + 3
        fourth = (n ** 2) * dither_matrix(int(n/2)) + 1
        first_col = numpy.concatenate((first, third), axis=0)
        second_col = numpy.concatenate((second, fourth), axis=0)
        return (1/n**2) * numpy.concatenate((first_col, second_col), axis=1)

def ordered_dithering(arr, dm):
    n = numpy.size(dm, axis=0)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            i = x % n
            j = y % n
            pidx = get_pixel_index(x, y)
            if arr[pidx] > dm[i][j]:
                set_arr_val(arr, pidx, 1)
            else:
                set_arr_val(arr, pidx, 0)
    return arr

def save_image(image, file_path):
    image.filepath_raw = file_path
    image.scale(WIDTH * 2, HEIGHT * 2)
    image.save()

def dither_image(factor, algo_type, rand_dist=False):
    image = load_image()
    pixel_array = numpy.array(image.pixels[:])
    new_pixels = dither(pixel_array, factor, algo_type, rand_dist=rand_dist)
    image.pixels = new_pixels
    file_path = f'//dither_tests/{algo_type}_factor{"_rand" if rand_dist else ""}.png'
    save_image(image, file_path)

def run_tests():
    render()
    dither_image(4, 'ordered')
    
    for algo_type in algo_types.keys():
        print('starting', algo_type)
        tic = perf_counter()
        dither_image(4, algo_type)
        toc = perf_counter()
        print(f"{algo_type} done in  {toc - tic:0.4f} seconds")

        tic = perf_counter()
        dither_image(4, algo_type, rand_dist=True)
        toc = perf_counter()
        print(f"{algo_type} done in  {toc - tic:0.4f} seconds")

    print('done')

def render_video(num_frames, algo_type, factor, rand_dist=False):
    file_dir = '//dither_frames/'
    files = []
    for f in range(num_frames):
        print('rendering frame', f, 'of', num_frames)
        bpy.context.scene.frame_set(f)
        render()
        image = load_image()
        pixel_array = numpy.array(image.pixels[:])
        new_pixels = dither(pixel_array, factor, algo_type, rand_dist=rand_dist)
        image.pixels = new_pixels
        file_path = f'{algo_type}_{str(factor)}_{str(f).rjust(4, "0")}.png'
        save_image(image, file_dir + file_path)
        files.append({ 'name': file_path })
    print('rendering done')

    temp_area_type = bpy.context.area.type
    bpy.context.area.type = 'SEQUENCE_EDITOR'
    bpy.ops.sequencer.image_strip_add(
        directory=file_dir, 
        files=files, 
        frame_start=1, 
        frame_end=1+num_frames, 
        channel=2
    )
    bpy.context.area.type = temp_area_type
    print('sequence added')



# render_and_modify()
# run_tests()
render_video(24 * (60 * 3 + 20), 'sierra4', 4, rand_dist=False)