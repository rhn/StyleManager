# -*- coding: utf-8 -*-
"""
/***************************************************************************
 StyleManager
                                 A QGIS plugin
 Allows to conveniently save and load styles for multiple layers
                             -------------------
        begin                : 2016-08-11
        copyright            : (C) 2016 by rhn
        email                : gihu.rhn@porcupinefactory.org
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load StyleManager class from file StyleManager.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .style_manager import StyleManager
    return StyleManager(iface)
