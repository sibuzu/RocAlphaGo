#!/usr/bin/env python

from AlphaGo.ai import GreedyPolicyPlayer
from AlphaGo.models.policy import CNNPolicy
from interface.gtp_wrapper import run_gtp

MODEL = 'tests/test_data/minimodel.json'
WEIGHTS = 'tests/test_data/hdf5/random_minimodel_weights.hdf5'

policy = CNNPolicy.load_model(MODEL)
policy.model.load_weights(WEIGHTS)

# policy.model.summary()

player = GreedyPolicyPlayer(policy)

run_gtp(player)
