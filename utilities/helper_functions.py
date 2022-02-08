from adapters.nist_spectrum_level_adapter import SpectrumLevelAdapter
from configs.nist_spectrum_level_adapter_config import SpectrumLevelConfig
import logging

def get_partition_function(
        spectrum: str,
        temperature: float
):
    spectrum_level_config = SpectrumLevelConfig()
    spectrum_level_adapter = SpectrumLevelAdapter(spectrum_level_config)
    level_data = spectrum_level_adapter.request_data(spectrum=spectrum, temperature=temperature)
    partition_function_raw_line = level_data.split("\n")[-2]
    partition_function_value = float(partition_function_raw_line.split()[-1])

    return partition_function_value