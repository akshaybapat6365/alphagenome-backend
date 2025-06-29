#!/bin/bash
echo "Starting build..."
python --version
pip --version
pip install --upgrade pip
pip install -r requirements.txt
echo "Build completed!"