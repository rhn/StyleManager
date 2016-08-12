# -*- coding: utf-8 -*-
"""
/*******************
 StyleManagerDialog
                                 A QGIS plugin
 Allows to conveniently save and load styles for multiple layers
                             -------------------
        begin                : 2016-08-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by rhn
        email                : gihu.rhn@porcupinefactory.org
 ********************/

/*********************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 **********************/
"""

import os

from PyQt4 import QtGui, QtCore, uic

def load_dialog(ui_file):
    return uic.loadUiType(os.path.join(
                               os.path.dirname(__file__), ui_file))

EXPORT_FORM_CLASS, _ = load_dialog('style_manager_export_dialog.ui')

IMPORT_FORM_CLASS, _ = load_dialog('style_manager_import_dialog.ui')

class StyleManagerDialogMixin(QtGui.QDialog):
    def __init__(self, parent=None):
        """Constructor."""
        super(StyleManagerDialogMixin, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.setWindowTitle(self.window_title)
        self.path = self.findChild(QtGui.QWidget, 'path')
        self.select_btn = self.findChild(QtGui.QWidget, 'select_btn')
        QtCore.QObject.connect(self.select_btn, QtCore.SIGNAL('clicked()'), self.set_path)

    def set_path(self):
        path = self.choose_path()
        if path:
            self.path.setText(path)

class StyleManagerExportDialog(StyleManagerDialogMixin, EXPORT_FORM_CLASS):
    window_title = "Save styles"
    def choose_path(self):
        return str(QtGui.QFileDialog.getSaveFileName(self, "Select new directory"))

class StyleManagerImportDialog(StyleManagerDialogMixin, IMPORT_FORM_CLASS):
    window_title = "Load styles"
    def choose_path(self):
        return str(QtGui.QFileDialog.getOpenFileName(self, "Select styles bundle", filter='Bundles .json (*.json)'))
