#!/usr/bin/python
# -*- coding: utf-8 -*-
from PySide2 import QtCore
from PySide2.QtGui import QStandardItemModel, QStandardItem


class ApplicationsModel(QStandardItemModel):
    _BASE_NAME = QtCore.Qt.UserRole + 10

    def __init__(self):
        super(ApplicationsModel, self).__init__()
        self._ITEM_NAME = self._BASE_NAME + 1

    def create_item(self, item):
        _item = QStandardItem(text=item.get('item_name', 'Empty'))
        _item.setData(item.get('item_name'), self._ITEM_NAME)

        return _item

    def add_item(self, item):
        self.appendRow(self.create_item(item))

    @property
    def _item_name(self, index):
        return index.data(self._ITEM_NAME)
