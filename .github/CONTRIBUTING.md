# Contributing to the project

If you want to contribute to the project, please follow the steps below:

Install the development requirements:

```bash
uv venv
source .venv/bin/activate
uv sync --all-extras --dev
```

Install and run the pre-commit hooks:

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

To add a new dependency to a group like a lint group to segment dependencies, run this:

```bash
uv add --group lint ruff
```

To run the code from main.py, run it via uv environment.

```bash
uv run main.py data/raw
```

To exit out of the virtual environment (venv), run the following:

```bash
deactivate
```

To figure out which dependency may be outdated, find the dependencies via:

```bash
uv pip list --outdated
```

To create a new dependency lock file manually (optional as it should happen automatically on uv add):

```bash
uv lock
```

To upgrade dependencies, run:

```bash
uv lock --upgrade
```
