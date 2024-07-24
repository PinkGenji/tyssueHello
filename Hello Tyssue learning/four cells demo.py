# -*- coding: utf-8 -*-
"""
This script uses a four cell system as a demo.
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
from tyssue.topology.sheet_topology import remove_face, cell_division

# 2D plotting
from tyssue.draw import sheet_view, highlight_cells

from tyssue.generation import three_faces_sheet

nondim_specs = config.dynamics.quasistatic_plane_spec()

""" start the project """
# Generate the cell sheet as three cells.
sheet = Sheet.planar_sheet_2d('face', nx = 3, ny=4, distx=2, disty=2)
sheet.sanitize(trim_borders=True)
geom.update_all(sheet)
sheet_view(sheet, mode = '2D')
# Add more mechanical properties, take four factors
# line tensions; edge length elasticity; face contractility and face area elasticity
new_specs = model_factory([effectors.LineTension, effectors.LengthElasticity, effectors.FaceContractility, effectors.FaceAreaElasticity])

sheet.update_specs(new_specs.specs, reset = True)
geom.update_all(sheet)

#check border vertices are not having force.
fig, ax= sheet_view(sheet)
for vert, data in sheet.vert_df.iterrows():
    ax.text(data.x, data.y+0.1, vert)

# So we need to sinactivate vert 0,2,3 and 5.
sheet.vert_df.loc[[0,2,3,5], 'is_active'] = 0
sheet.vert_df.loc[[0,2,3,5], 'is_active']
solver = QSSolver()
res = solver.find_energy_min(sheet, geom, smodel)

sheet_view(sheet)   # Draw cell mesh.


#plot forces
from tyssue.draw.plt_draw import plot_forces
fig, ax = plot_forces(sheet, geom, smodel, ['x', 'y'], scaling=0.1)
fig.set_size_inches(10, 12)

# Draw the cell mesh with face labelling.
fig, ax = sheet_view(sheet)
for face, data in sheet.face_df.iterrows():
    ax.text(data.x, data.y, face)

# Do cell division
daughter = cell_division(sheet, 1, geom, angle= np.pi)
geom.update_all(sheet)
sheet.reset_index(order=True)
res = solver.find_energy_min(sheet, geom, smodel)
# Draw again with face labelling.
fig, ax= sheet_view(sheet)
for vert, data in sheet.vert_df.iterrows():
    ax.text(data.x, data.y+0.1, vert)
#plot forces
from tyssue.draw.plt_draw import plot_forces
fig, ax = plot_forces(sheet, geom, smodel, ['x', 'y'], scaling=0.1)
fig.set_size_inches(10, 12)


print(sheet.vert_df) #print vert df

# Show three data frames for vertices, edge and face.

print("Following shows first few lines of the database for vertices: \n")
print(sheet.vert_df.head())
print("=========")

print("Following shows first few lines of the database for edges: \n")
print(sheet.edge_df.head())
print("\n There are too many columns, let's get all the column names: \n")
print(sheet.edge_df.keys())
print("=========")

print("Following shows first few lines of the database for faces: \n")
print(sheet.face_df.head())
print("\n There are too many columns, let's get all the column names: \n")
print(sheet.face_df.keys())
print("=========")

print("Vertex is: " + str(sheet.vert_df.loc[0,]) + "\n")
print("Edge is: " + str(sheet.edge_df.loc[0,]) + "\n")
print("Face is: " + str(sheet.face_df.loc[0,]) + "\n")

vertex_before = sheet.vert_df.loc[0,]
edge_before = sheet.edge_df.loc[0,]
face_before = sheet.face_df.loc[0,]

# Change one entry in vert_df, chagne y-coordinate for example.
sheet.vert_df.loc[0,['y']] = 2.9 

vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')

print('Now we use geom.update_all to check if all data frames will be auto-adjusted. \n')
print('start update: \n')
geom.update_all(sheet)

# Recheck the diffrences.
vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print('update finished, check results: \n')
print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')

""" Now we change the edge entry first. """

print("Vertex is: " + str(sheet.vert_df.loc[0,]) + "\n")
print("Edge is: " + str(sheet.edge_df.loc[0,]) + "\n")
print("Face is: " + str(sheet.face_df.loc[0,]) + "\n")

vertex_before = sheet.vert_df.loc[0,]
edge_before = sheet.edge_df.loc[0,]
face_before = sheet.face_df.loc[0,]

# Change one entry in edge_df, change edge length for example.
sheet.edge_df.loc[0,['length']] = 0.7

vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')

print('Now we use geom.update_all to check if all data frames will be auto-adjusted. \n')
print('start update: \n')
geom.update_all(sheet)

# Recheck the diffrences.
vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print('update finished, check results: \n')
print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')


""" Now we change face_df first. """

print("Vertex is: " + str(sheet.vert_df.loc[0,]) + "\n")
print("Edge is: " + str(sheet.edge_df.loc[0,]) + "\n")
print("Face area is: " + str(sheet.face_df.loc[0,'area']) + "\n")

vertex_before = sheet.vert_df.loc[0,]
edge_before = sheet.edge_df.loc[0,]
face_before = sheet.face_df.loc[0,]

# Change one entry in face_df, change face area for example.
sheet.face_df.loc[0,['area']] = 23

print("Face area is: " + str(sheet.face_df.loc[0,'area']) + "\n")


vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')

print("Face area is: " + str(sheet.face_df.loc[0,'area']) + "\n")

print('Now we use geom.update_all to check if all data frames will be auto-adjusted. \n')
print('start update: \n')
geom.update_all(sheet)

# Recheck the diffrences.
vertex_after = sheet.vert_df.loc[0,]
edge_after = sheet.edge_df.loc[0,]
face_after = sheet.face_df.loc[0,]

vertex_differ = (~(vertex_before == vertex_after)).sum()
edge_differ = (~(edge_before == edge_after)).sum()
face_differ = (~(face_before == face_after)).sum()

print('update finished, check results: \n')
print(f'There are {vertex_differ} difference in vertex data frame. \n')
print(f'There are {edge_differ} difference in edge data frame. \n')
print(f'There are {face_differ} difference in face data frame. \n')
print("Face area is: " + str(sheet.face_df.loc[0, 'area']) + "\n")


""" 
Can we make strange things directly on vertex dataset?
Can we do vertex merge directly on vertex dataset?
"""

sheet = Sheet.planar_sheet_2d('face', nx = 3, ny=4, distx=2, disty=2)
sheet.sanitize(trim_borders=True)
geom.update_all(sheet)
# Add more mechanical properties, take four factors
# line tensions; edge length elasticity; face contractility and face area elasticity
new_specs = model_factory([effectors.LineTension, effectors.LengthElasticity, effectors.FaceContractility, effectors.FaceAreaElasticity])

sheet.update_specs(new_specs.specs, reset = True)
geom.update_all(sheet)

fig, ax = sheet_view(sheet)
for face, data in sheet.face_df.iterrows():
     ax.text(data.x, data.y, face)

face_old = sheet.face_df

# Get vertex df first.
vertex_origin = sheet.vert_df
vertex_origin.loc[0,['is_active']] = 0.0
geom.update_all(sheet)
fig, ax = sheet_view(sheet)
for face, data in sheet.face_df.iterrows():
     ax.text(data.x, data.y, face)

face_new = sheet.face_df

''' use built-in functions to collapse an edge '''
sheet = Sheet.planar_sheet_2d('face', nx = 3, ny=4, distx=2, disty=2, noise = 0.5)
sheet.sanitize(trim_borders=True)
geom.update_all(sheet)
sheet_view(sheet)

geom.update_all(sheet)
# Add more mechanical properties, take four factors
# line tensions; edge length elasticity; face contractility and face area elasticity
new_specs = model_factory([effectors.LineTension, effectors.LengthElasticity, effectors.FaceContractility, effectors.FaceAreaElasticity])

sheet.update_specs(new_specs.specs, reset = True)
geom.update_all(sheet)

fig, ax = sheet_view(sheet)
for face, data in sheet.face_df.iterrows():
     ax.text(data.x, data.y, face)

face_old = sheet.face_df

from tyssue.topology.base_topology import collapse_edge, remove_face

# For 
shortest_edge = sheet.edge_df.eval('sx**2+sy**2').idxmin() 

sheet.get_neighbors(4)


"""
This is the end of the script.
"""
