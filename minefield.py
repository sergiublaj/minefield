'''
Name: minefield.py
Authors: Blaj Sergiu, Borbei Raul
Description: minefield game
'''

import os
import numpy
import PySimpleGUI
from tkinter import *
from PIL import ImageTk, Image

MAPS_FOLDER = './resources/maps'
IMAGES_FOLDER = './resources/images'

PHOTOS_FILES = ('pickaxe.png', 'message.png', 'bomb.png')
MAP_TEST = 'map_test.txt'

GRID_SIZE = 500
APP_FONT = 'Helvetica'
TEXT_SIZE = 16
PySimpleGUI.theme('DarkGrey5')
SCORE_STEP = 10

MINEFOL_ASSUMPTIONS = [
    'formulas(assumptions).', 'all x all y (safe(x,y) <-> -(mine(x,y))).', 'safe(1,1).', 'end_of_list.', '\n']
MINEFOL_GOALS = ['formulas(goals).', '', 'end_of_list.', '\n']

PROVER_INPUT = 'prover9.in'
PROVER_OUTPUT = 'prover9.out'

READ_MODE = 'r'
WRITE_MODE = 'w'

PROVER_COMMAND = f'prover9 -f {PROVER_INPUT} > {PROVER_OUTPUT}'
THEOREM_PROVED = 'THEOREM PROVED'


class Minefield:
    def __init__(self):
        pass

    def initialize(self):
        self.read_config(os.path.join(MAPS_FOLDER, MAP_TEST))

        self.initialize_window()

        self.initialize_game()

        self.load_pictures()

    def read_config(self, map_path):
        self.initialize_array()

        row = 0
        reading_map = True
        with open(map_path, 'r') as map_file:
            for line in map_file.readlines():
                if line.startswith('='):
                    reading_map = False
                    continue

                if reading_map:
                    for column in range(len(line)):
                        if line[column] == 'M':
                            self.messages[(column, row)] = ''
                        elif line[column] == 'B':
                            self.bombs.append((column, row))
                        elif line[column] == '%':
                            self.walls.append((column, row))

                    row += 1

                else:
                    if line.endswith('\n'):
                        line = line[:-1]

                    words = line.split(' ')
                    self.messages[(int(words[0]), int(
                        words[1]))] = ' '.join(words[2:])

        self.cell_count = row
        self.cell_size = GRID_SIZE // self.cell_count

    def initialize_array(self):
        self.messages = {}
        self.bombs = []
        self.walls = []

    def load_pictures(self):
        self.pictures = []

        for resource in PHOTOS_FILES:
            image = Image.open(os.path.join(IMAGES_FOLDER, resource))
            image = image.resize(
                (self.cell_size, self.cell_size), Image.ANTIALIAS)
            photoImage = ImageTk.PhotoImage(image)
            self.pictures.append(photoImage)

    def initialize_window(self):
        self.initialize_matrix()

        sizeX = GRID_SIZE // self.cell_count // 6
        sizeY = 1

        layout = [[PySimpleGUI.Canvas(size=(GRID_SIZE, GRID_SIZE),
                                      background_color='WHITE',
                                      key='-CANVAS-')],
                  [[PySimpleGUI.Exit(font=' '.join([APP_FONT, str(TEXT_SIZE)]), size=(sizeX, sizeY)),
                   PySimpleGUI.Button('Restart', font=' '.join([APP_FONT, str(TEXT_SIZE)]), size=(sizeX, sizeY))],
                   [PySimpleGUI.Text('', key='-SCORE-',
                                     font=' '.join([APP_FONT, str(TEXT_SIZE)]), size=(sizeX, sizeY))],
                   [PySimpleGUI.Text(f'{self.messages[(1, 1)]}', key='-MESSAGE-',
                                     font=' '.join([APP_FONT, str(TEXT_SIZE)]), size=(sizeX * 2, sizeY))]]]

        self.window = PySimpleGUI.Window('Minefield v1.2', layout, resizable=True, finalize=True,
                                         return_keyboard_events=True)

        self.canvas = self.window['-CANVAS-']

    def initialize_matrix(self):
        self.cell_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)
        self.visited_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)
        self.safe_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)

    def initialize_game(self):
        self.player_pos = [self.cell_size, self.cell_size]

        self.score = 0

        self.visited_cells = 0

        self.is_running = True

        MINEFOL_ASSUMPTIONS.insert(3, self.messages[(1, 1)])

    def draw_grid(self):
        self.canvas.TKCanvas.create_rectangle(
            1, 1, GRID_SIZE, GRID_SIZE, outline='BLACK', width=1)

        for idx in range(self.cell_count):
            self.canvas.TKCanvas.create_line(
                ((self.cell_size * idx),
                 self.cell_size), ((self.cell_size * idx), GRID_SIZE),
                fill='BLACK', width=1)
            self.canvas.TKCanvas.create_line(
                (self.cell_size, (self.cell_size * idx)
                 ), (GRID_SIZE, (self.cell_size * idx)),
                fill='BLACK', width=1)

    def draw_map(self, xPos, yPos):
        number_coordinate = self.cell_size // 2 + 2

        for idx in range(self.cell_count):
            self.draw_cell(idx, 0, 'GRAY')
            self.canvas.TKCanvas.create_text(idx * self.cell_size + number_coordinate, number_coordinate,
                                             fill='WHITE', font=' '.join([APP_FONT, str(self.cell_size)]),
                                             text=f'{idx}')

            self.draw_cell(0, idx, 'GRAY')
            self.canvas.TKCanvas.create_text(number_coordinate, idx * self.cell_size + number_coordinate,
                                             fill='WHITE', font=' '.join([APP_FONT, str(self.cell_size)]),
                                             text=f'{idx}')

        for row in range(1, self.cell_count):
            for col in range(1, self.cell_count):
                if (row, col) in self.walls:
                    self.draw_cell(row, col, 'GRAY')

                if self.visited_map[row][col] == 1:
                    self.draw_cell(row, col)

                    if (row, col) in self.messages.keys():
                        self.draw_cell(row, col, 'GREEN')
                        self.draw_image(row, col, self.pictures[1])
                    if (row, col) in self.bombs:
                        self.draw_cell(row, col, 'RED')
                        self.draw_image(row, col, self.pictures[2])

        self.draw_image(xPos,
                        yPos, self.pictures[0])

    def draw_image(self, x, y, resource):
        x *= self.cell_size
        y *= self.cell_size

        self.canvas.TKCanvas.create_image(
            x, y, image=resource, anchor='nw')

    def draw_cell(self, x, y, color='YELLOW'):
        x *= self.cell_size
        y *= self.cell_size

        self.canvas.TKCanvas.create_rectangle(
            x, y, x + self.cell_size, y + self.cell_size,
            outline='BLACK', fill=color, width=1)

    def run(self):
        while True:
            self.canvas.TKCanvas.delete('all')

            self.window['-SCORE-'].update(f'Score: {self.score}')

            self.draw_grid()

            xPos = self.player_pos[0] // self.cell_size
            yPos = self.player_pos[1] // self.cell_size

            self.visited_map[xPos][yPos] = 1

            self.draw_map(xPos, yPos)

            if self.process_events(xPos, yPos) == -1:
                break

        self.window.close()

    def process_events(self, oldX, oldY):
        event, _ = self.window.read()
        if event in (None, 'Exit'):
            return -1

        event_type = self.get_event(event)
        if event_type == 'Restart':
            self.window.close()
            self.initialize_window()
            self.initialize_game()
            return

        if not self.is_running:
            return

        if event_type == 'Up' and int(self.player_pos[1] - self.cell_size) >= 0 and \
                (self.player_pos[0] // self.cell_size, (self.player_pos[1] - self.cell_size) // self.cell_size) not in self.walls:
            self.player_pos[1] = self.player_pos[1] - self.cell_size
        elif event_type == 'Down' and int(self.player_pos[1] + self.cell_size) < GRID_SIZE-1 and \
                (self.player_pos[0] // self.cell_size, (self.player_pos[1] + self.cell_size) // self.cell_size) not in self.walls:
            self.player_pos[1] = self.player_pos[1] + self.cell_size
        elif event_type == 'Left' and int(self.player_pos[0] - self.cell_size) >= 0 and \
                ((self.player_pos[0] - self.cell_size) // self.cell_size, self.player_pos[1] // self.cell_size) not in self.walls:
            self.player_pos[0] = self.player_pos[0] - self.cell_size
        elif event_type == 'Right' and int(self.player_pos[0] + self.cell_size) < GRID_SIZE-1 and \
                ((self.player_pos[0] + self.cell_size) // self.cell_size, self.player_pos[1] // self.cell_size) not in self.walls:
            self.player_pos[0] = self.player_pos[0] + self.cell_size

        newX = self.player_pos[0] // self.cell_size
        newY = self.player_pos[1] // self.cell_size

        self.check_move(oldX, oldY, newX, newY)

    def get_event(self, event):
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

    def check_move(self, oldX, oldY, newX, newY):
        if oldX == newX and oldY == newY:
            return

        if (newX, newY) in self.bombs:
            self.window['-MESSAGE-'].update(f'YOU LOST!')
            self.is_running = False

        if (newX, newY) in self.messages.keys():
            current_message = self.messages[(newX, newY)]

            self.window['-MESSAGE-'].update(
                f'{current_message}')

            if current_message not in MINEFOL_ASSUMPTIONS:
                MINEFOL_ASSUMPTIONS.insert(3, current_message)
        else:
            self.window['-MESSAGE-'].update('')

        if not self.visited_map[newX][newY]:
            self.safe_map[newX][newY] = self.check_safe(newX, newY)
            self.score += ((-1) **
                           (not self.safe_map[newX][newY])) * SCORE_STEP
            self.visited_cells += 1

        if self.visited_cells == self.cell_count ** 2 - len(self.bombs) - len(self.walls) - 1:
            self.window['-MESSAGE-'].update(f'YOU WON!')
            self.is_running = False

    def check_safe(self, x, y):
        MINEFOL_GOALS[1] = f'safe({x}, {y}).'

        with open(PROVER_INPUT, WRITE_MODE) as prover_file:
            prover_file.write('\n'.join(MINEFOL_ASSUMPTIONS))
            prover_file.write('\n'.join(MINEFOL_GOALS))

        os.system(PROVER_COMMAND)

        with open(PROVER_OUTPUT, READ_MODE) as prover_file:
            demonstration = prover_file.read()

        return THEOREM_PROVED in demonstration


def main():
    minefield = Minefield()
    minefield.initialize()
    minefield.run()


if __name__ == '__main__':
    main()
