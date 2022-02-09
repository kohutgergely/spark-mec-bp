from bs4 import BeautifulSoup


class NistBaseResponseValidator:

    def __init__(self, response_text: str):
        self.response_text = response_text
        self.base_error_message = f"Error when querying NIST spectrum line database - "

    def validate(self):
        if "<!DOCTYPE html" in self.response_text:
            nist_error_message = self._get_error_from_response()
            return {
                "result": False,
                "error": self.base_error_message + nist_error_message
            }
        return {
            "result": True,
            "error": None
        }

    def _get_error_from_response(self):
        parsed_text = BeautifulSoup(self.response_text, 'html.parser')
        return parsed_text.body.font.string
