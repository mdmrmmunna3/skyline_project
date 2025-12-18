#!/bin/bash
source venv/bin/activate
export SKYLINE_CONFIG_FILE=$(pwd)/etc/skyline.yaml
uvicorn skyline_apiserver.main:app --host 0.0.0.0 --port 9999 --reload
