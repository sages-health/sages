SAGES
====

SAGES

# Development

### Mac
To initialize a development environment, run:

```bash
make
```

This will create a virtual environment in the current directory and initialize pre-commit. Activate the virtual environment by running:

```bash
source .venv/bin/activate
```

Once the virtual environment is installed, install dependencies (or update if the [setup.cfg](setup.cfg) is changed), by running:

```bash
make
# or
make update
```

### Windows

To initialize a development environment run:
```bash
python -m venv --prompt vims .venv
```

This will create a virtual environment in the current directory and initialize pre-commit. Before running the application, activate the virtual environment by running:

```bash
.venv/Scripts/activate
```

Once the virtual environment is installed, install dependencies (or update if the [setup.cfg](setup.cfg) is changed), by running each of the following commands:

```bash
.venv/Scripts/pip install -U pip
.venv/Scripts/pip install -U pip setuptools
.venv/Scripts/pip install -U pip wheel build
.venv/Scripts/pip install -U pip install --default-time=1000 black==21.10b0 isort==5.10.1 flake8==4.0.1 pre-commit
.venv/Scripts/pre-commit install
.venv/Scripts/pip install -e .
```

### Git - First time setup

#### Windows 
Make sure you're running the latest git on windows (currently 2.37.1), and then set the http.sslBackend config setting to schannel:
```
git config --global http.sslBackend schannel
```
This reconfigures git to use the Windows certificate store, which on every APL computer will already have the APL Root Certificate in the list (along with every other standard certificate used outside of APL). If this still isn't working, you can easily add the APL Root Certificate to the windows store following the instructions [here](https://support.globalsign.com/ssl/ssl-certificates-installation/import-and-export-certificate-microsoft-windows) (download it as recommended and then follow the instructions).

### Git - Workflow

Make changes and then switch to a new branch with the ticket number by running:
```bash
git checkout -b [ticket title]
```

Then commit changes by running:
```bash
git commit -m "message"
```

Push changes from local to remote by running:
```bash
git push origin [ticket title]
```
## Cleaning

To cleanup the virtual environment / start from scratch run:

```bash
make clean
```

# Running

All python commands **MUST** be run from within the virtual environment.

A [docker-compose.yml](docker-compose.yml) file is provided in the project root that launches the backend + nginx (which has the frontend built in).

```bash
docker compose up
```

The application needs to be seeded once by running the command below. This will remove all current data from the database.

```bash
python init.py
```


The main application can be run with:

```bash
python -m vims.app
```

## Tools

A password hashing tool is provided for generating hashed passwords for adding users to the database:

```bash
python src/vims/tools/fernet.py encrypt $Settings.ENCRYPTION_KEYS $YOUR_PASSWORD
```

## Building SAGES using Pyinstaller

Run the `build_linux.sh` script in order to install dependencies, build the frontend JavaScript distribution, copy it to the Pyinstaller folder, and generate the executable. Be sure to include a .env file in 
