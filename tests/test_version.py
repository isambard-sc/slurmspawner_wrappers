import re

from slurmspawner_wrappers import __version__, __version_tuple__

def test_version() -> None:
    """
    Check version dunder module variables are present and consistent

    .. note:: Only checks the major.minor.patch component of the version  
    """
    # Check that version number starts with major.minor.patch number (and optional v prefix) 
    match = re.fullmatch(r"^v?(?P<major>\d+)\.(?P<minor>\d)+\.(?P<patch>\d+).*$", __version__)

    assert match, "__version__ should start with a valid dotted version number"
    
    assert int(match.group("major")) == __version_tuple__[0]
    assert int(match.group("minor")) == __version_tuple__[1]
    assert int(match.group("patch")) == __version_tuple__[2]
