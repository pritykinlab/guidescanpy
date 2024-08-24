import os
from os.path import abspath, dirname
from guidescanpy import config


def test_config_string():
    assert config.pytest.astring == "foo"


def test_config_bool_true():
    assert config.pytest.atrue is True


def test_config_bool_false():
    assert config.pytest.afalse is False


def test_config_nested_int():
    assert config.pytest.nested.aint == 42


def test_config_special():
    assert config.pytest.aspecial == f"foo{abspath(dirname(config.file_path))}/bar"


# Configuration can be overridden by environment variables
# of the form GUIDESCAN_<section>_<subsection>_...<key>
# When accessed, they are automatically typecast to the value
# that would have been returned from the yaml file
def test_config_string_override():
    old_envvar = os.environ.get("GUIDESCAN_PYTEST_ASTRING")
    os.environ["GUIDESCAN_PYTEST_ASTRING"] = "bar"
    assert config.pytest.astring == "bar"
    if old_envvar is not None:
        os.environ["GUIDESCAN_PYTEST_ASTRING"] = old_envvar
    else:
        del os.environ["GUIDESCAN_PYTEST_ASTRING"]
    assert config.pytest.astring == "foo"


def test_config_int_override():
    old_envvar = os.environ.get("GUIDESCAN_PYTEST_NESTED_AINT")
    os.environ["GUIDESCAN_PYTEST_NESTED_AINT"] = "84"
    assert config.pytest.nested.aint == 84
    if old_envvar is not None:
        os.environ["GUIDESCAN_PYTEST_NESTED_AINT"] = old_envvar
    else:
        del os.environ["GUIDESCAN_PYTEST_NESTED_AINT"]
    assert config.pytest.nested.aint == 42


def test_config_bool_override():
    old_envvar = os.environ.get("GUIDESCAN_PYTEST_ATRUE")
    # Note: correct way to override a boolean to False!
    os.environ["GUIDESCAN_PYTEST_ATRUE"] = "FALSE"
    assert config.pytest.atrue is False
    if old_envvar is not None:
        os.environ["GUIDESCAN_PYTEST_ATRUE"] = old_envvar
    else:
        del os.environ["GUIDESCAN_PYTEST_ATRUE"]
    assert config.pytest.atrue is True


def test_config_envvar():
    # Config variables can be enclosed in {} to denote that the value
    # should be obtained from an environment variables
    old_envvar = os.environ.get("GUIDESCAN_PYTEST_ENV_VAR")
    os.environ["GUIDESCAN_PYTEST_ENV_VAR"] = "baz"
    assert config.pytest.adynamic == "baz"
    if old_envvar is not None:
        os.environ["GUIDESCAN_PYTEST_ENV_VAR"] = old_envvar
        assert config.pytest.adynamic == old_envvar
    else:
        del os.environ["GUIDESCAN_PYTEST_ENV_VAR"]
        assert config.pytest.adynamic == "{GUIDESCAN_PYTEST_ENV_VAR}"


def test_config_json():
    # A `json` attribute is available on the Config object
    # This is for backwards compatibility with a previous implementation
    # and is a dict representation of the configuration
    json = config.json
    assert json["pytest"]["nested"]["aint"] == 42
