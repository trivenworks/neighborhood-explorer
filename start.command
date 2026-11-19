#!/bin/zsh
cd -- "${0:A:h}" || exit 1
python3 scripts/dev_server.py --port 8767
