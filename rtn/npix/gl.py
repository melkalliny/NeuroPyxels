# -*- coding: utf-8 -*-
"""
2018-07-20

@author: Maxime Beau, Neural Computations Lab, University College London

Dataset: Neuropixels dataset -> dp is phy directory (kilosort or spyking circus output)
"""
import os
import os.path as op

import numpy as np
import pandas as pd

from rtn.utils import npa

def assert_multidatasets(dp):
    'Returns unpacked merged_clusters_spikes.npz if it exists in dp, None otherwise.'
    if op.exists(op.join(dp, 'merged_clusters_spikes.npz')):
        mcs=np.load(op.join(dp, 'merged_clusters_spikes.npz'))
        return mcs[list(mcs.keys())[0]]

def chan_map(probe_version='3A', dp=None, y_orig='surface'):
    assert y_orig in ['surface', 'tip']
    assert probe_version in ['3A', '1.0_staggered', '1.0_aligned', '2.0_singleshank', '2.0_fourshanked', 'local']
    
    if probe_version in probe_version in ['3A', '1.0_staggered']:
        Nchan=384
        cm_el = npa([[  27,   0],
                           [  59,   0],
                           [  11,   20],
                           [  43,   20]])
        vert=npa([[  0,   40],
                  [  0,   40],
                  [  0,   40],
                  [  0,   40]])
        
        cm=cm_el.copy()
        for i in range(int(Nchan/cm_el.shape[0])-1):
            cm = np.vstack((cm, cm_el+vert*(i+1)))
        cm=np.hstack([np.arange(Nchan).reshape(Nchan,1), cm])
    
    elif probe_version=='1.0_aligned':
        Nchan=384
        cm_el = npa([[  11,   0],
                           [  43,   0]])
        vert=npa([[  0,   20],
                  [  0,   20]])
        
        cm=cm_el.copy()
        for i in range(int(Nchan/cm_el.shape[0])-1):
            cm = np.vstack((cm, cm_el+vert*(i+1)))
        cm=np.hstack([np.arange(Nchan).reshape(Nchan,1), cm])
        
    elif probe_version=='2.0_singleshank':
        Nchan=384
        cm_el = npa([[  0,   0],
                           [  32,   0]])
        vert=npa([[  0,   15],
                  [  0,   15]])
        
        cm=cm_el.copy()
        for i in range(int(Nchan/cm_el.shape[0])-1):
            cm = np.vstack((cm, cm_el+vert*(i+1)))
        cm=np.hstack([np.arange(Nchan).reshape(Nchan,1), cm])
    
    elif probe_version=='local':
        if dp is None:
            raise ValueError("dp argument is not provided - when channel map is \
                             atypical and probe_version is hence called 'local', \
                             the datapath needs to be provided to load the channel map.")
        c_ind=np.load(op.join(dp, 'channel_map.npy'));cp=np.load(op.join(dp, 'channel_positions.npy'));
        cm=npa(np.hstack([c_ind, cp]), dtype=np.int32)
        
    if y_orig=='surface':
        cm[:,1:]=cm[:,1:][::-1]
        
    return cm

def load_units_qualities(dp):
    f1='cluster_group.tsv'
    f2='cluster_groups.csv'
    if os.path.isfile(op.join(dp, f1)):
        qualities = pd.read_csv(f1,delimiter='	')
    elif os.path.isfile(op.join(dp, f1)):
        qualities = pd.read_csv('merged_'+f1,delimiter='	')
    elif os.path.isfile(f2):
        qualities = pd.read_csv(op.join(dp, f2))
    elif os.path.isfile(f2):
        qualities = pd.read_csv(op.join(dp, 'merged_'+f2))
    else:
        print('cluster groups table not found in provided data path. Exiting.')
        return
    return qualities

def get_units(dp, quality='all'):
    assert quality in ['all', 'good', 'mua', 'noise']
    
    cl_grp = load_units_qualities(dp)
    
    if 'dataset' in cl_grp.columns:
        units=['{}_{}'.format(cl_grp.loc[i, 'dataset_i'], cl_grp.loc[i, 'cluster_id']) for i in cl_grp.index if cl_grp.loc[i, 'group']=='good']
        return units
        
    else:
        cl_grp = load_units_qualities(dp)
        try:
            np.all(np.isnan(cl_grp['group'])) # Units have not been given a class yet
            units=[]
        except:
            if quality=='all':
                units = cl_grp.loc[:, 'cluster_id']
            else:
                units = cl_grp.loc[np.nonzero(cl_grp['group']==quality)[0], 'cluster_id']
        return np.array(units, dtype=np.int64)

def get_good_units(dp):
    return get_units(dp, quality='good')
