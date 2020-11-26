#!/bin/sh

sudo rm /lib/x86_64-linux-gnu/libm.so.6
sudo ln -s /opt/glibc-2.27/lib/libm-2.27.so /lib/x86_64-linux-gnu/libm.so.6