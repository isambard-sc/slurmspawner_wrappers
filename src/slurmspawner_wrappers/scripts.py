"""
Functions that wrap Slurm commands to be executed by JupyterHub via batchspawner.SlurmSpawner.

The wrapper functions are to be used as console script entry points to the package, i.e. they should
not accept any arguments and return an integer exit code.
"""

import os
import subprocess
import sys

from .constants import SBATCH_PATH, SCANCEL_PATH, SQUEUE_PATH


def run_sbatch() -> int:
    """
    Run `sbatch` as a subprocess with batch script provided through stdin

    `sbatch` is invoked using the default command form specified in
    batchspawner.SlurmSpawner.batch_submit_cmd (a template):

        sbatch --parsable

    When submitting a batch script via batchspawner.BatchSpawner.submit_batch_script(), the
    batch script (from batchspawner.SlurmSpawner.batch_script) is passed to stdin of sbatch
    (see batchspawner.BatchSpawner.run_command() for implementation)

    :return: the integer return code of the `sbatch` subprocess
    """
    # Run default `sbatch` command used by SlurmSpawner, passing stdin of Python process
    # to subprocess
    completed_process = subprocess.run(
        args=[str(SBATCH_PATH), "--parsable"],
        stdin=sys.stdin,
        capture_output=False,
        shell=False,
        input=None,
        env=None,
        check=False,
    )

    return completed_process.returncode


def run_squeue() -> int:
    """
    Run `squeue` as a subprocess with job ID provided as environment variable

    `squeue` is invoked using the default command form specified in
    batchspawner.SlurmSpawner.batch_query_cmd (a template):

        squeue -h -j {job_id} -o '%T %B'

    In this case {job_id} is specified via environment variable SLURMSPAWNER_JOB_ID.

    :raises SystemExit: if SLURMSPAWNER_JOB_ID environment variable is not present in the current
        process environment
    :return: the integer return code of the `squeue` subprocess
    """
    try:
        job_id = os.environ["SLURMSPAWNER_JOB_ID"]
    except KeyError as exc:
        raise SystemExit("ERROR: environment variable SLURMSPAWNER_JOB_ID must be set") from exc

    # Run default `squeue` command used by SlurmSpawner, using environment
    # variable `SLURMSPAWNER_JOB_ID` to specify job_id
    completed_process = subprocess.run(
        args=[str(SQUEUE_PATH), "-h", "-j", job_id, "-o", "%T %B"],
        capture_output=False,
        shell=False,
        input=None,
        env=None,
        check=False,
    )

    return completed_process.returncode


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
        job_id = os.environ["SLURMSPAWNER_JOB_ID"]
    except KeyError as exc:
        raise SystemExit("ERROR: environment variable SLURMSPAWNER_JOB_ID must be set") from exc

    # Run default `scancel` command used by SlurmSpawner environment variable
    # `SLURMSPAWNER_JOB_ID` to specify job_id
    completed_process = subprocess.run(
        args=[str(SCANCEL_PATH), job_id], capture_output=False, shell=False, input=None, env=None, check=False
    )

    return completed_process.returncode
