import pytest
import validators.nist_validators

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

def test_nist_base_validator_has_the_correct_instance_attributes(valid_response):
    validator = validators.nist_validators.NistBaseResponseValidator(valid_response.text)
    assert validator.response_text == valid_response.text
    assert validator.base_error_message == "Error when querying NIST spectrum line database - "

def test_nist_base_validator_validate_method_returns_truthy_validation_result_on_valid_response(valid_response):

    expected_validation_result = {
        "result": True,
        "error": None
    }
    validator = validators.nist_validators.NistBaseResponseValidator(valid_response.text)
    actual_validation_result = validator.validate()

    assert expected_validation_result == actual_validation_result

def test_nist_base_validator_validate_method_returns_falsy_validation_result_on_valid_response(invalid_response):

    expected_validation_result = {
        "result": False,
        "error": "Error when querying NIST spectrum line database - Unrecognized token."
    }
    validator = validators.nist_validators.NistBaseResponseValidator(invalid_response.text)
    actual_validation_result = validator.validate()

    assert expected_validation_result == actual_validation_result