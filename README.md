# minefield

Minfield in Python3

# GUI

taken from: https://github.com/KenoLeon/Medium-Mazes

# steps to run

1. clone/ download the project
2. open folder with vscode/ pycharm
3. python -m venv venv
4. .\venv\Scripts\activate
5. pip install PySimpleGUI
6. pip install numpy
7. pip install pillow
8. python minefield.py

# build your own map

note: axis are open-gl like **
0 1 2 3 -> x axis **
1 **
2 **
3 -> y axis \_\_

the content of map file should be **
% - axis indices **
M - messages **
B - bomb **
. - empty cell **
= - separates map from messages **
i j message_text - message object \_\_
