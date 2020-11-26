#!/bin/bash

redis-cli flushall
python3 visualization/open3d/run_open3d_visualizer.py &

python main.py 
