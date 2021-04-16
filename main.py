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
    def __init__(self, parent=None, _screen=None):
        super(MainLauncher, self).__init__(parent)
        log.info('Start init')
        self.cw = QtWidgets.QWidget(self)
        self.setCentralWidget(self.cw)
        self.setMinimumWidth(175)
        self.current_project = 'Character TD'
        self.ml = QtWidgets.QVBoxLayout(self.cw)
        self.config_parser = config_parser.ParseConfig()
        self._config = None
        self.x = None
        self.buttons = []
        self.create_app_buttons()

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
        self.set_position(_screen)
        self.show()

    def launch_app(self):
        sender = self.sender().objectName()
        # обновляем конфигурацию
        self.load_main_config()
        # распарсим конфиг
        cfg = self.prepare_config(self._config.get(sender))
        # теперь получим приложение для запуска
        application = cfg.pop('app')
        # print(application)
        # print(json.dumps(cfg, indent=4, separators=(',', ':')))
        subprocess.Popen([application], env=cfg)

    def prepare_config(self, i):
        """Парсит env для приложения"""
        self.config_parser.parse_config(i)
        cfg = self.config_parser.env
        # print(json.dumps(cfg, indent=4, separators=(',', ':')))
        return cfg

    def load_main_config(self):
        with open(join(join(dirname(__file__), 'configs', 'main_config.json'))) as conf:
            self._config = json.loads(conf.read())

    def create_app_buttons(self):
        """
        Загружает основной файл с окружением и создает кучу ебаных кнопок для приложений
        :return:
        """
        if not self._config:
            self.load_main_config()

        for item in self._config:
            if not self._config[item].get('app'):
                # если нет ключа app то кнопочку не генерим
                continue
            text = self._config[item].get('beauty_name', item)
            wdg = QtWidgets.QPushButton(self, text=text)
            # wdg = BtnApp(self, text)
            wdg.setObjectName(item)
            wdg.clicked.connect(self.launch_app)
            self.ml.addWidget(wdg)
            self.buttons.append(wdg)

    def show_hide(self):
        log.info('Shit')
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def set_position(self, i):
        pos = QtCore.QRect(
            QtCore.QPoint(i.width() - 250, i.height() - 200),
            QtCore.QSize(180, 140)
        )
        self.setGeometry(pos)


class BtnApp(QtWidgets.QPushButton):
    def __init__(self, parent=None, name=None):
        super(BtnApp, self).__init__(parent)
        self.name = name
        self.setMinimumHeight(34)
        mouse_hover = self.mouseMoveEvent
        self.setMouseTracking(True)

        def redraw(event):
            # if event.type():
            # painter = QtGui.QPainter(self)
            # painter.fillRect(
            #     0, 0, painter.device().width(), painter.device().height(),
            #     QtGui.QColor(128, 140, 150, 200)
            # )
            mouse_hover(event)
            print(event.type())
            # self.paintEvent(event)

        self.mouseMoveEvent = redraw

    def get_icon(self):
        """
        Ищет иконку для кнопки
        :return:
        """
        pass

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())

        color = QtGui.QColor(145, 155, 165, 105)
        if e.type() == QtCore.QEvent.Type.MouseMove:
            color = QtGui.QColor(128, 140, 150, 200)
            # print("mouse move")
        else:
            color = QtGui.QColor(150, 150, 155, 190)
        #     print('Painting')
        brush.setColor(color)
        brush.setStyle(QtCore.Qt.SolidPattern)
        painter.fillRect(rect, brush)
        painter.setBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
        painter.setPen(QtGui.QPen(QtGui.QColor(85, 45, 45, 255)))


        painter.drawText(
            QtCore.QPoint(38, 20),
            self.name
        )


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName('3d generalist')
    app.setApplicationVersion('0.1 alpha')
    app.setOrganizationName('VB')

    screen = app.primaryScreen()
    res = screen.availableGeometry()

    win = MainLauncher(_screen=res)
    # geo = win.geometry()
    # print(f"pos: x {geo.x()} y {geo.y()}\nwidth: {geo.width()} | height: {geo.height()}")
    sys.exit(app.exec_())
