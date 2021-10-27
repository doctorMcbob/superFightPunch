#!/bin/bash
s=""
for ((n=0;n<=200;n++))
do
	s="${s} ${n}.png"
done

convert -delay 2 -loop 0  ${s} replay.gif

