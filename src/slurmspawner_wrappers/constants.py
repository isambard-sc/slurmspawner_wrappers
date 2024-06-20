"""
Package-wide constants
"""

from pathlib import Path

# For security and reliability the wrapper scripts use absolute paths to
# Slurm commands, rather than relying on locating executables from PATH
SBATCH_PATH = Path("/usr/bin/sbatch")
SQUEUE_PATH = Path("/usr/bin/squeue")
SCANCEL_PATH = Path("/usr/bin/scancel")
