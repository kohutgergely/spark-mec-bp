from spark_mec_bp.nist.validators import ResponseErrorValidator
from dataclasses import dataclass
import requests


@dataclass
class IonizationEnergyData:
    data: str


class IonizationEnergyFetcher:
    url = "https://physics.nist.gov/cgi-bin/ASD/ie.pl"
    units = 0
    output_format = 3
    order = 0
    atomic_number = "on"
    ion_charge = "on"
    element_name = "on"
    isoelectronic_sequence = "on"
    ground_state_electronic_shells = "on"
    ground_state_configuration = "on"
    ground_state_level = "on"
    ionized_configuration = "on"
    uncertainity = "on"
    spectrum_name_output = "on"
    ionization_energy_output = 0
    submit = "Retrieve Data"

    def __init__(self) -> None:
        self.validator = ResponseErrorValidator()

    def fetch(
        self,
        spectrum: str,
    ) -> IonizationEnergyData:
        with requests.get(
            url=self.url,
            params={
                "spectra": spectrum,
                "units": self.units,
                "format": self.output_format,
                "order": self.order,
                "at_num_out": self.atomic_number,
                "ion_charge_out": self.ion_charge,
                "el_name_out": self.element_name,
                "seq_out": self.isoelectronic_sequence,
                "shells_out": self.ground_state_electronic_shells,
                "conf_out": self.ground_state_configuration,
                "level_out": self.ground_state_level,
                "ion_conf_out": self.ionized_configuration,
                "unc_out": self.uncertainity,
                "sp_name_out": self.spectrum_name_output,
                "e_out": self.ionization_energy_output,
                "submit": self.submit,
            },
        ) as response:
            self._validate_response(response)
            return IonizationEnergyData(data=response.text)

    def _validate_response(self, response: requests.Response) -> None:
        response.raise_for_status()
        validation_error = self.validator.validate(response.text)
        if validation_error:
            raise validation_error
