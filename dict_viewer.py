# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, showWarning
# import all of the Qt GUI library
from aqt.qt import *
import anki

import sys
import traceback

from dict_viewer_plugin import cache
from dict_viewer_plugin.main_classes import ParseError, WordNotFoundError, Element, Section, \
    SectionType, SectionContainer

sys.path.append(os.path.join(os.path.dirname(__file__), "dict_viewer_plugin", "site_packages"))

from dict_viewer_plugin.main import load_word


def play_sound(sound_file):
    """
    :type sound_file: cache.File
    """
    path = sound_file.get_absolute_path()
    anki.sound.clearAudioQueue()
    anki.sound.play(path)


class PluginWindow:

    def __init__(self):
        self.main_grid = None

    def word_changed(self, text):
        pass

    def clicked(self, text):
        try:
            section_container = load_word(text)
        except ParseError, e:
            showWarning('Parsing error: {}'.format(e.message))
            return
        except WordNotFoundError, e:
            showWarning('Word not found: {}'.format(e.word))
            return

        grid = self.main_grid.itemAtPosition(5, 1)
        if grid is not None:
            for i in reversed(range(grid.count())):
                for j in reversed(range(grid.itemAt(i).count())):
                    grid.itemAt(i).itemAt(j).widget().setParent(None)
        else:
            grid = QGridLayout()
            self.main_grid.addLayout(grid, 5, 1)

        for i, section in enumerate(section_container.sections):
            grid.addLayout(self.section_to_widget(section), i, 1)

    def section_to_widget(self, section):
        """
        :type section: Section
        """
        grid = QGridLayout()
        content = QLabel()
        content.setStyleSheet("border: 1px solid black")
        content.setText(unicode(section))
        label_name = ''
        if section.type == SectionType.PRONUNCIATION:
            label_name = 'IPA:'
        if section.type == SectionType.DEFINITION:
            label_name = 'definition:'
        if section.type == SectionType.SENTENCE:
            label_name = 'sentence:'
        if label_name:
            label = QLabel()
            label.setText(label_name)
            grid.addWidget(label, 1, 1)
        if section.audio is not None:
            button = QPushButton()
            button.setText('listen')
            button.clicked.connect(lambda: play_sound(section.audio))
            grid.addWidget(button, 1, 3)
            cb_audio = QCheckBox('copy audio')
            grid.addWidget(cb_audio, 1, 5)
        cb = QCheckBox('copy text')
        grid.addWidget(cb, 1, 4)

        content.setSizePolicy ( QSizePolicy.Fixed, QSizePolicy.Fixed)

        grid.addWidget(content, 1, 2)
        return grid

    def testFunction(self):
        mw.myWidget = win = QWidget()

        self.main_grid = QGridLayout()

        typingGrid = QHBoxLayout()

        word_line = QLineEdit()
        word_line.textChanged.connect(self.word_changed)
        word_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        typingGrid.addWidget(word_line)

        button = QPushButton()
        button.setText('search')
        button.setSizePolicy ( QSizePolicy.Fixed, QSizePolicy.Fixed)
        typingGrid.addWidget(button)

        self.main_grid.addLayout(typingGrid, 1, 1)

        # auxiliary label keeping the rest of the layout fixed
        helper = QLabel()
        helper.setText("")
        # label3.setStyleSheet("border: 1px solid black")
        self.main_grid.addWidget(helper, 6, 1)

        button.clicked.connect(lambda: self.clicked(word_line.text()))

        win.setLayout(self.main_grid)
        win.setWindowTitle("PyQt")
        win.show()


plugin_window = PluginWindow()

# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(plugin_window.testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)