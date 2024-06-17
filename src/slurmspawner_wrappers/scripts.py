"""
Functions that wrap Slurm commands to be executed by JupyterHub via batchspawner.SlurmSpawner.

The wrapper functions are to be used as console script entry points to the package, i.e. they should
not accept any arguments and return an integer exit code.
"""

import sys


def run_sbatch() -> int:
    print("ERROR: function run_sbatch not implemented", file=sys.stderr)
    return 1


def run_squeue() -> int:
    print("ERROR: function run_squeue not implemented", file=sys.stderr)
    return 1


def run_scancel() -> int:
    print("ERROR: function run_squeue not implemented", file=sys.stderr)
    return 1
