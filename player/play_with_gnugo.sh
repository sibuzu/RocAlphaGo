#!/bin/sh 

PLAYER1="gnugo --mode gtp --level 5"
PLAYER2="player/ChickBot.py"
gogui -program "gogui-twogtp -black \"$PLAYER1\" -white \"$PLAYER2\""