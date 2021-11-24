import os
import numpy
import PySimpleGUI
from tkinter import *
from PIL import ImageTk, Image

RESOURCES_FOLDER = './resources'
PHOTOS_FILES = ('pickaxe.png', 'message.png', 'bomb.png')
MAP_TEST = 'map_test.txt'

GRID_SIZE = 400
APP_FONT = 'Any 16'
PySimpleGUI.theme('DarkGrey5')
SCORE_STEP = 10


class Minefield:
    def __init__(self) -> None:
        self.cell_count = 0
        self.cell_size = 0
        self.canvas = None
        self.window = None
        self.player_pos = None
        self.cell_map = None
        self.safe_map = None
        self.visited_map = None
        self.messages_coords = None
        self.bombs_coords = None
        self.pictures = None
        self.score = 0

    def initialize(self):
        self.read_config(MAP_TEST)

        self.initialize_window()

        self.load_pictures()

        self.canvas = self.window['canvas']
        self.player_pos = [0, 0]
        self.score = 10

        self.draw_grid()
        self.draw_map(0, 0)

    def read_config(self, map_path):
        self.initialize_array()

        row = 0
        with open(map_path, "r") as map_file:
            for line in map_file.readlines():
                for column in range(len(line)):
                    if line[column] == 'M':
                        self.messages_coords.append((row, column))
                    elif line[column] == 'B':
                        self.bombs_coords.append((row, column))

                row += 1

        self.cell_count = row
        self.cell_size = GRID_SIZE // self.cell_count

    def initialize_array(self):
        self.messages_coords = []
        self.bombs_coords = []

    def load_pictures(self):
        self.pictures = []

        for resource in PHOTOS_FILES:
            image = Image.open(os.path.join(RESOURCES_FOLDER, resource))
            image = image.resize(
                (self.cell_size, self.cell_size), Image.ANTIALIAS)
            photoImage = ImageTk.PhotoImage(image)
            self.pictures.append(photoImage)

    def initialize_window(self):
        self.initialize_matrix()

        layout = [[PySimpleGUI.Canvas(size=(GRID_SIZE, GRID_SIZE),
                                      background_color='WHITE',
                                      key='canvas')],
                  [PySimpleGUI.Exit(font=APP_FONT),
                   PySimpleGUI.Text('', key='-SCORE-',
                                    font=APP_FONT, size=(15, 1)),
                   PySimpleGUI.Button('Restart', font=APP_FONT)]]

        self.window = PySimpleGUI.Window('Minefield v1.0', layout, resizable=True, finalize=True,
                                         return_keyboard_events=True)

    def initialize_matrix(self):
        self.cell_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)
        self.visited_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)
        self.safe_map = numpy.zeros(
            (self.cell_count, self.cell_count), dtype=int)

    def draw_grid(self):
        self.canvas.TKCanvas.create_rectangle(
            1, 1, GRID_SIZE, GRID_SIZE, outline='BLACK', width=1)

        for idx in range(self.cell_count):
            self.canvas.TKCanvas.create_line(
                ((self.cell_size * idx),
                 0), ((self.cell_size * idx), GRID_SIZE),
                fill='BLACK', width=1)
            self.canvas.TKCanvas.create_line(
                (0, (self.cell_size * idx)
                 ), (GRID_SIZE, (self.cell_size * idx)),
                fill='BLACK', width=1)

    def draw_map(self, xPos, yPos):
        for i in range(self.cell_count):
            for j in range(self.cell_count):
                if self.visited_map[i][j] == 1:
                    self.draw_cell(i, j)
                if (i, j) in self.messages_coords:
                    self.draw_cell(i, j, 'GREEN')
                    self.draw_image(i, j, self.pictures[1])
                if (i, j) in self.bombs_coords:
                    self.draw_cell(i, j, 'RED')
                    self.draw_image(i, j, self.pictures[2])

        self.draw_image(xPos,
                        yPos, self.pictures[0])

    def draw_image(self, x, y, resource):
        x *= self.cell_size
        y *= self.cell_size

        self.canvas.TKCanvas.create_image(
            x, y, image=resource, anchor='nw')

    def draw_cell(self, x, y, color='GREY'):
        x *= self.cell_size
        y *= self.cell_size

        self.canvas.TKCanvas.create_rectangle(
            x, y, x + self.cell_size, y + self.cell_size,
            outline='BLACK', fill=color, width=1)

    def run(self):
        while True:
            self.canvas.TKCanvas.delete("all")

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
        if event_type == 'Up' and int(self.player_pos[1] - self.cell_size) >= 0:
            self.player_pos[1] = self.player_pos[1] - self.cell_size
        elif event_type == 'Down' and int(self.player_pos[1] + self.cell_size) < GRID_SIZE-1:
            self.player_pos[1] = self.player_pos[1] + self.cell_size
        elif event_type == 'Left' and int(self.player_pos[0] - self.cell_size) >= 0:
            self.player_pos[0] = self.player_pos[0] - self.cell_size
        elif event_type == 'Right' and int(self.player_pos[0] + self.cell_size) < GRID_SIZE-1:
            self.player_pos[0] = self.player_pos[0] + self.cell_size
        elif event_type == 'Restart':
            self.initialize_map()

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
        if (oldX != newX or oldY != newY) and self.safe_map[newX][newY] == 0:
            self.score -= SCORE_STEP


def main():
    minefield = Minefield()
    minefield.initialize()
    minefield.run()


if __name__ == "__main__":
    main()
