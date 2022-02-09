import logging
import os
from datetime import datetime
from configs.nist_spectrum_level_adapter_config import SpectrumLevelAdapterConfig
from configs.nist_ionization_energy_adapter_config import IonizationEnergyAdapterConfig
from configs.nist_spectrum_line_adapter_config import SpectrumLineAdapterConfig
from adapters.nist_spectrum_level_adapter import SpectrumLevelAdapter
from adapters.nist_spectrum_line_adapter import SpectrumLineAdapter
from adapters.nist_ionization_energy_adapter import IonizationEnergyAdapter

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
file_handler = logging.FileHandler("{:%Y-%m-%d-%H-%M}.log".format(datetime.now()))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
console = logging.StreamHandler()
console.setFormatter(formatter)
logger.addHandler(console)


config = SpectrumLineAdapterConfig()
line_scraper = SpectrumLineAdapter(config)
print(line_scraper.request_data(
    spectrum="Fe I",
    lower_wavelength=300,
    upper_wavelength=500)
)

config = SpectrumLevelAdapterConfig()
line_scraper = SpectrumLevelAdapter(config)
print(line_scraper.request_data(
    spectrum="Fe I",
    temperature=2))

config = IonizationEnergyAdapterConfig()
line_scraper = IonizationEnergyAdapter(config)
print(line_scraper.request_data(spectrum="Ar II"))



