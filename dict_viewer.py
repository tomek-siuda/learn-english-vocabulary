# import the main window object (mw) from aqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, showWarning
# import all of the Qt GUI library
from aqt.qt import *

import sys
import traceback

from dict_viewer_plugin.main_classes import ParseError, WordNotFoundError, Element, Section, \
    SectionType, SectionContainer

sys.path.append(os.path.join(os.path.dirname(__file__), "dict_viewer_plugin", "site_packages"))

from dict_viewer_plugin.main import load_word


class PluginWindow:

    def __init__(self):
        self.main_grid = None

    def word_changed(self, text):
        pass

    def clicked(self, label, text):
        try:
            section_container = load_word(text)
        except ParseError, e:
            showWarning('Parsing error: {}'.format(e.message))
            return
        except WordNotFoundError, e:
            showWarning('Word not found: {}'.format(e.word))
            return

        for i, section in enumerate(section_container.sections):
            self.main_grid.addLayout(self.section_to_widget(section), i+5, 1)

    def section_to_widget(self, section):
        """
        :type section: Section
        """
        grid = QGridLayout()
        content = QLabel()
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
        grid.addWidget(content, 1, 2)
        return grid

    def testFunction(self):
        mw.myWidget = win = QWidget()

        grid = QGridLayout()
        self.main_grid = grid

        button = QPushButton()
        button.setText('click me')
        grid.addWidget(button, 1, 3)

        word_line = QLineEdit()
        word_line.textChanged.connect(self.word_changed)
        grid.addWidget(word_line, 1, 2)

        label = QLabel()
        label.setText("Hello World")
        grid.addWidget(label, 1, 1)

        label2 = QLabel()
        label2.setText("Hello World")
        grid.addWidget(label2, 2, 2)

        button.clicked.connect(lambda: self.clicked(label2, word_line.text()))

        win.setLayout(grid)
        win.setWindowTitle("PyQt")
        win.show()


plugin_window = PluginWindow()

# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(plugin_window.testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)