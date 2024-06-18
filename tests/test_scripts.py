import subprocess
from collections.abc import Callable

import pytest

from slurmspawner_wrappers.scripts import run_scancel, run_squeue


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
