#! /bin/sh
python3.8 scripts/01-create-uterrances.py
python3.8 scripts/02-upload-uterrances.py
python3.8 scripts/03-train-model.py
python3.8 scripts/04-get-evaluation.py
python3.8 scripts/05-deploy-model.py
python3.8 scripts/06-unit-test.py
