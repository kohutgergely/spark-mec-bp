import logging
from datetime import datetime
from configs.nist_spectrum_level_adapter_config import SpectrumLevelAdapterConfig
from configs.nist_ionization_energy_adapter_config import IonizationEnergyAdapterConfig
from configs.nist_spectrum_line_adapter_config import SpectrumLineAdapterConfig
from adapters.nist_spectrum_level_adapter import SpectrumLevelAdapter
from adapters.nist_spectrum_line_adapter import SpectrumLineAdapter
from adapters.nist_ionization_energy_adapter import IonizationEnergyAdapter
from lib import helper_functions
import gather_data, plasma_temperature, prepare_spectrum

def set_logging():
    logging.captureWarnings(True) 
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    file_handler = logging.FileHandler("{:%Y-%m-%d-%H-%M}.log".format(datetime.now()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

if __name__ == "__main__":
    set_logging()
    config = helper_functions.read_config_file("config.yaml")
    prepare_spectrum.main(config["prepare_spectrum"])
    gather_data.main(config["gather_data"])
    plasma_temperature.main(config["plasma_temperature"])