#!/usr/bin/env python

from __future__ import print_function
import sys
import os
import glob
import time
from random import shuffle

PWD = '/home/simon/git/RocAlphaGo'
WIGHTPATH = 'data/weight2/'
WIGHTFILE = 'weights.{:05d}.hdf5'
WEIGHFILEPATH = WIGHTPATH + WIGHTFILE
EPOCH = 3
os.chdir(PWD)

while True:
    train_data = glob.glob('data/hdf/KGS-*.hdf5')
    weights = sorted(glob.glob(WIGHTPATH + 'weights.*.hdf5'))
    max_weight = 0
    if len(weights) > 0:
        max_weight = int(weights[-1][-10:-5])

    shuffle(train_data)
    for tfile in train_data:
        shuffle_file = os.path.join(WIGHTPATH, 'shuffle.npz')
        if os.path.exists(shuffle_file):
            os.remove(shuffle_file)
            
        cmd = 'export PYTHONPATH={}; '.format(PWD)
        cmd += 'python AlphaGo/training/supervised_policy_trainer.py data/models/policy_model2.json '
        if not os.path.isdir(WIGHTPATH):
            os.mkdir(WIGHTPATH)
        cmd += '{} {} -E {}'.format(tfile, WIGHTPATH, EPOCH)
        if os.path.isfile(WEIGHFILEPATH.format(EPOCH-1)):
            cmd += ' --weights ' + WIGHTFILE.format(EPOCH-1)
        print(cmd)        
        res = os.system(cmd) # run cmd

        if res == 0:
            max_weight += 1
            cmd2 = 'cp {} {}'.format(WEIGHFILEPATH.format(EPOCH-1), WEIGHFILEPATH.format(max_weight))
            print(cmd2)
            os.system(cmd2) # run cmd2

        print('press Ctrl-C to break the loop.   Wait 3 seconds.')
        time.sleep(3)
