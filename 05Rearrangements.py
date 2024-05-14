# -*- coding: utf-8 -*-
"""
This file is for learning 05Rearrangements of the tyssue package.
"""

import os
import pandas as pd
import numpy as np
import json
import matplotlib.pylab as plt

from tyssue import Sheet, Monolayer, config
from tyssue import SheetGeometry, PlanarGeometry


# What we're here for
from tyssue.topology.sheet_topology import type1_transition
from tyssue.topology.base_topology import collapse_edge, remove_face
from tyssue.topology.sheet_topology import split_vert as sheet_split
from tyssue.topology.bulk_topology import split_vert as bulk_split
from tyssue.topology import condition_4i, condition_4ii

## model and solver
from tyssue.dynamics.sheet_vertex_model import SheetModel as model
from tyssue.solvers.quasistatic import QSSolver
from tyssue.generation import extrude
from tyssue.dynamics import model_factory, effectors

# 2D plotting
from tyssue.draw import sheet_view, highlight_cells

#I/O
from tyssue.io import hdf5
plt.style.use('bmh')

import logging

'''
Type 1 Transition:

First, we generate the initial cells.

'''

geom = SheetGeometry


solver = QSSolver()

wd = r"C:\Users\lyu195\Documents\GitHub\tyssueHello"
os.chdir(wd)

os.path.isfile('small_hexagonal.hf5')  #Check working directory set correctly.

h5store = 'small_hexagonal.hf5'

datasets = hdf5.load_datasets(h5store, data_names=['face', 'vert', 'edge'])
specs = config.geometry.cylindrical_sheet()
sheet = Sheet('emin', datasets, specs)


geom.update_all(sheet)

nondim_specs = config.dynamics.quasistatic_sheet_spec()
dim_model_specs = model.dimensionalize(nondim_specs)
sheet.update_specs(dim_model_specs, reset=True)

solver_settings = {'options': {'gtol':1e-4}}

sheet.get_opposite()
sheet.vert_df.is_active = 0

active_edges = (sheet.edge_df['opposite'] > -1)
active_verts = np.unique(sheet.edge_df[active_edges]['srce'])

sheet.vert_df.loc[active_verts, 'is_active'] = 1

fig, ax = sheet_view(sheet, ['z', 'x'],
                     edge={'head_width': 0.5},
                     vert={'visible': False})
fig.set_size_inches(10, 6)

'''
Type 1 transition starts:
'''

type1_transition(sheet, 82)
geom.update_all(sheet)

res = solver.find_energy_min(sheet, geom, model, **solver_settings)
fig, ax = sheet_view(sheet, mode="quick", coords=['z', 'x'])

# Closer look using sheet_view:

fig, ax = sheet_view(sheet, ['z', 'x'], mode="quick")

ax.set_xlim(3, 10)
ax.set_ylim(-7.5, -2.5)

ax.set_aspect('equal')
fig.set_size_inches(8, 5)


fig, mesh = sheet_view(sheet, mode='3D')
fig

res = solver.find_energy_min(sheet, geom, model)
print(res['success'])
fig, ax = sheet_view(sheet, ['z', 'x'], mode="quick")

sheet.validate()

































'''
This is the end of the file.
'''
