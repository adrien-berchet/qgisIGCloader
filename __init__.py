# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IGCloader
                                 A QGIS plugin
 Reading and plotting IGC gliding logger tracks
                             -------------------
        begin                : 2018-01-09
        copyright            : (C) 2018 by Julian Todd
        email                : julian@goatchurch.org.uk
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
    """Load IGCloader class from file IGCloader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .IGCloader import IGCloader
    return IGCloader(iface)
