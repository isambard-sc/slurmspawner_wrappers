"""
Functions that wrap Slurm commands to be executed by JupyterHub via batchspawner.SlurmSpawner.

The wrapper functions are to be used as console script entry points to the package, i.e. they should
not accept any arguments and return an integer exit code.
"""

import os
import subprocess
import sys


def run_sbatch() -> int:
    print("ERROR: function run_sbatch not implemented", file=sys.stderr)
    return 1


def run_squeue() -> int:
    print("ERROR: function run_squeue not implemented", file=sys.stderr)
    return 1


def run_scancel() -> int:
    """
    Run `scancel` as a subprocess with job ID provided as environment variable

    `scancel` is invoked using the default command form specified in 
    batchspawner.SlurmSpawner.batch_cancel_cmd (a template):

        scancel {job_id}

    In this case {job_id} is specified via environment variable SLURMSPAWNER_JOB_ID.

    :raises SystemExit: if SLURMSPAWNER_JOB_ID environment variable is not present in the current
        process environment
    :return: the integer return code of the `scancel` subprocess
    """
    try:
        jobid = os.environ["SLURMSPAWNER_JOB_ID"]
    except KeyError as exc:
        raise SystemExit("ERROR: environment variable SLURMSPAWNER_JOB_ID must be set") from exc

    # Run default `scancel` command used by SlurmSpawner "scancel {job_id}", using
    # environment variable `SLURMSPAWNER_JOB_ID` to specify job_id
    # TODO: Use absolute path to scancel
    completed_process = subprocess.run(
        args=["scancel", jobid], capture_output=False, shell=False, input=None, env=None, check=False
    )

    return completed_process.returncode
