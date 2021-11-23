import os
import math
import numpy
import PySimpleGUI
from tkinter import *
from PIL import ImageTk, Image

RESOURCES_FOLDER = './resources'
MAP_TEST = 'map_test.txt'
PICKAXE = 'pickaxe.png'
MESSAGE = 'message.png'
BOMB = 'bomb.png'

UTILS = {'cell_count': 0,
         'cell_size': 0,
         'grid_size': 400,
         'canvas': False,
         'window': False,
         'player_pos': [0, 0],
         'cell_map': False,
         'safe_map': False,
         'visited_map': False,
         'messages_coords': False,
         'bombs_coords': False,
         }

APP_FONT = 'Any 16'
PySimpleGUI.theme('DarkGrey5')
SCORE = 0


def draw_grid():
    UTILS['canvas'].TKCanvas.create_rectangle(
        1, 1, UTILS['grid_size'], UTILS['grid_size'], outline='BLACK', width=1)

    for idx in range(UTILS['cell_count']):
        UTILS['canvas'].TKCanvas.create_line(
            ((UTILS['cell_size'] * idx),
             0), ((UTILS['cell_size'] * idx), UTILS['grid_size']),
            fill='BLACK', width=1)
        UTILS['canvas'].TKCanvas.create_line(
            (0, (UTILS['cell_size'] * idx)
             ), (UTILS['grid_size'], (UTILS['cell_size'] * idx)),
            fill='BLACK', width=1)


def draw_image(x, y, resource):
    x *= UTILS['cell_size']
    y *= UTILS['cell_size']

    image = Image.open(os.path.join(RESOURCES_FOLDER, resource))
    image = image.resize(
        (UTILS['cell_size'], UTILS['cell_size']), Image.ANTIALIAS)
    photoImage = ImageTk.PhotoImage(image)
    UTILS['canvas'].TKCanvas.create_image(
        x, y, image=photoImage, anchor='nw')


def draw_cell(x, y, color='GREY'):
    x *= UTILS['cell_size']
    y *= UTILS['cell_size']

    UTILS['canvas'].TKCanvas.create_rectangle(
        x, y, x + UTILS['cell_size'], y + UTILS['cell_size'],
        outline='BLACK', fill=color, width=1)


def initialize_map():
    UTILS['cell_map'] = numpy.zeros(
        (UTILS['cell_count'], UTILS['cell_count']), dtype=int)
    UTILS['visited_map'] = numpy.zeros(
        (UTILS['cell_count'], UTILS['cell_count']), dtype=int)

    layout = [[PySimpleGUI.Canvas(size=(UTILS['grid_size'], UTILS['grid_size']),
                                  background_color='WHITE',
                                  key='canvas')],
              [PySimpleGUI.Exit(font=APP_FONT),
               PySimpleGUI.Text('', key='-SCORE-',
                                font=APP_FONT, size=(15, 1)),
               PySimpleGUI.Button('Restart', font=APP_FONT)]]

    UTILS['window'] = PySimpleGUI.Window('Minefield v1.0', layout, resizable=True, finalize=True,
                                         return_keyboard_events=True)
    UTILS['canvas'] = UTILS['window']['canvas']

    image = Image.open(os.path.join(RESOURCES_FOLDER, PICKAXE))
    image = image.resize(
        (UTILS['cell_size'], UTILS['cell_size']), Image.ANTIALIAS)
    photoImage = ImageTk.PhotoImage(image)
    UTILS['canvas'].TKCanvas.create_image(
        UTILS['player_pos'][0], UTILS['player_pos'][1], image=photoImage, anchor='nw')

    draw_grid()
    draw_map()


def draw_map():
    for i in range(UTILS['cell_count']):
        for j in range(UTILS['cell_count']):
            if UTILS['visited_map'][i][j] == 1:
                draw_cell(i, j)
            if (i, j) in UTILS['messages_coords']:
                draw_cell(i, j, 'GREEN')
                # draw_image(i, j, MESSAGE)
            if (i, j) in UTILS['bombs_coords']:
                draw_cell(i, j, 'RED')
                # draw_image(i, j, BOMB)


def get_event(event):
    move = event
    if event.startswith('Up'):
        move = 'Up'
    elif event.startswith('Down'):
        move = 'Down'
    elif event.startswith('Left'):
        move = 'Left'
    elif event.startswith('Right'):
        move = 'Right'

    return move


def process_events():
    event, _ = UTILS['window'].read()
    if event in (None, 'Exit'):
        return -1

    event_type = get_event(event)
    if event_type == 'Up' and int(UTILS['player_pos'][1] - UTILS['cell_size']) >= 0:
        UTILS['player_pos'][1] = UTILS['player_pos'][1] - UTILS['cell_size']
    elif get_event(event) == 'Down' and int(UTILS['player_pos'][1] + UTILS['cell_size']) < UTILS['grid_size']-1:
        UTILS['player_pos'][1] = UTILS['player_pos'][1] + UTILS['cell_size']
    elif event_type == 'Left' and int(UTILS['player_pos'][0] - UTILS['cell_size']) >= 0:
        UTILS['player_pos'][0] = UTILS['player_pos'][0] - UTILS['cell_size']
    elif event_type == 'Right' and int(UTILS['player_pos'][0] + UTILS['cell_size']) < UTILS['grid_size']-1:
        UTILS['player_pos'][0] = UTILS['player_pos'][0] + UTILS['cell_size']
    elif event_type == 'Restart':
        UTILS['cell_map'] = numpy.zeros(
            (UTILS['cell_count'], UTILS['cell_count']), dtype=int)
        UTILS['visited_map'] = numpy.zeros(
            (UTILS['cell_count'], UTILS['cell_count']), dtype=int)
        UTILS['messages_coords'] = []
        UTILS['bombs_coords'] = []


def run():
    while True:
        UTILS['canvas'].TKCanvas.delete("all")

        UTILS['window']['-SCORE-'].update(f'Score: {SCORE}')

        draw_grid()

        xPos = UTILS['player_pos'][0] // UTILS['cell_size']
        yPos = UTILS['player_pos'][1] // UTILS['cell_size']

        UTILS['visited_map'][xPos][yPos] = 1

        draw_map()

        draw_image(UTILS['player_pos'][0], UTILS['player_pos'][1], PICKAXE)

        if process_events() == -1:
            break

    UTILS['window'].close()


def read_config(map_path):
    UTILS['messages_coords'] = []
    UTILS['bombs_coords'] = []

    row = 0
    with open(map_path, "r") as map_file:
        for line in map_file.readlines():
            for column in range(len(line)):
                if line[column] == 'M':
                    UTILS['messages_coords'].append((row, column))
                elif line[column] == 'B':
                    UTILS['bombs_coords'].append((row, column))

            row += 1

    UTILS['cell_count'] = row
    UTILS['cell_size'] = UTILS['grid_size'] // UTILS['cell_count']


if __name__ == "__main__":
    read_config(MAP_TEST)

    initialize_map()

    run()
