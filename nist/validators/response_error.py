from bs4 import BeautifulSoup
from typing import Optional


class ValidationError(Exception):
    pass


class ResponseErrorValidator:
    base_error_message = "Error when querying NIST spectrum line database - "
    error_string = "<html"

    def validate(self, response: str) -> Optional[ValidationError]:
        if self.error_string in response:
            nist_error_message = self._get_error_message_from_response_if_exists(
                response)
            return self._create_validation_error(message=self.base_error_message + nist_error_message)

        return None

    def _create_validation_error(self, message: str) -> ValidationError:
        return ValidationError(message)

    def _get_error_message_from_response_if_exists(self, response: str) -> str:
        error_message = BeautifulSoup(response, 'html.parser').body.font.string
        return error_message if error_message else ""
