import pytest
from nist.validators.response_error import ResponseErrorValidator, ValidationError


@pytest.fixture()
def valid_response(mocker):
    response = mocker.MagicMock()
    response.text = "valid response text without html tags"

    return response


@pytest.fixture()
def invalid_response(mocker):
    response = mocker.MagicMock()
    response.text = '''<html>
        <body bgcolor="white">
        <font color="red">Unrecognized token.</font>
        </body>
        </html>'''

    return response


def test_nist_response_validator_validate_method_returns_none_on_valid_response(valid_response):
    assert ResponseErrorValidator().validate(valid_response.text) is None


def test_nist_base_validator_validate_method_returns_validation_error_on_invalid_response(invalid_response):
    assert isinstance(ResponseErrorValidator().validate(
        invalid_response.text), ValidationError)
