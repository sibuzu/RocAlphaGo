#!/bin/sh 

PLAYER1="gnugo --mode gtp"
PLAYER2="player/ChickBot.py"
TWOGTP="gogui-twogtp -black \"$PLAYER1\" -white \"$PLAYER2\" -games 10 \
  -size 19 -alternate -sgffile gnugo5"
gogui -size 19 -program "$TWOGTP" -computer-both -auto
rm -f gnugo5.html gnugo5.summary.dat
gogui-twogtp -analyze gnugo5.dat
