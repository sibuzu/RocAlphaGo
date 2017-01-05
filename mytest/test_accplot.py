#!/usr/bin/env python

from __future__ import print_function
import h5py 
import numpy as np
from AlphaGo.models.policy import CNNPolicy
from keras.optimizers import SGD
import matplotlib.pyplot as plt
import glob
import os

def one_hot_action(action, size=19):
    """Convert an (x,y) action into a size x size array of zeros with a 1 at x,y
    """
    categorical = np.zeros((size, size))
    categorical[action] = 1
    return categorical

def run():
    import argparse
    parser = argparse.ArgumentParser(description='Perform supervised training on a policy network.')

    # required args
    parser.add_argument("model", help="i.e. data/models/model_cnn12_dropout.json")  # noqa: E501
    parser.add_argument("weights", help="weight path, i.e. data/weight2/")
    parser.add_argument("features", help="feature files, i.e. data/hdf/KGS-050.hdf5")

    # load model & weigts
    args = parser.parse_args()
    policy = CNNPolicy.load_model(args.model)
    model = policy.model
    policy.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=["accuracy"])
    # model.summary()

    # load data
    stride = 100
    dataset = h5py.File(args.features)
    states = np.array(dataset['states'])[::stride]
    action_xy = np.array(dataset['actions'])[::stride]
    n_total_data = states.shape[0]
    print("n = {}, keys = {}".format(n_total_data, dataset.keys()))
    print("actionxy =>", action_xy.shape)

    # tarnsfer statexy to states
    actions = np.zeros((n_total_data, 361))
    for i in range(n_total_data):
        # tuple is necessay and important, [13 16] --> (13, 16)
        actions[i] = one_hot_action(tuple(action_xy[i])).flatten()
    print("actions =>", actions.shape)

    # evaluate
    wfiles = sorted(glob.glob(os.path.join(args.weights, '*.hdf5')))
    nw = len(wfiles)
    acc = np.zeros(nw)
    for i in range(nw):
        model.load_weights(wfiles[i])
        result = policy.model.evaluate(states, actions)
        acc[i] = result[1]
        print("acc[{}]={}".format(i, acc[i]))
    plt.plot(acc)
    plt.show()

def limit_gpu_memory(fraction = 0.4):
    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = fraction
    set_session(tf.Session(config=config))

def auto_gpu_memory():
    import tensorflow as tf
    from keras.backend.tensorflow_backend import set_session
    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    set_session(tf.Session(config=config))

if __name__ == '__main__':
    limit_gpu_memory()
    run()
