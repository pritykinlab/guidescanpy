from guidescanpy import config


def test_config_string():
    assert isinstance(config.guidescan.bin, str)


def test_config_string_bool():
    assert config.celery.eager in (True, False)


def test_config_string_override():
    old_value = config.guidescan.bin
    with config({"guidescan.bin": "foo"}):
        assert config.guidescan.bin == "foo"
    assert config.guidescan.bin == old_value
