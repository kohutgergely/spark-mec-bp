from configs.nist_ionization_energy_adapter_config import IonizationEnergyAdapterConfig
from validators.nist_validators import NistBaseResponseValidator
import logging
import requests


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
                response_validation = NistBaseResponseValidator(response.text).validate()
                if response_validation["result"] is False:
                    raise SyntaxError(response_validation["error"])

            except Exception as error:
                logging.error(str(error))
                raise error

            return response.text
