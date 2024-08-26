# -*- coding: utf-8 -*-
"""
This script investigate the angle direction within cell division function.
"""

# =============================================================================
# First we need to surpress the version warnings from Pandas.
import warnings 
warnings.simplefilter(action='ignore', category=FutureWarning) 
# =============================================================================

# Load all required modules.

import numpy as np
import pandas as pd

import os
import json
import matplotlib as matplot
import matplotlib.pylab as plt
import ipyvolume as ipv

from tyssue import Sheet, config #import core object
from tyssue import PlanarGeometry as geom #for simple 2d geometry

# For cell topology/configuration
from tyssue.topology.sheet_topology import type1_transition
from tyssue.topology.base_topology import collapse_edge, remove_face
from tyssue.topology.sheet_topology import split_vert as sheet_split
from tyssue.topology.bulk_topology import split_vert as bulk_split
from tyssue.topology import condition_4i, condition_4ii

## model and solver
from tyssue.dynamics.planar_vertex_model import PlanarModel as smodel
from tyssue.solvers.quasistatic import QSSolver
from tyssue.generation import extrude
from tyssue.dynamics import model_factory, effectors
from tyssue.topology.sheet_topology import remove_face, cell_division, get_division_edges

# Event manager
from tyssue.behaviors import EventManager

# 2D plotting
from tyssue.draw import sheet_view, highlight_cells


# Generate the cell sheet as three cells.
sheet = Sheet.planar_sheet_2d('face', nx = 3, ny=4, distx=2, disty=2)
sheet.sanitize(trim_borders=True)
geom.update_all(sheet)
# add mechanical properties.
nondim_specs = nondim_specs = config.dynamics.quasistatic_plane_spec()
sheet.update_specs(nondim_specs, reset = True)
solver = QSSolver()
res = solver.find_energy_min(sheet, geom, smodel)
geom.update_all(sheet)
sheet.get_opposite() 
print(sheet.edge_df)
sheet_view(sheet)

daughter = cell_division(sheet, mother = 2, geom=geom, angle = np.pi/2)
daughter = cell_division(sheet, mother = 1, geom=geom, angle = np.pi/2)
geom.update_all(sheet)
print(sheet.edge_df)
sheet_view(sheet)

help(sheet.get_opposite)

print(sheet.edge_df)


sheet.get_opposite()    # store the corresponding half-edge into edge dataframe.
sheet.get_extra_indices()
sheet.free_edges
sheet.east_edges
sheet.west_edges



# labelling the east edges
fig, ax= sheet_view(sheet)
for edge, data in sheet.edge_df.iterrows():
    # We only want the indexes that are in the east_edge list.
    if edge in sheet.east_edges:
        ax.text((data.sx+data.tx)/2, (data.sy+data.ty)/2, edge)
    else:
        continue





"""
This is the end of the script.
"""
