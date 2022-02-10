from bs4 import BeautifulSoup


class NistBaseResponseValidator:

    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.base_error_message = "Error when querying NIST spectrum line database - "

    def validate(self):
        if "<html" in self.response_text:
            nist_error_message = self._get_error_from_response()
            final_error_message = self.base_error_message + nist_error_message
            return self._create_validation_result(result=False, error=final_error_message)

        return self._create_validation_result(result=True)

    def _create_validation_result(self, result: object, error: object = None) -> object:
        return {
            "result": result,
            "error": error
        }

    def _get_error_from_response(self) -> str:
        parsed_text = BeautifulSoup(self.response_text, 'html.parser')
        return parsed_text.body.font.string
