from configs.nist_spectrum_level_adapter_config import SpectrumLevelAdapterConfig
from validators.nist_validators import NistBaseResponseValidator
import logging
import requests


class SpectrumLevelAdapter:

    def __init__(self, config: SpectrumLevelAdapterConfig) -> None:
        self.config = config

    def request_data(
            self,
            spectrum: str,
            temperature: float
    ):
        logging.info(
            f"Retrieving spectrum level information from NIST database for the following query: {spectrum}")
        with requests.get(
            url=self.config.url,
            params={
                "spectrum": spectrum,
                "temp": temperature,
                "units": self.config.units,
                "de": self.config.de,
                "format": self.config.output_format,
                "output": self.config.display_output,
                "page_size": self.config.page_size,
                "multiplet_ordered": self.config.multiplet_ordered,
                "conf_out": self.config.level_information_principal_configuration,
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