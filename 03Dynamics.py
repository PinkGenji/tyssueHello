# -*- coding: utf-8 -*-
"""
This file is for learning 03Dynamics of the tyssue package.
"""

'''
One of the objectives of tyssue is to make it easy to define and change the expression
of the epithelium energy. For this, we define two classes of obejcts: Effector and Model.

Effector: those define a single energy term, evaluated on the mesh, and depending
on the values in the data frame.
For example, line tension, for which the energy is proportional to the length of the hal-edge,
is defined as an Effector object. 
For each Effector, we define a way to compute the energy and its spatial derivative, the gradient.

Model: a model is basically a collection of effectors, with the mechanisms to combine
them to define the total dynamics of the system.

In general, the parameters of the models are addressable at the single element level.
For example, the line tension can be set for each individual edge.

'''

import sys
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pylab as plt
import tyssue

from scipy import optimize

from tyssue import Sheet, config
from tyssue import SheetGeometry as geom
from tyssue.dynamics import effectors, model_factory
from tyssue.draw import sheet_view
from tyssue.draw.plt_draw import plot_forces
from tyssue.io import hdf5

# Set the working directory to the location of the file first, we do it manually.
wd = r"C:\Users\lyu195\Documents\GitHub\tyssueHello"
os.chdir(wd)

os.path.isfile('small_hexagonal.hf5')  #Check working directory set correctly.

h5store = 'small_hexagonal.hf5'
# h5store = 'data/before_apoptosis.hf5'

datasets = hdf5.load_datasets(h5store)
sheet = Sheet('emin', datasets)
sheet.sanitize(trim_borders=True, order_edges=True)

geom.update_all(sheet)

sqrt_area = sheet.face_df['area'].mean()**0.5
geom.scale(sheet, 1/sqrt_area, sheet.coords)

fig, ax = sheet_view(sheet, ['z', 'x'], mode = 'quick')

'''
(Non)-Dimensionalization:

This section is about manipulating the units of parameters, so we can get a
preferred area, such as the area is unity.

'''

geom.scale(sheet, 1/sheet.face_df['area'].mean()**0.5, coords = sheet.coords)
geom.update_all(sheet)

'''
Effector class:

An effector designates a dynamical term in the epithelium governing equation.
For quasi-static models, we need to provide a method to compute the energy associated
with this effector, and the corresponding gradient.

For example, we can consider a line tension effector. The energy is the sum of 
the tensions over all edges. For each half-edge, the gradient is defined by two terms,
one for the gradient term associated with the half-edge ij source, 
the other for it's target.

The positional derivative of energy is composed of a term that sums over all the 
edges which vertex i is a source, and another term that sums over all edges which
vertex i is a target.

Here is the definition of the line tension effector:

'''

'''
# =============================================================================
class LineTension(AbstractEffector):
    dimension = units.line_tension
    magnitude = 'line_tension'
    label = 'Line tension'
    element = 'edge'
    specs = {'edge':{'is_active':1, 'line_tension':1e-2}}
    
    spatial_ref = 'mean_length', units.length
    
    @staticmethod
    def energy(eptm):
        return eptm.edge_df.eval(
            "line_tension" "* is_active" "* length / 2"
        )  # accounts for half edges

    @staticmethod
    def gradient(eptm):
        grad_srce = -eptm.edge_df[eptm.ucoords] * to_nd(
            eptm.edge_df.eval("line_tension * is_active/2"), len(eptm.coords)
        )
        grad_srce.columns = ["g" + u for u in eptm.coords]
        grad_trgt = -grad_srce
        return grad_srce, grad_trgt
# =============================================================================
other examples are in the "tyssue.dynamics.effectors" module.
'''    

'''
Model factory:

These effectors are then aggregated with others to define a model object. This
object will have two methods compute_energy and compute_gradient that take an 
Epithelium object as single argument.

Such a model will usually be built with the function model_factory, that takes
a list of effectors as input and returns a model object. For example, we can define
the model from Farhadifar et al. by:

'''

model = model_factory([
    effectors.LineTension,
    effectors.FaceContractility,
    effectors.FaceAreaElasticity
    ])

# As for other parts, the parameters are defined by a nested dictionary 'spec'.
# Default values are gathered in the model.spec attribute:

model.specs

# We can use sheet.update_spec to set the correct columns in the sheet object.
# Once the column are set, it is possible to sets parameters for a subsets of edges
# by indexing the edges with a boolean series:
sheet.edge_df.loc[sheet.edge_df['sx']<0, 'line_tension'] = 0.5
sheet.update_specs(model.specs, reset=True)

'''
Compute energy:

'''

geom.update_all(sheet)
energy = model.compute_energy(sheet)    # Returns a scalar value
print(f'Total energy: {energy: .3f}')

# We can compute all energy terms with the full_output = True:
Et, Ec, Ea = model.compute_energy(sheet, full_output=True)
Et.head()

fig, ax = sheet_view(
    sheet,
    coords = list('zy'),
    face = {'visible': True, 'color':Ec, 'colormap':'gray'},
    edge = {'color': Et}
    )


'''
Computing the gradient

By default, the gradient computes an array of shape(Nv, 3), with 3 coordinates
(or 2 in 2D) for each vertex.

'''

grad_E = model.compute_gradient(sheet)
grad_E.head()

gradients = model.compute_gradient(sheet, components=True) # Returns a tuple of terms for each effector of the model.
gradients = {label: (srce, trgt) for label, (srce, trgt) in zip(model.labels, gradients)}
gradients['Line tension'][0].head()

'''
Plotting forces

The tyssue.draw defines a useful plot_forces function.

'''

fig, ax = plot_forces(sheet, geom, model, ['z', 'y'], scaling = 1)
fig.set_size_inches(10, 12)



'''
This is the end of the file.
'''
