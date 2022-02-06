from nist_service.line_scraper_config import LineScraperConfig

from nist_service.line_scraper import LineScraper

config = LineScraperConfig(
    spectra="Fe II;Na;Mg",
    lower_wavelength=400,
    upper_wavelength=800
)
line_scraper = LineScraper(config)
line_scraper.request_lines()
line_scraper.to_csv()