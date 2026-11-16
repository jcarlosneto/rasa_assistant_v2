#!/bin/bash
# Atalho mantido da versao 1. O trabalho de verdade esta em run.py (multiplataforma).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec python3 "$DIR/run.py" train
