import io
import re
import subprocess
import sys
from collections.abc import Callable, Generator
from pathlib import Path
from shutil import which

import pytest

from slurmspawner_wrappers.scripts import run_sbatch, run_scancel, run_squeue

sbatch_cmd_present = pytest.mark.skipif(which("sbatch") is None, reason="`sbatch` command required")
squeue_cmd_present = pytest.mark.skipif(which("squeue") is None, reason="`squeue` command required")
scancel_cmd_present = pytest.mark.skipif(which("scancel") is None, reason="`scancel` command required")


@pytest.mark.parametrize(
    "test_fn",
    [
        pytest.param(run_scancel, id="run_scancel"),
        pytest.param(run_squeue, id="run_squeue"),
    ],
)
def test_run_missing_env_var(test_fn: Callable[[], int], monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Check `test_fn` raises a SystemExit exception when expected environment variable is missing
    """

    monkeypatch.delenv("SLURMSPAWNER_JOB_ID", raising=False)

    with pytest.raises(SystemExit):
        _ = test_fn()


@pytest.fixture(scope="function", params=[pytest.param(0, id="returncode=0"), pytest.param(1, id="returncode=1")])
def patched_subprocess_run(request: pytest.FixtureRequest, mocker) -> Callable:
    """
    Create a mocked subprocess.run() for testing

    The return value of the mocked function is set to a subprocess.CompletedProcess instance with
    dummy args attribute and returncode from fixture parameters
    """

    return mocker.patch(
        "subprocess.run",
        autospec=True,
        return_value=subprocess.CompletedProcess(args=["dummy", "value"], returncode=request.param),
    )


def test_run_scancel(monkeypatch: pytest.MonkeyPatch, patched_subprocess_run: Callable) -> None:
    """
    Check run_scancel() calls subprocess.run() with expected arguments and returns subprocess returncode
    """

    job_id = "1234"
    monkeypatch.setenv("SLURMSPAWNER_JOB_ID", job_id)

    returncode = run_scancel()

    assert (
        returncode == patched_subprocess_run.return_value.returncode
    ), "return code should match value set for subprocess.run()"
    patched_subprocess_run.assert_called_once()
    assert patched_subprocess_run.call_args.kwargs["args"] == [
        "scancel",
        job_id,
    ], "subprocess.run() should be called with expected 'args' kwarg"


def test_run_squeue(monkeypatch: pytest.MonkeyPatch, patched_subprocess_run: Callable) -> None:
    """
    Check run_squeue() calls subprocess.run() with expected arguments and returns subprocess returncode
    """

    job_id = "1234"
    monkeypatch.setenv("SLURMSPAWNER_JOB_ID", job_id)

    returncode = run_squeue()

    assert (
        returncode == patched_subprocess_run.return_value.returncode
    ), "return code should match value set for subprocess.run()"
    patched_subprocess_run.assert_called_once()
    assert patched_subprocess_run.call_args.kwargs["args"] == [
        "squeue",
        "-h",
        "-j",
        job_id,
        "-o",
        "%T %B",
    ], "subprocess.run() should be called with expected 'args' kwarg"


def test_run_sbatch(patched_subprocess_run: Callable) -> None:
    """
    Check run_batch() calls subprocess.run() with expected arguments and returns subprocess returncode
    """

    returncode = run_sbatch()

    assert (
        returncode == patched_subprocess_run.return_value.returncode
    ), "return code should match value set for subprocess.run()"
    patched_subprocess_run.assert_called_once()
    assert patched_subprocess_run.call_args.kwargs["args"] == [
        "sbatch",
        "--parsable",
    ], "subprocess.run() should be called with expected 'args' kwarg"
    assert (
        patched_subprocess_run.call_args.kwargs["stdin"] is sys.stdin
    ), "subprocess.run() should be called with expected 'stdin' kwarg"


@pytest.fixture
def mock_batch_script_stdin(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> io.TextIOWrapper:
    """
    Replaces sys.stdin with a file object corresponding to a temporary file containing a simple Slurm batch script
    """

    script_path = tmp_path / "script.sh"

    # Simple job submission script that requests 1 task on 1 node for 2 minutes (and 100M memory)
    # This waits for 60s to allow time for job to be queried and cancelled. Output is redirected
    # to /dev/null (no output file written)
    script_path.write_text(
        "\n".join(
            [
                "#!/bin/bash",
                '#SBATCH --job-name="pytest-slurmspawner_wrappers"',
                "#SBATCH --nodes=1",
                "#SBATCH --ntasks-per-node=1",
                "#SBATCH --time=2",
                "#SBATCH --mem=100M",
                "#SBATCH --output=/dev/null",
                "",
                "sleep 60",
                "",
            ]
        )
    )

    with open(script_path, "r") as mock_stdin:
        monkeypatch.setattr("sys.stdin", mock_stdin)
        yield mock_stdin


# Possible long-form ``squeue`` state codes, from https://slurm.schedmd.com/squeue.html#SECTION_JOB-STATE-CODES
SQUEUE_STATES = [
    "BOOT_FAIL",
    "CANCELLED",
    "COMPLETED",
    "CONFIGURING",
    "COMPLETING",
    "DEADLINE",
    "FAILED",
    "NODE_FAIL",
    "OUT_OF_MEMORY",
    "PENDING",
    "PREEMPTED",
    "RUNNING",
    "RESV_DEL_HOLD",
    "REQUEUE_FED",
    "REQUEUE_HOLD",
    "REQUEUED",
    "RESIZING",
    "REVOKED",
    "SIGNALING",
    "SPECIAL_EXIT",
    "STAGE_OUT",
    "STOPPED",
    "SUSPENDED",
    "TIMEOUT",
]


@sbatch_cmd_present
@squeue_cmd_present
@scancel_cmd_present
def test_integration(
    mock_batch_script_stdin: Generator[io.TextIOWrapper, None, None],
    capfd: Generator[pytest.CaptureFixture[str], None, None],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Integration test that submits, queries, and cancels a test job

    The run_sbatch(), run_squeue(), and run_scancel() functions are used manage the job
    """

    # SUBMIT JOB
    # Batch script to submit provided via mocked sys.stdin (mock_batch_script_stdin)
    returncode = run_sbatch()

    # Job ID should be returned in stdout
    # Split on semicolon since sbatch --parsable may also output a cluster name
    # after job id, separated by ;
    job_id = capfd.readouterr().out.rstrip().split(";")[0]

    # Set SLURMSPAWNER_JOB_ID environment variable used by run_squeue() and
    # run_scancel()
    monkeypatch.setenv("SLURMSPAWNER_JOB_ID", job_id)

    # QUERY JOB
    returncode = run_squeue()

    assert returncode == 0, "expect return code 0 from run_squeue()"

    squeue_out = capfd.readouterr().out.rstrip()

    match = re.fullmatch(r"^(?P<job_state>[A-Z_]+) (?P<batch_host>.*)$", squeue_out)

    assert match, "squeue output should match regular expression"
    assert (
        match.group("job_state") in SQUEUE_STATES
    ), "job state in squeue output should match one of the possible squeue job state codes"

    # CANCEL JOB
    returncode = run_scancel()

    # NOTE: This does not check that job has been ended, only that scancel returned a non-zero exit code. scancel will
    #    return a non-zero error code even when given job ids for jobs that have already been cancelled!
    # TODO: Explicitly check the job has been cancelled/ended
    assert returncode == 0, "expect return code 0 from run_scancel()"
