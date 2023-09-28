#!/usr/bin/sh
conda create -n py3_32
conda activate py3_32
conda config --env --set subdir linux-32
conda install python=3 gxx_linux-32
