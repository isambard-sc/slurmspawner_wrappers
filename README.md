# slurmspawner_wrappers

Wrapper scripts for Slurm commands run by JupyterHub `SlurmSpawner`

## Install

The package needs to be installed in order for the wrapper scripts to be available from the command line.
This is because the scripts are implemented as [console-script-type entry points][entry-points-setuptools-docs] for the Python project.

[entry-points-setuptools-docs]: https://setuptools.pypa.io/en/latest/userguide/entry_point.html

It is recommended to first create a virtual environment

```shell
python -m venv --upgrade-deps /path/to/slurmspawner-venv
```

then install the package into the virtual environment.

### Install directly from the GitHub repository

```shell
/path/to/slurmspawner-venv/bin/python -m pip install "slurmspawner_wrappers @ git+https://github.com/isambard-sc/slurmspawner_wrappers.git"
```

### Install from local clone of repository

Clone the repository

```shell
git clone https://github.com/isambard-sc/slurmspawner_wrappers.git
```

Then install into the virtual environment using the path to the cloned repository

```shell
/path/to/slurmspawner-venv/bin/python -m pip install /path/to/slurmspawner_wrappers
```

An [editable install][editable-installs-pip-docs] is useful when developing. This adds files in the source directory to the Python import path, so edits to the source code are reflected in the installed package.

[editable-installs-pip-docs]: https://pip.pypa.io/en/stable/topics/local-project-installs/#editable-installs

```shell
/path/to/slurmspawner-venv/bin/python -m pip install -e /path/to/slurmspawner_wrappers
```

> [!NOTE]
> Edits to project metadata will still require reinstallation of the package.

### Install from built distribution

Clone the repository

```shell
git clone https://github.com/isambard-sc/slurmspawner_wrappers.git
```

Build the distribution (requires [`build`][pypa-build-docs])

[pypa-build-docs]: https://build.pypa.io

```shell
python -m build /path/to/slurmspawner_wrappers
```

Install from the sdist or wheel placed in the `dist/` directory

```shell
/path/to/slurmspawner-venv/bin/python -m pip install /path/to/slurmspawner_wrappers/dist/slurmspawner_wrappers-{version}.tar.gz
```

```shell
/path/to/slurmspawner-venv/bin/python -m pip install /path/to/slurmspawner_wrappers/dist/slurmspawner_wrappers-{version}-py3-none-any.whl
```

### Install with development dependencies

Use the `[dev]` optional dependency to install development tools (linting, formatting, testing etc.) alongside the `slurmspawner_wrappers` package.

This is useful in combination with an editable install from a local copy of the repository. The local copy can then be worked with using the development tools.

```shell
/path/to/slurmspawner-venv/bin/python -m pip install -e '/path/to/slurmspawner_wrappers[dev]'
```

## Usage

The wrapper scripts `slurmspawner_sbatch`, `slurmspawner_squeue`, and `slurmspawner_scancel` are intended to be used as replacements for the `sbatch`, `squeue`, and `scancel` commands used by [batchspawner][batchspawner-github]'s `SlurmSpawner`.
To allow for secure `sudo` policy configuration, they receive parameters (e.g. job ID) via environment variables or stdin.

The environment variables are never expanded in a shell context and are interpreted as strings in the Python scripts, avoiding the risk of [shell injection][shell-injection-wikipedia].

[shell-injection-wikipedia]: https://en.wikipedia.org/wiki/Code_injection

### Command-line

The scripts are intended to be run by JupyterHub (via `SlurmSpawner`), but can also be run directly on the command line.

Submit job script `submit.sh`

```shell
slurmspawner_sbatch < submit.sh
```

Query job ID 1234

```shell
SLURMSPAWNER_JOB_ID=1234 slurmspawner_squeue
```

Cancel job ID 1234

```shell
SLURMSPAWNER_JOB_ID=1234 slurmspawner_scancel
```

### JupyterHub configuration

The `batch_submit_cmd`, `batch_query_cmd` and `batch_cancel_cmd` configuration attributes for the `SlurmSpawner` class should be modified in  JupyterHub configuration file to use the wrapper scripts in place of the `sbatch`, `squeue`, and `scancel` commands themselves.

[batchspawner-github]: https://github.com/jupyterhub/batchspawner/

**TODO**: How to set configuration attributes
