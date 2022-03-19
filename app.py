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


# spectrum_line_config = SpectrumLineAdapterConfig()
# spectrum_line_adapter = SpectrumLineAdapter(spectrum_line_config)
# print(spectrum_line_adapter.request_data(
#     spectrum="Fe I",
#     lower_wavelength=300,
#     upper_wavelength=500)
# )


# requested_spectrum = "Ar II"
# requested_temperature = 5
# ion_adapter_config = IonizationEnergyAdapterConfig()
# ionization_energy_adapter = IonizationEnergyAdapter(ion_adapter_config)
# ion_data = ionization_energy_adapter.request_data(spectrum=requested_spectrum)

# spectrum_level_config = SpectrumLevelAdapterConfig()
# spectrum_level_adapter = SpectrumLevelAdapter(spectrum_level_config)
# spectrum_level_data = spectrum_level_adapter.request_data(spectrum=requested_spectrum, temperature=requested_temperature)


# ionization_energy = helper_functions.get_ionization_energy(requested_spectrum, ion_data)
# partition_function = helper_functions.get_partition_function(spectrum_level_data)

# print(f"Spectrum={requested_spectrum}, IE={ionization_energy}, Z={partition_function}")


if __name__ == "__main__":
    set_logging()
    config = helper_functions.read_config_file("config.yaml")
    prepare_spectrum.main(config["prepare_spectrum"])
    gather_data.main(config["gather_data"])
    plasma_temperature.main(config["plasma_temperature"])