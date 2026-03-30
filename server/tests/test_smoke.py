def test_version_defined():
    from src.version import __version__

    assert isinstance(__version__, str)
    assert len(__version__) > 0