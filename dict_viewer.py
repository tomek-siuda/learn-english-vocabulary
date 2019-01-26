# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

import sys
import traceback

from dict_viewer_plugin.main_classes import ParseError

sys.path.append(os.path.join(os.path.dirname(__file__), "site_packages"))

from dict_viewer_plugin.main import load_word


def word_changed(text):
    pass


def clicked(label, text):
    try:
        load_word(text)
    except ParseError, e:
        
    label.setText(text)


def testFunction():
    mw.myWidget = win = QWidget()

    grid = QGridLayout()

    button = QPushButton()
    button.setText('click me')
    grid.addWidget(button, 1, 3)

    word_line = QLineEdit()
    word_line.textChanged.connect(word_changed)
    grid.addWidget(word_line, 1, 2)

    label = QLabel()
    label.setText("Hello World")
    grid.addWidget(label, 1, 1)

    label2 = QLabel()
    label2.setText("Hello World")
    grid.addWidget(label2, 2, 2)

    button.clicked.connect(lambda: clicked(label2, word_line.text()))

    win.setLayout(grid)
    win.setWindowTitle("PyQt")
    win.show()


# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)