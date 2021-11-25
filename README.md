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

note: axis are open-gl like <br />
0 1 2 3 -> x axis <br />
1 <br />
2 <br />
3 -> y axis <br />

the content of map file should be <br />
% - wall or axis indices<br />
M - messages <br />
B - bomb <br />
. - empty cell <br />
= - separates map from messages <br />
i j message_text - message object <br />
