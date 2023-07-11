from guidescanpy import config


def test_config_string():
    assert config.pytest.astring == "foo"


def test_config_string_bool():
    assert config.pytest.abool is True


def test_config_nested_int():
    assert config.pytest.nested.aint == 42


def test_config_string_override():
    old_value = config.pytest.astring
    with config({"pytest.astring": "bar"}):
        assert config.pytest.astring == "bar"
    assert config.pytest.astring == old_value
