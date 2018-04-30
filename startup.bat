echo off
pushd %~dp0
title IRSpectrum Init
echo Initializing...
pip install -r requirements.txt
npm install
updatedb.py
node main.js