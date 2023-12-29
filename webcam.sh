#!/bin/bash
mjpg_streamer -i "input_uvc.so -d /dev/video0 -r 320x240" -o "output_http.so -w ./www"
${mjpg_streamer_command}
