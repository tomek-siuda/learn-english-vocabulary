# import the main window object (mw) from aqt
import json

from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, showWarning
# import all of the Qt GUI library
from aqt.qt import *
import anki
from aqt.editor import Editor
from anki.hooks import wrap

import sys
import traceback

from dict_viewer_plugin import cache, main_classes, frequency_list
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

    def __init__(self, editor):
        self.main_grid = None
        self.section_container = None  # type: SectionContainer
        self.frequency_position = None
        self.editor = editor

    def word_changed(self, text):
        pass

    def copy(self):
        if self.section_container is None:
            showWarning('Nothing to copy')
            return
        text = main_classes.section_container_to_text(
            self.section_container,
            lambda path: mw.col.media.addFile(path)
        )
        self.editor.web.eval("setFormat('inserthtml', %s);" % json.dumps(text))

    def clicked(self, text):
        try:
            section_container = load_word(text)
        except ParseError, e:
            showWarning('Parsing error: {}'.format(e.message))
            return
        except WordNotFoundError, e:
            showWarning('Word not found: {}'.format(e.word))
            return

        self.frequency_position = frequency_list.get_position(text)
        self.section_container = section_container

        content_layout = self.content_layout
        if content_layout is not None:
            for i in reversed(range(content_layout.count())):
                try:
                    # Widgets don't have the count method
                    content_layout.itemAt(i).count()
                except AttributeError:
                    widget = content_layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                    else:
                        # Workaround for removing QSpacerItem
                        content_layout.removeItem(content_layout.itemAt(i))
                    continue
                for j in reversed(range(content_layout.itemAt(i).count())):
                    widget = content_layout.itemAt(i).itemAt(j).widget()
                    if widget:
                        widget.setParent(None)

        content_layout.addWidget(self.create_frequency_widget())
        content_layout.addWidget(QLabel(''))

        grid = QGridLayout()
        for i, section in enumerate(section_container.sections):
            self.section_to_widget(section, grid, i)
        content_layout.addLayout(grid)
        content_layout.addStretch()

    def create_frequency_widget(self):
        return QLabel('Frequency position: ' + str(self.frequency_position))

    def section_to_widget(self, section, grid, row_id):
        """
        :type section: Section
        """
        label_name = ''
        if section.type == SectionType.PRONUNCIATION:
            label_name = 'IPA:'
        if section.type == SectionType.DEFINITION:
            label_name = 'definition:'
        if section.type == SectionType.SENTENCE:
            label_name = ''
        if section.type == SectionType.NAME:
            label_name = 'word:'
        if label_name:
            label = QLabel()
            label.setText(label_name)
            label.setStyleSheet("border: 1px solid black")
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            grid.addWidget(label, row_id, 1)
        if section.audio is not None:
            button = QPushButton()
            button.setText('listen')
            button.clicked.connect(lambda: play_sound(section.audio))
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            grid.addWidget(button, row_id, 3)
            cb_audio = QCheckBox('copy audio')
            cb_audio.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            cb_audio.setCheckState(Qt.Checked if section.copy_audio else Qt.Unchecked)
            cb_audio.stateChanged.connect(lambda: self.audio_checkbox(cb_audio, section))
            grid.addWidget(cb_audio, row_id, 5)
        cb = QCheckBox('copy text')
        cb.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        cb.setCheckState(Qt.Checked if section.copy_text else Qt.Unchecked)
        cb.stateChanged.connect(lambda: self.text_checkbox(cb, section))
        grid.addWidget(cb, row_id, 4)

        content = QLabel()
        content.setStyleSheet("border: 1px solid black")
        content.setText(unicode(section))
        grid.addWidget(content, row_id, 2)

        # content.setSizePolicy ( QSizePolicy.Fixed, QSizePolicy.Fixed)

        return grid

    def audio_checkbox(self, cb, section):
        """
        :type section: Section
        """
        section.copy_audio = cb.isChecked()

    def text_checkbox(self, cb, section):
        """
        :type section: Section
        """
        section.copy_text = cb.isChecked()

    def testFunction(self):
        mw.myWidget = win = QWidget()

        self.main_grid = QVBoxLayout()

        typingGrid = QHBoxLayout()

        word_line = QLineEdit()
        word_line.textChanged.connect(self.word_changed)
        word_line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        typingGrid.addWidget(word_line)

        button = QPushButton()
        button.setText('search')
        button.setSizePolicy ( QSizePolicy.Fixed, QSizePolicy.Fixed)
        typingGrid.addWidget(button)

        typingGrid.addStretch()


        self.main_grid.addLayout(typingGrid)
        self.main_grid.addWidget(QLabel(''))

        self.content_layout = QVBoxLayout()
        content_widget = QWidget()
        content_widget.setLayout(self.content_layout)

        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(content_widget)

        self.main_grid.addWidget(scroll)


        self.main_grid.addWidget(QLabel(''))
        copy_button = QPushButton()
        copy_button.setText('copy')
        copy_button.setSizePolicy ( QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.main_grid.addWidget(copy_button)

        self.main_grid.addStretch()

        button.clicked.connect(lambda: self.clicked(word_line.text()))
        word_line.returnPressed.connect(lambda: self.clicked(word_line.text()))
        copy_button.clicked.connect(lambda: self.copy())

        win.setLayout(self.main_grid)
        win.setWindowTitle("PyQt")
        win.show()


plugin_window = PluginWindow(None)

# create a new menu item, "test"
action = QAction("test", mw)
# set it to call testFunction when it's clicked
action.triggered.connect(plugin_window.testFunction)
# and add it to the tools menu
mw.form.menuTools.addAction(action)

def open_plugin_window(self):
    plugin_window = PluginWindow(self)
    plugin_window.testFunction()

def setup_buttons(self):
    self._addButton("mybutton", lambda s=self: open_plugin_window(self),
                    text=u"D", tip="dict viewer", key="")

Editor.open_plugin_window = open_plugin_window
Editor.setupButtons = wrap(Editor.setupButtons, setup_buttons)
