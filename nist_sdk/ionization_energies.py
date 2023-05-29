import validator.nist_validators
import logging
import requests

class IonizationEnergyAdapterConfig:
    url = "https://physics.nist.gov/cgi-bin/ASD/ie.pl"
    units = 0
    output_format = 3
    order = 0
    spectrum_name_output = "on"
    ionization_energy_output = 0
    submit = "Retrieve Data"

class IonizationEnergyData:

    def __init__(self, data: str) -> None:
        self.data = data

    def __str__(self) -> str:
        return self.data


class IonizationEnergyAdapter:

    def __init__(self, config: IonizationEnergyAdapterConfig) -> None:
        self.config = config

    def request_data(
            self,
            spectrum: str,
    ):
        logging.info(
            f"Retrieving ionization energy from NIST database for the following query: {spectrum}")
        with requests.get(
                url=self.config.url,
                params={

                    "spectra": spectrum,
                    "units": self.config.units,
                    "format": self.config.output_format,
                    "order": self.config.order,
                    "sp_name_out": self.config.spectrum_name_output,
                    "e_out": self.config.ionization_energy_output,
                    "submit": self.config.submit
                }
        ) as response:
            try:
                response.raise_for_status()
                validator = validator.nist_validators.NistBaseResponseValidator(response.text)
                response_validation = validator.validate()
                if response_validation["result"] is False:
                    raise SyntaxError(response_validation["error"])

            except Exception as error:
                logging.error(str(error))
                raise error

            return IonizationEnergyData(response.text)
