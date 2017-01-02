#!/usr/bin/env python

from __future__ import print_function
import argparse

MODEL = 'data/models/policy_cnn12.json'
WEIGHTS = 'data/models/weights_cnn12.hdf5'

def play(model, weight):
    from AlphaGo.ai import GreedyPolicyPlayer
    from AlphaGo.models.policy import CNNPolicy
    from interface.gtp_wrapper import run_gtp, ExtendedGtpEngine
    import keras
    import tensorflow as tf
    from keras.backend import tensorflow_backend as K

    config = tf.ConfigProto()
    config.gpu_options.allow_growth = True
    K.set_session(tf.Session(config=config))

    model = CNNPolicy.load_model(MODEL)
    model.model.load_weights(WEIGHTS)

    # policy.model.summary()

    player = GreedyPolicyPlayer(model)
    run_gtp(player, name="ChickBot", version="0.1", helper_level=15, debug=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run ChickBot Go Bot')
    parser.add_argument('--model', default=MODEL,
                        help='DL network model')
    parser.add_argument('--weights', default=WEIGHTS,
                        help='DL network weights')

    args = parser.parse_args()

    print("MODEL: {}".format(args.model))
    print("WEIGHTS: {}".format(args.weights))
    play(args.model, args.weights)

