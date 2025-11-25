#
# Copyright (c) 2013 - 2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#
cd ../frontend
npm install -g @quasar/cli yarn
npm install
npm run build
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install pyinstaller
python -m PyInstaller --clean --noconfirm  vims.spec
if [ -f "sages.db" ] ; then
    rm "sages.db"
fi
python init_tables.py > init_tables.log
python init.py > init.log
cp -r ../frontend/dist/spa dist/vims/dist
cp app.config.py dist/vims/
cp roles.config.py dist/vims/
cp roles.json dist/vims/
cp sages.db dist/vims
cd dist/vims
if [ -f ".env" ] ; then
    rm ".env"
fi
echo "FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")" >> .env
echo "JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" >> .env
echo "RUN_MODE=standalone" >> .env
source .env
