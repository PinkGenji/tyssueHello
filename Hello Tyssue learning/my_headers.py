# -*- coding: utf-8 -*-
"""
This script contains all my personal defined functions to be used.
"""
import numpy as np
import pandas as pd
import math
from tyssue.topology.sheet_topology import type1_transition
from tyssue.topology.base_topology import add_vert
from tyssue.topology.sheet_topology import face_division
from tyssue import PlanarGeometry as geom
from tyssue.dynamics.planar_vertex_model import PlanarModel as model


  
def dot(v,w):
    x,y = v
    X,Y = w
    return x*X + y*Y
  
def length(v):
    x,y = v
    return math.sqrt(x*x + y*y)
  
def vector(b,e):
    """
    Creates a vector: b-e (arrow from e to b), stored as a tuple.

    """
    x,y = b
    X,Y = e
    return (round(X-x,5),round(Y-y , 5))
  
def unit(v):
    x,y = v
    mag = length(v)
    return (x/mag, y/mag)
  
def distance(p0,p1):
    return length(vector(p0,p1))
  
def scale(v,sc):
    x,y = v
    return (x * sc, y * sc)
  
def add(v,w):
    x,y = v
    X,Y = w
    return (x+X, y+Y)

def delete_face(sheet_obj, face_deleting):
    """

    
    Parameters
    ----------
    sheet_obj : Epithelium
        An Epithelium 'Sheet' object from Tyssue.
    face_deleting : Int
        The index of the face to be deleted.

    Returns
    -------
    A Pandas Data Frame that deletes the face, with border edges are single
    arrowed, without index resetting.

    """
    # Compute all edges associated with the face, then drop these edges in df.
    associated_edges = sheet_obj.edge_df[sheet_obj.edge_df['face'] == face_deleting]
    sheet_obj.edge_df.drop(associated_edges.index, inplace = True)
    
    # All associated edges are removed, now remove the 'empty' face and reindex.
    sheet_obj.face_df.drop(face_deleting , inplace =True)


def xprod_2d(vec1, vec2):
    """
    

    Parameters
    ----------
    vec1 : Iterable
        First vector
    vec2 : Iterable
        Second vector

    Returns
    -------
    A scalar value that is the 2D cross product,
    equivalent to setting z=0 in 3D.

    """
    scalar = vec1[0]*vec2[1] - vec1[1]*vec2[0]
    return scalar

def closest_pair_dist(a,end1, end2):
    towards_end1 = distance(end1, a)
    towards_end2 = distance(end2, a)
    if towards_end1 < towards_end2:
        return towards_end1, end1
    elif towards_end1 > towards_end2:
        return towards_end2, end2

def put_vert(eptm, edge, coord_put):
    """Adds a vertex somewhere in the an edge,

    which is split as is its opposite(s)

    Parameters
    ----------
    eptm : a :class:`Epithelium` instance
    edge : int
    the index of one of the half-edges to split
    coord_put: list
    the coordinate of the new vertex to be put

    Returns
    -------
    new_vert : int
    the index to the new vertex
    new_edges : int or list of ints
    index to the new edge(s). For a sheet, returns
    a single index, for a 3D epithelium, returns
    the list of all the new parallel edges
    new_opp_edges : int or list of ints
    index to the new opposite edge(s). For a sheet, returns
    a single index, for a 3D epithelium, returns
    the list of all the new parallel edges


    In the simple case whith two half-edge, returns
    indices to the new edges, with the following convention:

    s    e    t
      ------>
    * <------ *
    oe

    s    e       ne   t
      ------   ----->
    * <----- * ------ *
        oe   nv   noe

    where "e" is the passed edge as argument, "s" its source "t" its
    target and "oe" its opposite. The returned edges are the ones
    between the new vertex and the input edge's original target.
    """

    srce, trgt = eptm.edge_df.loc[edge, ["srce", "trgt"]]
    opposites = eptm.edge_df[
        (eptm.edge_df["srce"] == trgt) & (eptm.edge_df["trgt"] == srce)
    ]
    parallels = eptm.edge_df[
        (eptm.edge_df["srce"] == srce) & (eptm.edge_df["trgt"] == trgt)
    ]

    new_vert = eptm.vert_df.loc[srce:srce]
    eptm.vert_df = eptm.vert_df.append(new_vert, ignore_index=True)
    new_vert = eptm.vert_df.index[-1]
    eptm.vert_df.loc[new_vert, eptm.coords] = coord_put
    new_edges = []

    for p, p_data in parallels.iterrows():
        eptm.edge_df.loc[p, "trgt"] = new_vert
        eptm.edge_df = eptm.edge_df.append(p_data, ignore_index=True)
        new_edge = eptm.edge_df.index[-1]
        eptm.edge_df.loc[new_edge, "srce"] = new_vert
        eptm.edge_df.loc[new_edge, "trgt"] = trgt
        new_edges.append(new_edge)

    new_opp_edges = []
    for o, o_data in opposites.iterrows():
        eptm.edge_df.loc[o, "srce"] = new_vert
        eptm.edge_df = eptm.edge_df.append(o_data, ignore_index=True)
        new_opp_edge = eptm.edge_df.index[-1]
        eptm.edge_df.loc[new_opp_edge, "trgt"] = new_vert
        eptm.edge_df.loc[new_opp_edge, "srce"] = trgt
        new_opp_edges.append(new_opp_edge)

    # ## Sheet special case
    if len(new_edges) == 1:
        new_edges = new_edges[0]
    if len(new_opp_edges) == 1:
        new_opp_edges = new_opp_edges[0]
    elif len(new_opp_edges) == 0:
        new_opp_edges = None
    return new_vert, new_edges, new_opp_edges


def divisibility_check(eptm, cell_id):
    """
    

    Parameters
    ----------
    eptm : epithelium object
        
    cell_id : int
        The index of the cell being checked

    Returns
    -------
    Boolean, True for 'can divide', False for 'cannot divide'

    """
    eptm.get_opposite()
    if any(eptm.edge_df[eptm.edge_df.loc[:,'face'] == cell_id].loc[:,'opposite']==-1) == True:
        return True
    else:
        return False



def lateral_split(eptm, mother):
    """
    Split the cell by choosing one of the edges to be a basal edge.

    Parameters
    ----------
    eptm : a: Class: 'Epithelium' instance

    mother : int
        the index of the mother cell.

    Returns
    -------
    daughter: face index of new cell.

    """
    edge_in_cell = eptm.edge_df[eptm.edge_df.loc[:,'face'] == mother]
    # Obtain the index for one of the basal edges.
    basal_edges = edge_in_cell[ edge_in_cell.loc[:,'opposite']==-1 ]
    basal_edge_index = basal_edges.index[np.random.randint(0,len(basal_edges))]
    #get the vertex index of the newly added mid point.
    basal_mid = add_vert(eptm, edge = basal_edge_index)[0]
    geom.update_all(eptm)

    # re-rewite the edge_in_cell to include the new vertex.
    edge_in_cell = eptm.edge_df[eptm.edge_df.loc[:,'face'] == mother]
    condition = edge_in_cell.loc[:,'srce'] == basal_mid
    # extract the x-coordiante from array, then convert to a float type.
    
    # Extract the centre vertex.
    c0x = float(edge_in_cell[condition].loc[:,'fx'].values[0])
    c0y = float(edge_in_cell[condition].loc[:,'fy'].values[0])
    c0 = [c0x, c0y]
    cent_dict = {'y': c0y, 'is_active': 1, 'x': c0x}
    eptm.vert_df = eptm.vert_df.append(cent_dict, ignore_index = True)
    # The append function adds the new row in the last row, we the use iloc to 
    # get the index of the last row, hence the index of the centre point.
    cent_index = eptm.vert_df.index[-1]
    
    # Extract for source vertex coordinates
    p0x = float(edge_in_cell[condition].loc[:,'sx'].values[0])
    p0y = float(edge_in_cell[condition].loc[:,'sy'].values[0])
    p0 = [p0x, p0y]

    # Extract the directional vector.
    rx = float(edge_in_cell[condition].loc[:,'rx'].values[0])
    ry = float(edge_in_cell[condition].loc[:,'ry'].values[0])
    r  = [-rx, -ry]   # use the line in opposite direction.
    
    # We need to use iterrows to iterate over rows in pandas df
    # The iteration has the form of (index, series)
    # The series can be sliced.
    for index, row in edge_in_cell.iterrows():
        s0x = row['sx']
        s0y = row['sy']
        t0x = row['tx']
        t0y = row['ty']
        v1 = [s0x-p0x,s0y-p0y]
        v2 = [t0x-p0x,t0y-p0y]
        # if the xprod_2d returns negative, then line intersects the line segment.
        if xprod_2d(r, v1)*xprod_2d(r, v2) < 0:
            #print(f'The edge that is intersecting is: {index}')
            dx = row['dx']
            dy = row['dy']
            c1 = (dx*ry/rx)-dy
            c2 = s0y-p0y - (s0x*ry/rx) + (p0x*ry/rx)
            k=c2/c1
            intersection = [s0x+k*dx, s0y+k*dy]
            oppo_index = int(put_vert(eptm, index, intersection)[0])
    # Do face division
    new_face_index = face_division(eptm, mother = mother, vert_a = basal_mid, vert_b = oppo_index )
    # Put a vertex at the centroid, on the newly formed edge (last row in df).
    put_vert(eptm, edge = eptm.edge_df.index[-1], coord_put = c0)
    eptm.update_num_sides()
    return new_face_index
    #second_half = face_division(eptm, mother = mother, vert_a = oppo_index, vert_b = cent_index)
    #print(f'The new edge has first half as: {first_half} and second half as: {second_half} ')


def lateral_division(sheet, manager, cell_id, division_rate):
    """Defines a lateral division behavior.
    The function is composed of:
        1. check if the cell is CT cell and ready to split.
        2. generate a random number from (0,1), and compare with a threshold.
        3. two daughter cells starts growing until reach a threshold.
        
    
    Parameters
    ----------
    sheet: a :class:`Sheet` object
    cell_id: int
        the index of the dividing cell
    crit_area: float
        the area at which 
    growth_speed: float
        increase in the area per unit time
        A_0(t + dt) = A0(t) + growth_speed
    """

    # if the cell area is larger than the crit_area, we let the cell divide.
    if sheet.face_df.loc[cell_id, "cell_type"] == 'CT' and sheet.face_df.loc[cell_id, 'division_status'] == 'ready':
        # A random float number is generated between (0,1)
        prob = np.random.uniform(0,1)
        if prob < division_rate:
            daughter = lateral_split(sheet, mother = cell_id)
            sheet.face_df.loc[cell_id,'growth_speed'] = (sheet.face_df.loc[cell_id,'prefered_area'] - sheet.face_df.loc[cell_id, 'area'])/5
            sheet.face_df.loc[cell_id, 'division_status'] = 'growing'
            sheet.face_df.loc[daughter,'growth_speed'] = (sheet.face_df.loc[daughter,'prefered_area'] - sheet.face_df.loc[daughter, 'area'])/5
            sheet.face_df.loc[daughter, 'division_status'] = 'growing'
            # update geometry
            geom.update_all(sheet)
        else:
            pass
            
    elif sheet.face_df.loc[cell_id, "cell_type"] == 'CT' and sheet.face_df.loc[cell_id, 'division_status'] == 'growing':
        sheet.face_df.loc[cell_id,'prefered_area'] = sheet.face_df.loc[cell_id,'area'] + sheet.face_df.loc[cell_id,'growth_speed']
        if sheet.face_df.loc[cell_id,'area'] <= sheet.face_df.loc[cell_id,'prefered_area']:
            # restore division_status and prefered_area
            sheet.face_df.loc[cell_id, 'division_status'] = 'ready'
            sheet.face_df.loc[cell_id, "prefered_area"] = 1.0
    else:
        pass

def T1_check(eptm, threshold, scale):
    for i in eptm.sgle_edges:
        if eptm.edge_df.loc[i,'length'] < threshold:
            type1_transition(eptm, edge01 = i, multiplier= scale)
            print(f'Type 1 transition applied to edge {i} \n')
        else:
            continue
    
def my_ode(eptm):
    valid_verts = eptm.active_verts[eptm.active_verts.isin(eptm.vert_df.index)]
    grad_U = model.compute_gradient(eptm).loc[valid_verts]
    dr_dt = -grad_U.values/eptm.vert_df.loc[valid_verts, 'viscosity'].values[:,None]
    return dr_dt


def collapse_edge(sheet, edge, reindex=True, allow_two_sided=False):
    """Collapses edge and merges it's vertices, creating (or increasing the rank of)
    a rosette structure.

    If `reindex` is `True` (the default), resets indexes and topology data.
    The edge is collapsed on the smaller of the srce, trgt indexes
    (to minimize reindexing impact)

    Returns the index of the collapsed edge's remaining vertex (its srce)

    """

    srce, trgt = np.sort(sheet.edge_df.loc[edge, ["srce", "trgt"]]).astype(int)

    # edges = sheet.edge_df[
    #     ((sheet.edge_df["srce"] == srce) & (sheet.edge_df["trgt"] == trgt))
    #     | ((sheet.edge_df["srce"] == trgt) & (sheet.edge_df["trgt"] == srce))
    # ]

    # has_3_sides = np.any(
    #     sheet.face_df.loc[edges["face"].astype(int), "num_sides"] < 4
    # )
    # if has_3_sides and not allow_two_sided:
    #     warnings.warn(
    #         f"Collapsing edge {edge} would result in a two sided face, aborting"
    #     )
    #     return -1

    sheet.vert_df.loc[srce, sheet.coords] = sheet.vert_df.loc[
        [srce, trgt], sheet.coords
    ].mean(axis=0)
    sheet.vert_df.drop(trgt, axis=0, inplace=True)
    # rewire
    sheet.edge_df.replace({"srce": trgt, "trgt": trgt}, srce, inplace=True)
    # all the edges parallel to the original
    collapsed = sheet.edge_df.query("srce == trgt")
    sheet.edge_df.drop(collapsed.index, axis=0, inplace=True)
    return srce

def split_vert(sheet, vert, face, to_rewire, epsilon, recenter=False):
    """Creates a new vertex and moves it towards the center of face.

    The edges in to_rewire will be connected to the new vertex.

    Parameters
    ----------

    sheet : a :class:`tyssue.Sheet` instance
    vert : int, the index of the vertex to split
    face : int, the index of the face where to move the vertex
    to_rewire : :class:`pd.DataFrame` a subset of `sheet.edge_df`
        where all the edges pointing to (or from) the old vertex will point
        to (or from) the new.

    Note
    ----

    This will leave opened faces and cells

    """

    # Add a vertex
    this_vert = sheet.vert_df.loc[vert:vert]  # avoid type munching
    sheet.vert_df = pd.concat([sheet.vert_df, this_vert], ignore_index=True)

    new_vert = sheet.vert_df.index[-1]
    # Move it towards the face center
    r_ia = sheet.face_df.loc[face, sheet.coords] - sheet.vert_df.loc[vert, sheet.coords]
    shift = r_ia * epsilon / np.linalg.norm(r_ia)
    if recenter:
        sheet.vert_df.loc[new_vert, sheet.coords] += shift / 2.0
        sheet.vert_df.loc[vert, sheet.coords] -= shift / 2.0

    else:
        sheet.vert_df.loc[new_vert, sheet.coords] += shift

    # rewire
    sheet.edge_df.loc[to_rewire.index] = to_rewire.replace(
        {"srce": vert, "trgt": vert}, new_vert
    )


def type1_transition_custom(sheet, edge01, multiplier=1.5):
    """Performs a type 1 transition around the specified edge, 
    reusing the collapsed edge's index and vertices for the newly created edge.

    Parameters
    ----------
    sheet : a `Sheet` instance
    edge01 : int
       Index of the edge around which the transition takes place
    remove_tri_faces : bool, optional
       If True (default), removes triangular cells after the T1 transition is performed
    multiplier : float, optional
       Default 1.5, multiplier to the threshold length for the new edge

    Returns
    -------
    int : The index of the newly created edge (same as the collapsed edge)
    """
    
    # Get the source, target, and face associated with edge01
    srce, trgt, face = sheet.edge_df.loc[edge01, ["srce", "trgt", "face"]].astype(int)

    # Step 1: Collapse the edge by merging vertices and updating positions
    vert = min(srce, trgt)  # Use the smaller index for consistency
    the_other_vert = max(srce,trgt)
    sheet.vert_df.loc[vert, sheet.coords] = sheet.vert_df.loc[[srce, trgt], sheet.coords].mean(axis=0)

    # Remove the target vertex (trgt) from vert_df and rewire edges
    sheet.vert_df.drop(trgt, inplace=True)
    sheet.edge_df.replace({"srce": trgt, "trgt": trgt}, vert, inplace=True)
    
    # Remove edges that have collapsed (where srce == trgt)
    collapsed_edges = sheet.edge_df.query("srce == trgt").index
    sheet.edge_df.drop(collapsed_edges, inplace=True)

    # Step 2: Create a new vertex and connect it to form a new edge
    # Add the new vertex by copying the coordinates of vert and shifting towards the face center
    new_vert_coords = sheet.vert_df.loc[vert, sheet.coords].copy()
    face_center = sheet.face_df.loc[face, sheet.coords]
    direction = face_center - new_vert_coords
    shift = (direction * multiplier / np.linalg.norm(direction)) / 2.0  # half shift for balance
    new_vert_coords += shift

    # Add new vertex to vert_df
    new_vert = sheet.vert_df.index.max() + 1
    sheet.vert_df.loc[new_vert] = new_vert_coords

    # Reassign edges initially pointing to vert to new_vert for the new connection
    to_rewire = sheet.edge_df[(sheet.edge_df["srce"] == vert) | (sheet.edge_df["trgt"] == vert)]
    sheet.edge_df.loc[to_rewire.index, ["srce", "trgt"]] = to_rewire.replace({vert: new_vert})

    # Step 3: Create the new edge using the same index as the original edge01
    sheet.edge_df.loc[edge01, ["srce", "trgt"]] = [vert, new_vert]
    sheet.edge_df.loc[edge01, "length"] = multiplier * sheet.settings.get("threshold_length", 1.0)


    return edge01

def division_1(sheet, rng, cent_data, cell_id, dt):
    """The cells keep growing, when the area exceeds a critical area, then
    the cell divides.
    
    Parameters
    ----------
    sheet: a :class:`Sheet` object
    cell_id: int
        the index of the dividing cell
    crit_area: float
        the area at which 
    growth_rate: float
        increase in the area per unit time
        A_0(t + dt) = A0(t) * (1 + growth_rate * dt)
    """
    condition = sheet.edge_df.loc[:,'face'] == cell_id
    edge_in_cell = sheet.edge_df[condition]
    # We need to randomly choose one of the edges in cell 2.
    chosen_index = rng.choice(list(edge_in_cell.index))
    # Extract and store the centroid coordinate.
    c0x = float(cent_data.loc[cent_data['face']==cell_id, ['fx']].values[0])
    c0y = float(cent_data.loc[cent_data['face']==cell_id, ['fy']].values[0])
    c0 = [c0x, c0y]

    # Add a vertex in the middle of the chosen edge.
    new_mid_index = add_vert(sheet, edge = chosen_index)[0]
    # Extract for source vertex coordinates of the newly added vertex.
    p0x = sheet.vert_df.loc[new_mid_index,'x']
    p0y = sheet.vert_df.loc[new_mid_index,'y']
    p0 = [p0x, p0y]

    # Compute the directional vector from new_mid_point to centroid.
    rx = c0x - p0x
    ry = c0y - p0y
    r  = [rx, ry]   # use the line in opposite direction.
    # We need to use iterrows to iterate over rows in pandas df
    # The iteration has the form of (index, series)
    # The series can be sliced.
    for index, row in edge_in_cell.iterrows():
        s0x = row['sx']
        s0y = row['sy']
        t0x = row['tx']
        t0y = row['ty']
        v1 = [s0x-p0x,s0y-p0y]
        v2 = [t0x-p0x,t0y-p0y]
        # if the xprod_2d returns negative, then line intersects the line segment.
        if xprod_2d(r, v1)*xprod_2d(r, v2) < 0 and index !=chosen_index :
            dx = row['dx']
            dy = row['dy']
            c1 = dx*ry-dy*rx
            c2 = s0y*rx-p0y*rx - s0x*ry + p0x*ry
            k=c2/c1
            intersection = [s0x+k*dx, s0y+k*dy]
            oppo_index = put_vert(sheet, index, intersection)[0]
            # Split the cell with a line.
            new_face_index = face_division(sheet, mother = cell_id, vert_a = new_mid_index , vert_b = oppo_index )
            # Put a vertex at the centroid, on the newly formed edge (last row in df).
            cent_index = put_vert(sheet, edge = sheet.edge_df.index[-1], coord_put = c0)[0]
            random_int_1 = rng.integers(10000, 15000) / 1000
            random_int_2 = rng.integers(10000, 15000) / 1000
            sheet.face_df.loc[cell_id,'T_cycle'] = np.array(random_int_1, dtype=np.float64)
            sheet.face_df.loc[new_face_index,'T_cycle'] = np.array(random_int_2, dtype=np.float64)
            sheet.face_df.loc[cell_id, 'T_age'] = dt
            sheet.face_df.loc[new_face_index,'T_age'] = dt
            print(f'cell {cell_id} is divided, dauther cell {new_face_index} is created.')
            return new_face_index

def time_step_bot(sheet,dt, max_dist_allowed):
    # Force computing and updating positions.
    valid_active_verts = sheet.active_verts[sheet.active_verts.isin(sheet.vert_df.index)]
    pos = sheet.vert_df.loc[valid_active_verts, sheet.coords].values
    # Compute the force with opposite of gradient direction.
    dot_r = my_ode(sheet)
    
    movement = dot_r*dt
    current_movement = np.linalg.norm(movement, axis=1)
    while max(current_movement) > max_dist_allowed:
        dt /=2
        movement = dot_r *dt
        current_movement = np.linalg.norm(movement, axis=1)
    return dt, movement


def boundary_nodes(sheet):
    """
    This returns a list of the vertex index that are boundary nodes.

    """
    boundary = set()
    for i in sheet.edge_df.index:
        if sheet.edge_df.loc[i,'opposite'] == -1:
            boundary.add(sheet.edge_df.loc[i,'srce'])
            boundary.add(sheet.edge_df.loc[i,'trgt'])
    boudnary_vert = sheet.vert_df.loc[list(boundary), ['x','y']]
    return boudnary_vert

def T3_detection(sheet, edge_index, d_min):
    """
    This detects if an edge will collide with another vertex within a d_min
    distance for both node1 and node2 zones. It returns a Boolean.
    """
    # Get the nodes of the edge
    node1 = sheet.edge_df.loc[edge_index, 'srce']
    node2 = sheet.edge_df.loc[edge_index, 'trgt']
    
    # Compute the radius of the detection zones
    radius = (1/4 * sheet.edge_df.loc[edge_index, 'length']**2 + d_min**2)**0.5
    
    # Get the coordinates of node1 and node2
    node1_coords = np.array(sheet.vert_df.loc[node1, ['x', 'y']])
    node2_coords = np.array(sheet.vert_df.loc[node2, ['x', 'y']])
    
    # Define the zones as dictionaries
    node1_zone = {
        'center': node1_coords,
        'radius': radius
    }
    node2_zone = {
        'center': node2_coords,
        'radius': radius
    }
    
    # Logic to check collision for both zones
    for idx, vertex in boundary_nodes(sheet).iterrows():
        if idx == node1 or idx == node2:
            continue  # Skip the nodes of the edge itself
        
        vertex_coords = np.array(vertex[['x', 'y']])
        
        # Check if the vertex is within node1's zone
        distance_to_node1 = np.linalg.norm(vertex_coords - node1_zone['center'])
        if distance_to_node1 < node1_zone['radius']:
            return True  # Collision detected in node1's zone
        
        # Check if the vertex is within node2's zone
        distance_to_node2 = np.linalg.norm(vertex_coords - node2_zone['center'])
        if distance_to_node2 < node2_zone['radius']:
            return True  # Collision detected in node2's zone

    return False  # No collision detected in either zone

def pnt2line(pnt, start, end):
    """
    Given a line with coordinates 'start' and 'end' and the
    coordinates of a point 'pnt' the proc returns the shortest 
    distance from pnt to the line and the coordinates of the 
    nearest point on the line.
    
    1  Convert the line segment to a vector ('line_vec').
    2  Create a vector connecting start to pnt ('pnt_vec').
    3  Find the length of the line vector ('line_len').
    4  Convert line_vec to a unit vector ('line_unitvec').
    5  Scale pnt_vec by line_len ('pnt_vec_scaled').
    6  Get the dot product of line_unitvec and pnt_vec_scaled ('t').
    7  Ensure t is in the range 0 to 1.
    8  Use t to get the nearest location on the line to the end
        of vector pnt_vec_scaled ('nearest').
    9  Calculate the distance from nearest to pnt_vec_scaled.
    10 Translate nearest back to the start/end line. 
    Malcolm Kesson 16 Dec 2012

    Parameters
    ----------
    pnt : coordinate of the point

    start : coordinate of the starting point of the line segment
    end : coordinate of the end point of the line segment

    Returns
    -------
    tuple type. (dist, nearest)
    dist : float, distance between the point and line segment
    nearest : tuple of coordinates in floats of the nearest point on the line

    """
    line_vec = vector(start, end)
    pnt_vec = vector(start, pnt)
    line_len = length(line_vec)
    line_unitvec = unit(line_vec)
    pnt_vec_scaled = scale(pnt_vec, 1.0/line_len)
    t = dot(line_unitvec, pnt_vec_scaled)    
    if t < 0.0:
        t = 0.0
    elif t > 1.0:
        t = 1.0
    nearest = scale(line_vec, t)
    dist = distance(nearest, pnt_vec)
    nearest = add(nearest, start)
    return dist, nearest

def edge_extension(sheet, edge_id, total_extension):
    """
    Extends the edge equally on both ends of the line segment.

    Parameters
    ----------
    sheet : eptm instance
        Instance of the simulation object containing the cell sheet.
    edge_id : int
        Index of the edge to extend.
    total_extension : float
        Total length to add to the edge (split equally between source and target).

    Returns
    -------
    None.
    """
    import numpy as np  # Ensure NumPy is imported

    # Extract source and target vertex IDs
    srce_id, trgt_id = sheet.edge_df.loc[edge_id, ['srce', 'trgt']]
    
    # Extract source and target positions as numpy arrays
    srce = sheet.vert_df.loc[srce_id, ['x', 'y']].values
    trgt = sheet.vert_df.loc[trgt_id, ['x', 'y']].values
    # Compute the unit vector in the direction of the edge
    a = trgt - srce  # Vector from source to target
    a_hat = a / np.linalg.norm(a)  # Convert to unit vector (NumPy array)
    # Compute the extension vector
    extension = a_hat * total_extension / 2  # NumPy array supports elementwise operations
    
    # Update the source and target positions
    sheet.vert_df.loc[srce_id, ['x', 'y']] -= extension
    sheet.vert_df.loc[trgt_id, ['x', 'y']] += extension
    
    # Update geometry
    geom.update_all(sheet)
    

def adjacency_check(sheet, vert1, vert2):
    """
    Returns True if vert1 and vert2 are connected by an edge. Otherwise False
    """
    
    exists = sheet.edge_df[
        ((sheet.edge_df['srce'] == vert1) & (sheet.edge_df['trgt'] == vert2)) |
        ((sheet.edge_df['srce'] == vert2) & (sheet.edge_df['trgt'] == vert1))
    ].any().any()  # Checks if any rows satisfy the condition

    return exists  # Return True if such a row exists, False otherwise

def adjacent_vert(sheet, v, srce_id, trgt_id):
        
    adjacent = None
    if adjacency_check(sheet, v, srce_id)==True:
        adjacent = srce_id
    elif adjacency_check(sheet, v, trgt_id)==True:
        adjacent = trgt_id
    return adjacent
            
def T3_eating(sheet, edge_id, vert_id):
    """
    This function internalize the vertex into the edge with edge_id.

    Parameters
    ----------
    sheet : emtp instance
    
    edge_id : Int

    vert_id : Int

    Returns
    -------
    None.

    """
    

    
        


""" This is the end of the script. """
