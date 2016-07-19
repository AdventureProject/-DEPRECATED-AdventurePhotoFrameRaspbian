#!/bin/sh

python /app/update.py

# Setup our permissions
chown -R root:root *
chmod 777 -R *