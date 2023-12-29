#!/bin/bash
cd ~/mjpg-streamer/mjpg-streamer-experimental
export LD_LIBRARY_PATH=.
mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 320x240" -o "output_http.so -w ./www"
${mjpg_streamer_command}