from event_sonification_workbench import __version__


def test_package_imports() -> None:
    """Confirm that the installed package can be imported."""
    assert __version__ == "0.1.0"
