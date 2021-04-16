#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import os
import re

from PySide2 import QtWidgets, QtGui, QtCore
from os.path import dirname, join, normpath
import sys
import subprocess
import jw_logger
import config_parser
try:
    from importlib import reload as reload
except ImportError:
    reload = reload

reload(config_parser)
reload(jw_logger)
log_file = join(dirname(__file__), 'launcher.log')
el_logger = jw_logger.ElLogger('launcher_logger', log_file)
log = el_logger.log

os.environ['PIPELINE_ROOT'] = "C:/tools"


class MainLauncher(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainLauncher, self).__init__(parent)
        log.info('Start init')
        self.cw = QtWidgets.QWidget(self)
        self.setCentralWidget(self.cw)
        self.current_project = 'Character TD'
        self.ml = QtWidgets.QVBoxLayout(self.cw)
        self.config_parser = config_parser.ParseConfig()
        self._config = None
        self.x = None
        self.buttons = []
        self.load_configs()

        self.tray = QtWidgets.QSystemTrayIcon(self)

        self.icon = QtGui.QPixmap(join(dirname(__file__), 'icons', 'mainIcon.png'))
        self.setWindowIcon(QtGui.QIcon(self.icon))

        if self.tray.isSystemTrayAvailable():
            self.tray.setIcon(QtGui.QIcon(self.icon))

            self.tray.activated.connect(self.show_hide)

            # === menu ===
            menu = QtWidgets.QMenu()
            action_show = menu.addAction('Show/Hide')
            action_show.triggered.connect(lambda: self.hide() if self.isVisible() else self.show())
            action_quit = menu.addAction('Quit')
            action_quit.triggered.connect(self.close)

            self.tray.setContextMenu(menu)
            self.tray.show()
        else:
            self.tray = None
        print(f"Pipilene root: {os.getenv('PIPELINE_ROOT')}")
        self.show()

    def _testing(self):
        sender = self.sender().objectName()
        # распарсим конфиг
        cfg = self.prepare_config(self._config.get(sender))
        # теперь получим приложение для запуска
        application = cfg.pop('app')
        # print(application)
        # lower = [k for k in cfg.keys() if k.islower()]
        # print(lower)
        # [cfg.pop(k) for k in lower]
        print(json.dumps(cfg, indent=4, separators=(',', ':')))
        subprocess.Popen([application], env=cfg)

    def prepare_config(self, i):
        self.config_parser.parse_config(i)
        # print(i)
        cfg = self.config_parser.env
        # cfg['PATH'] = cfg.pop('path')
        # print(json.dumps(cfg, indent=4, separators=(',', ':')))
        return cfg

    def load_configs(self):
        """
        Загружает основной файл с окружением и создает кучу ебаных кнопок для приложений
        :return:
        """
        with open(join(join(dirname(__file__), 'configs', 'main_config.json'))) as conf:
            self._config = json.loads(conf.read())
        for item in self._config:
            if not self._config[item].get('app'):
                # если нет ключа app то кнопочку не генерим
                continue
            text = self._config[item].get('beauty_name', item)
            wdg = QtWidgets.QPushButton(self, text=text)
            wdg.setObjectName(item)
            wdg.clicked.connect(self._testing)
            self.ml.addWidget(wdg)
            self.buttons.append(wdg)

    def show_hide(self):
        log.info('Shit')
        if self.isVisible():
            self.hide()
        else:
            self.show()


class SysTrayApp:
    def __init__(self):
        # super(SysTrayApp, self).__init__()
        self.tray = QtWidgets.QSystemTrayIcon()
        self.icon = QtGui.QPixmap(join(dirname(__file__), 'icons', 'mainIcon.png'))
        # .scaledToWidth(18, QtCore.Qt.SmoothTransformation)
        self.app = QtWidgets.QApplication(sys.argv)
        self.tray.setIcon(QtGui.QIcon(self.icon))
        self.tray.setContextMenu(self._main_menu())
        self.tray.show()
        # self.tray.setToolTip('This is Our Launcher')
        # self.tray.showMessage('Shitty', 'Fucky')
        #
        # @self.tray.activated.connect
        # def test(i):
        #     print('click')
        #     self.run_launcher()

    def _main_menu(self):
        menu = QtWidgets.QMenu()
        shit_action = menu.addAction('Run Launcher')
        shit_action.triggered.connect(self.run_maya)
        exit_action = menu.addAction('Exit')
        exit_action.triggered.connect(sys.exit)
        return menu

    def run_maya(self):
        import subprocess
        process = subprocess.Popen('notepad.exe')
        code = process
        print(code)

    def run_launcher(self):
        # import sys
        # _app = QtWidgets.QApplication(sys.argv)
        _win = MainLauncher()
        _win.setWindowTitle('Shitters')
        _win.show()
        # sys.exit(app.exec_())

    def run(self):
        self.app.exec_()
        sys.exit()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('3d generalist')
    app.setApplicationVersion('0.1 alpha')
    app.setOrganizationName('VB')
    win = MainLauncher()
    sys.exit(app.exec_())
