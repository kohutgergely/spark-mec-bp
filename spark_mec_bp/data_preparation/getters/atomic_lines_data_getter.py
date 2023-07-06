import numpy as np
from spark_mec_bp.nist.fetchers import AtomicLinesFetcher
from spark_mec_bp.nist.parsers import AtomicLinesParser

TARGET_COLUMNS = ["obs_wl_air(nm)", "Aki(s^-1)", "g_k", "Ek(cm-1)"]
NOT_NA_FILTER_COLUMN = "Aki(s^-1)"


class AtomicLinesDataGetter:
    def __init__(
        self,
        atomic_lines_fetcher: AtomicLinesFetcher,
        atomic_lines_parser: AtomicLinesParser,
    ) -> None:
        self.atomic_lines_fetcher = atomic_lines_fetcher
        self.atomic_lines_parser = atomic_lines_parser

    def get_data(self, species_name: str, target_peaks: np.ndarray) -> np.ndarray:
        lower_wavelength, upper_wavelength = self._get_wavelength_range(target_peaks)
        atomic_lines_data = self._fetch_atomic_lines_data_from_nist(
            species_name, lower_wavelength, upper_wavelength
        )
        parsed_data = self._parse_data_into_dataframe(atomic_lines_data)
        filtered_data = self._filter_data(parsed_data)

        return self._find_rows_nearest_to_target_peaks(
            filtered_data.to_numpy().astype(float), target_peaks
        )

    def _get_wavelength_range(self, target_peaks: np.ndarray):
        lower_wavelength = int((np.floor(target_peaks / 100) * 100).min())
        upper_wavelength = int((np.ceil(target_peaks / 100) * 100).max())

        return lower_wavelength, upper_wavelength

    def _filter_data(self, parsed_data):
        column_filtered_data = parsed_data[TARGET_COLUMNS]
        colunm_and_row_filtered_data = column_filtered_data[
            column_filtered_data[NOT_NA_FILTER_COLUMN].notna()
        ]

        return colunm_and_row_filtered_data

    def _fetch_atomic_lines_data_from_nist(
        self, species_name, lower_wavelength, upper_wavelength
    ):
        return self.atomic_lines_fetcher.fetch(
            species_name, lower_wavelength, upper_wavelength
        )

    def _parse_data_into_dataframe(self, atomic_lines_data):
        return self.atomic_lines_parser.parse_atomic_lines(atomic_lines_data)

    def _find_rows_nearest_to_target_peaks(self, spectrum_data, target_peaks):
        indices = np.abs(spectrum_data[:, 0] - target_peaks[:, np.newaxis]).argmin(
            axis=1
        )

        return spectrum_data[indices]
