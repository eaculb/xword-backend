## Setup

1. Install pyenv and pyenv-virtualenv

- [pyenv](https://github.com/pyenv/pyenv)
- [virtualenv](https://github.com/pyenv/pyenv-virtualenv) - note that the pyenv installer installs this for you

2. Create a virtual env and record it in the repo's `python-version`

```bash
pyenv virtualenv 3.8.0 eaculb-xword-backend
echo eaculb-xword-backend > .python-version
```

3. Compile and install requirements

```bash
pip-compile requirements-dev.in
pip-compile requirements.in
pip install -r requirements-dev.txt
```

## Testing

1. Install prerequisites for PostgreSQL

```
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
xz-utils tk-dev libffi-dev liblzma-dev python-openssl git
```

3. Install PostgreSQL:

note: if running Ubuntu 16.04 you will need to replace `postgresql-server-dev-12` with `postgresql-server-dev-9.5`

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib libpq-dev postgresql-server-dev-12
```

2. Create a db role with your username:

```bash
  sudo -u postgres createuser --interactive -P
```

3. At some point you will need to create a db password; record this or export in your `~/.bashrc`

4. Create a test db and export its url; I recommend creating a helper bash function to reset the test db and export its name

```bash
createdb xword_test
export DATABASE_URL=postgresql://localhost/xword_test
```