#!/bin/bash
# OCR 프로그램 실행 스크립트

cd "$(dirname "$0")"
source ocr_env/bin/activate
python multilang_ocr.py