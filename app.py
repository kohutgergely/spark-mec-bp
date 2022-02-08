from configs.nist_spectrum_level_adapter_config import SpectrumLevelConfig
from adapters.nist_spectrum_level_adapter import SpectrumLevelAdapter
from utilities import helper_functions
# config = LineScraperConfig()
# line_scraper = LineScraper(config)
# print(line_scraper.request_lines(
#     spectrum="Fe II;Na;Mg",
#     lower_wavelength=400,
#     upper_wavelength=800)
# )


print(helper_functions.get_partition_function(
    spectrum="Ar II",
    temperature=5)
)

