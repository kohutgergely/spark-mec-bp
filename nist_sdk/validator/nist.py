from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

error_string = "<html"

class ValidationError(Exception):
    pass

class NISTResponseValidator:
    base_error_message = "Error when querying NIST spectrum line database - "

    def validate(self, response: str) -> Optional[ValidationError]:
        if error_string in response:
            nist_error_message = self._get_error_from_response(response)
            return self._create_validation_error(message=self.base_error_message + nist_error_message)

        return None

    def _create_validation_error(self, message: str) -> Dict[str, Any]:
        return ValidationError(message)

    def _get_error_from_response(self, response: str) -> str:
        parsed_text = BeautifulSoup(response, 'html.parser')
        return parsed_text.body.font.string
