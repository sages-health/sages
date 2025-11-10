#
# Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#

python -m PyInstaller --clean --noconfirm  vims.spec
cp -r ../frontend/dist/spa dist/vims/dist
cp ../executable-files/app.config.py dist/vims/
cp ../executable-files/connection-info--local.json dist/vims/
cp ../executable-files/roles.config.py dist/vims/
cp ../executable-files/roles.json dist/vims/
cp ../executable-files/sages.db dist/vims/
cp ../executable-files/run.sh dist/vims/
