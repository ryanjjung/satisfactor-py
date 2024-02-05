#!/bin/bash

# Only Fedora is supported right now

sudo dnf install \
    gcc \
    gobject-introspection-devel \
    cairo-gobject-devel \
    pkg-config \
    python3-devel \
    gtk4

pip install -r requirements.txt
