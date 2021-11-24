import os
import numpy
import PySimpleGUI
from tkinter import *
from PIL import ImageTk, Image

RESOURCES_FOLDER = './resources'
PHOTOS_FILES = ('pickaxe.png', 'message.png', 'bomb.png')
MAP_TEST = 'map_test.txt'

GRID_SIZE = 500
APP_FONT = 'Helvetica'
TEXT_SIZE = 16
PySimpleGUI.theme('DarkGrey5')
SCORE_STEP = 10


class Minefield:
    def __init__(self) -> None:
        self.is_running = True
        self.cell_count = 0
        self.cell_size = 0
        self.canvas = None
        self.window = None
        self.player_pos = None
        self.cell_map = None
        self.safe_map = None
        self.visited_map = None
        self.messages = None
        self.bombs = None
        self.pictures = None
        self.score = 0

    def initialize(self):
        self.read_config(MAP_TEST)

        self.initialize_window()

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

                    row += 1

                else:
                    if line.endswith('\n'):
                        line = line[:-1]

                    words = line.split(' ')
                    self.messages[(int(words[0]), int(
                        words[1]))] = ' '.join(words[2:])

        print(self.messages)

        self.cell_count = row
        self.cell_size = GRID_SIZE // self.cell_count

    def initialize_array(self):
        self.messages = {}
        self.bombs = []

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

        self.window = PySimpleGUI.Window('Minefield v1.1', layout, resizable=True, finalize=True,
                                         return_keyboard_events=True)

        self.canvas = self.window['-CANVAS-']

        self.player_pos = [self.cell_size, self.cell_size]

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

        for i in range(1, self.cell_count):
            for j in range(1, self.cell_count):
                if self.visited_map[i][j] == 1:
                    self.draw_cell(i, j)

                    if (i, j) in self.messages.keys():
                        self.draw_cell(i, j, 'GREEN')
                        self.draw_image(i, j, self.pictures[1])
                    if (i, j) in self.bombs:
                        self.draw_cell(i, j, 'RED')
                        self.draw_image(i, j, self.pictures[2])

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
            self.initialize_window()
            self.score = SCORE_STEP
            self.is_running = True

        if not self.is_running:
            return

        if event_type == 'Up' and int(self.player_pos[1] - self.cell_size) > 0:
            self.player_pos[1] = self.player_pos[1] - self.cell_size
        elif event_type == 'Down' and int(self.player_pos[1] + self.cell_size) < GRID_SIZE-1:
            self.player_pos[1] = self.player_pos[1] + self.cell_size
        elif event_type == 'Left' and int(self.player_pos[0] - self.cell_size) > 0:
            self.player_pos[0] = self.player_pos[0] - self.cell_size
        elif event_type == 'Right' and int(self.player_pos[0] + self.cell_size) < GRID_SIZE-1:
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
        # if unvisited future cell is safe, add score step, else subtract it
        if (oldX != newX or oldY != newY) and not self.visited_map[newX][newY]:
            self.score += (-1 ** (not self.safe_map[newX][newY])) * SCORE_STEP

        if (newX, newY) in self.messages.keys():
            self.window['-MESSAGE-'].update(
                f'{self.messages[(newX, newY)]}')
        else:
            self.window['-MESSAGE-'].update('')

        if (newX, newY) in self.bombs:
            self.window['-MESSAGE-'].update(f'YOU LOST!')
            self.is_running = False

        self.safe_map[newX][newY] = 1

        visited_cells = 0
        for i in range(1, self.cell_count):
            for j in range(1, self.cell_count):
                visited_cells += self.visited_map[i][j] == 1

        # maximum visited cells can be total_cells squared minus cells containing axis indices minus number of cells containing bombs minus the current cell
        if visited_cells == self.cell_count ** 2 - (2 * self.cell_count - 1) - len(self.bombs) - 1:
            self.window['-MESSAGE-'].update(f'YOU WON!')
            self.is_running = False


def main():
    minefield = Minefield()
    minefield.initialize()
    minefield.run()


if __name__ == '__main__':
    main()
