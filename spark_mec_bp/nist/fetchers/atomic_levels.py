from spark_mec_bp.nist.validators import ResponseErrorValidator
from dataclasses import dataclass
import requests


@dataclass
class AtomicLevelsData:
    data: str


class AtomicLevelsFetcher:
    url = "https://physics.nist.gov/cgi-bin/ASD/energy1.pl"
    de = 0
    units = 0
    output_format = 3
    display_output = 0
    page_size = 15
    multiplet_ordered = 0
    principal_configuration = "on"
    principal_term = "on"
    level = "on"
    uncertainty = 1
    j = "on"
    g = "on"
    lande_g = "on"
    leading_percentagies = "on"
    submit = "Retrieve Data"

    def __init__(self) -> None:
        self.validator = ResponseErrorValidator()

    def fetch(
            self,
            spectrum: str,
            temperature: float
    ) -> AtomicLevelsData:
        return self._request_data_from_nist(spectrum, temperature)

    def _request_data_from_nist(self, spectrum: str, temperature: float) -> AtomicLevelsData:
        with requests.get(
                url=self.url,
                params={
                    "spectrum": spectrum,
                    "temp": temperature,
                    "units": self.units,
                    "de": self.de,
                    "format": self.output_format,
                    "output": self.display_output,
                    "page_size": self.page_size,
                    "multiplet_ordered": self.multiplet_ordered,
                    "conf_out": self.principal_configuration,
                    "term_out": self.principal_term,
                    "level_out": self.level,
                    "unc_out": self.uncertainty,
                    "j_out": self.j,
                    "g_out": self.g,
                    "lande_out": self.lande_g,
                    "perc_out": self.leading_percentagies,
                    "submit": self.submit
                }
        ) as response:
            self._validate_response(response)
            return AtomicLevelsData(data=response.text)

    def _validate_response(self, response: requests.Response) -> None:
        response.raise_for_status()
        validation_error = self.validator.validate(response.text)
        if validation_error:
            raise validation_error
