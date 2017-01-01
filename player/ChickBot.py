#!/usr/bin/env python

from AlphaGo.ai import GreedyPolicyPlayer
from AlphaGo.models.policy import CNNPolicy
from interface.gtp_wrapper import run_gtp, ExtendedGtpEngine

import keras
import tensorflow as tf
from keras.backend import tensorflow_backend as K

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
K.set_session(tf.Session(config=config))

MODEL = 'data/models/policy_model.json'
WEIGHTS = 'data/weights/weights.00100.hdf5'

policy = CNNPolicy.load_model(MODEL)
policy.model.load_weights(WEIGHTS)

# policy.model.summary()

player = GreedyPolicyPlayer(policy)

run_gtp(player, name="ChickBot", version="0.1", helper_level=15, debug=True)
