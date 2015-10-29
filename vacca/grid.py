#!/usr/bin/env python

#############################################################################
##
## This file is part of Taurus, a Tango User Interface Library
## 
## http://www.tango-controls.org/static/taurus/latest/doc/html/index.html
##
## Copyright 2011 CELLS / ALBA Synchrotron, Bellaterra, Spain
## 
## Taurus is free software: you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
## 
## Taurus is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
## 
## You should have received a copy of the GNU Lesser General Public License
## along with Taurus.  If not, see <http://www.gnu.org/licenses/>.
##
###########################################################################

import fandango
from taurus.qt.qtgui.table import TaurusGrid
from taurus.qt.qtgui.taurusgui.utils import PanelDescription


class VaccaGrid(TaurusGrid):
    """ TaurusGrid enhanced to provide default PanelDescription """

    @staticmethod
    def getGridPanelDescription(grid):
        class_name = get_grid(grid)
        gridPanel = PanelDescription('VaccaGrid',
                                classname = 'vacca.VaccaGrid',
                                model = grid,
                                )
        return gridPanel

class VaccaVerticalGrid(TaurusGrid):

    @staticmethod
    def getVerticalGridPanelDescription(grid):
        class_name = get_grid(get_vertical_grid(grid))
        gridPanel = PanelDescription('VaccaVGrid',
                                classname = 'vacca.VaccaVerticalGrid',
                                model = get_vertical_grid(grid),
                                )
        return gridPanel

def get_empty_grid():
    tg = TaurusGrid()
    tg.showRowFrame(False)
    tg.showColumnFrame(False)
    tg.showAttributeLabels(False)
    tg.showAttributeUnits(False)
    return tg

def get_grid(grid):
    print 'get_grid(%s)'%str(grid.keys())
    tg = get_empty_grid()
    tg.setRowLabels(grid['row_labels'])
    tg.setColumnLabels(grid['column_labels'])
    tg.setModel(grid['model'])#,delayed=False)
    return tg

def get_vertical_grid(grid):
    vgrid = dict(grid)
    vgrid['column_labels'] = grid['row_labels']#'Gauges:VGCT|CCG|V-PEN,Pumps:IPCT|V-VARIP'
    vgrid['row_labels'] = grid['column_labels']
    vgrid['model'] = [s.replace('|State', '') for s in fandango.toSequence(
        grid['model'])]
    return vgrid #get_grid(vgrid)

from .doc import get_autodoc
__doc__ = get_autodoc(__name__,vars())