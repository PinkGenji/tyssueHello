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

from scipy import optimize

from tyssue import Sheet, config
from tyssue import SheetGeometry as geom
from tyssue.dynamics import effectors, model_factory
from tyssue.draw import sheet_view
from tyssue.draw.plt_draw import plot_forces
from tyssue.io import hdf5



os.chdir(r'/Users/bruceyu/Documents/GitHub/tyssueHello')


h5store = 'small_hexagonal.hf5'
# h5store = 'data/before_apoptosis.hf5'

os.path.isfile(h5store) #check if the working directory has been set correctly.

datasets = hdf5.load_datasets(h5store)
sheet = Sheet('emin', datasets)
sheet.sanitize(trim_borders=True, order_edges=True)

geom.update_all(sheet)

sqrt_area = sheet.face_df['area'].mean()**0.5
geom.scale(sheet, 1/sqrt_area, sheet.coords)

fig, ax = sheet_view(sheet, ['z', 'x'], mode = 'quick')











'''
This is the end of the file.
'''

