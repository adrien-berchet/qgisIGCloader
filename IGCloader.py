# -*- coding: utf-8 -*-
"""
/***************************************************************************
 IGCloader
                                 A QGIS plugin
 Reading and plotting IGC gliding logger tracks
                              -------------------
        begin                : 2018-01-09
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Julian Todd
        email                : julian@goatchurch.org.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog

from qgis.core import *

# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from IGCloader_dialog import IGCloaderDialog
import os.path

import igcfile

class IGCloader:
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
            'IGCloader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&IGC loader')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'IGCloader')
        self.toolbar.setObjectName(u'IGCloader')

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
        return QCoreApplication.translate('IGCloader', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = IGCloaderDialog()

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
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)
        
        self.dlg.selectedFile.clear()
        self.dlg.fileSelector.clicked.connect(self.select_igc_file)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/IGCloader/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'IGC importer'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&IGC loader'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def select_igc_file(self):
        filename = QFileDialog.getOpenFileName(self.dlg, "Select .igc file ","", '*.igc')
        self.dlg.selectedFile.setText(filename)

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        
        # See if OK was pressed
        if result:
            fname = self.dlg.selectedFile.text()

            hfparams, recs, cdeclarations = igcfile.GLoadIGC(fname)
            uri = 'LineString?crs=epsg:4326'  # corresponds to wgs84
            name = hfparams.get("PLTPILOT", 'Some guy') 
            layer =  QgsVectorLayer(uri, 'Flight-legs: '+name, 'memory')
            if not layer.isValid():
                raise Exception("Invalid layer with %s" % uri)
            QgsMessageLog.logMessage("Memory layer '%s' called '%s' added" % (uri, name), tag='Import .3d', level=QgsMessageLog.INFO)

            # put in 10 points
            #xyzs = [ (-2+i*0.1, 65+i**2*0.2, 200-i*10)  for i in range(10) ]
            #xyzq = [QgsPointV2(QgsWKBTypes.PointZ, rec[0], rec[1], rec[2]) for rec in xyzs]

            xyzq = [QgsPointV2(QgsWKBTypes.PointZ, rec[0], rec[1], rec[2]) for rec in recs]
            
            #attrs = [1 if flag in style else 0 for flag in self.leg_flags]
            linestring = QgsLineStringV2()
            linestring.setPoints(xyzq)
            feat = QgsFeature()
            geom = QgsGeometry(linestring)
            feat.setGeometry(geom) 
            #feat.setAttributes(attrs)
            layer.dataProvider().addFeatures([feat])

            layer.updateExtents() 
            QgsMapLayerRegistry.instance().addMapLayers([layer])
