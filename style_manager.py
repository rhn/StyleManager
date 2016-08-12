# -*- coding: utf-8 -*-
"""
/************
 StyleManager
                                 A QGIS plugin
 Allows to conveniently save and load styles for multiple layers
                              -------------------
        begin                : 2016-08-11
        git sha              : $Format:%H$
        copyright            : (C) 2016 by rhn
        email                : gihu.rhn@porcupinefactory.org
 *************/

/**************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialogs
from style_manager_dialog import StyleManagerExportDialog, StyleManagerImportDialog
import os.path
import os
import errno
import json
from qgis.core import QGis, QgsMapLayer


def try_mkdir(path):
    try:
        return os.mkdir(path)
    except OSError as e:
        if e.errno == errno.EEXIST:
            return
        raise


def geom_type_to_name(geom_type):
    return {QGis.Point: 'Point',
            QGis.Line: 'Line',
            QGis.Polygon: 'Polygon'}[geom_type]


def get_layer_kind(layer):
    if layer.type() == QgsMapLayer.RasterLayer:
        return 'Raster'
    elif layer.type() == QgsMapLayer.VectorLayer:
        return geom_type_to_name(layer.geometryType())
    return 'Unknown'


def LayerMeta(name, type_, path):
    return {'name': name, 'type': type_, 'path': path}



class PersistenceFunctions:
    def __init__(self, meta_file_name='styles.json'):
        self.meta_file_name = meta_file_name

    def get_import_sources(self, iface, order):
        layers = iface.legendInterface().layers()

        base_layers = {}
        for layer in layers:
            name = layer.name()
            if name == 'points':
                base_layers['Point'] = layer
            elif name == 'lines':
                base_layers['Line'] = layer
            elif name == 'multipolygons':
                base_layers['Polygon'] = layer

        return [(layer['path'], (layer['name'], base_layers[layer['type']])) for layer in order]

    def import_(self, iface, path):
        with open(os.path.join(path, self.meta_file_name), 'r') as meta_file:
            order = json.load(meta_file)
        import_sources = self.get_import_sources(iface, order)
        self.load_layers(iface, path, import_sources)

    def load_layers(self, iface, path, import_sources):
        # insert in reverse order - new layers end up on top
        for subpath, (name, data_layer) in reversed(import_sources):
            style_path = os.path.join(path, *subpath) + '.qml'
            new_layer = iface.addVectorLayer(data_layer.source(), name, data_layer.providerType())
            message, result = new_layer.loadNamedStyle(style_path)
            if not result:
                raise Exception(message)

    def export(self, iface, path):
        legend = iface.legendInterface()
        layers = legend.layers()

        order = []
        dirs_to_layers = {}
        for layer in layers:
            if not legend.isLayerVisible(layer):
                continue

            raw_name = layer.name()
            layer_type = get_layer_kind(layer)
            name = raw_name.split('_', 1)[0]
            
            order.append(LayerMeta(raw_name, layer_type, (name, layer_type)))
            namedir = dirs_to_layers.setdefault(name, {})
            namedir.setdefault(layer_type, layer)
        
        try:
            try_mkdir(path)
            with open(os.path.join(path, META_FILE_NAME), 'w') as order_file:
                json.dump(order, order_file, indent=1)
            for name, namedir in dirs_to_layers.items():
                namepath = os.path.join(path, name)
                try_mkdir(namepath)
                for geom_type_name, layer in namedir.items():
                    stylepath = os.path.join(namepath, geom_type_name + '.qml')
                    layer.saveNamedStyle(stylepath)
        except:
            raise

persistence = PersistenceFunctions()
META_FILE_NAME = persistence.meta_file_name


class StyleManager:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'StyleManager_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialogs (after translation) and keep reference
        self.export_dlg = StyleManagerExportDialog()
        self.import_dlg = StyleManagerImportDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Style Manager')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'StyleManager')
        self.toolbar.setObjectName(u'StyleManager')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('StyleManager', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        self.add_action(
            icon_path=':/plugins/StyleManager/icon_save.png',
            text=self.tr(u'Save styles'),
            callback=self.export,
            parent=self.iface.mainWindow())
        self.add_action(
            icon_path=':/plugins/StyleManager/icon.png',
            text=self.tr(u'Load styles'),
            callback=self.import_,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Style Manager'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def get_path(self, dialog):
        # show the dialog
        dialog.show()
        # Run the dialog event loop
        result = dialog.exec_()
        # See if OK was pressed
        if not result:
            return None
        return dialog.path.text()

    def export(self):
        """Run method that performs all the real work"""
        path = self.get_path(self.export_dlg)
        if path is None:
            return
        if os.path.basename(path) == META_FILE_NAME:
            path = os.path.dirname(path)

        persistence.export(self.iface, path)

    def import_(self):
        """Run method that performs all the real work"""
        path = self.get_path(self.import_dlg)
        if path is None:
            return
        persistence.import_(self.iface, os.path.dirname(path))
