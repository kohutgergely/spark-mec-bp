import numpy as np
from application import Application, ApplicationResult, ApplicationConfig
from application.logger import Logger
from application.plotting import Plotter
from application.lib import LinePairChecker


def log_results(line_pair_checker: LinePairChecker, result: ApplicationResult):
    AuI_linepair_check = line_pair_checker.check_line_pairs(
        result.first_species_atomic_lines,
        result.first_species_integrals,
        result.temperature,
    )
    AgI_linepair_check = line_pair_checker.check_line_pairs(
        result.second_species_atomic_lines,
        result.second_species_integrals,
        result.temperature,
    )

    logger.info(
        f"The number concentration ratio for {config.first_species_atom_name}-{config.second_species_atom_name}: {result.total_concentration:8.5f}"
    )
    logger.info(f"The temperature is: {result.temperature:6.3f} K")
    logger.info(
        f"{config.first_species_atom_name} linepair deviations: {AuI_linepair_check}"
    )
    logger.info(
        f"{config.second_species_atom_name} linepair deviations: {AgI_linepair_check}"
    )


def plot_figures(plotter: Plotter, result: ApplicationResult):
    plotter.plot_original_spectrum(
        spectrum=result.original_spectrum,
        spectrum_correction_data=result.spectrum_correction_data,
    )

    plotter.plot_saha_boltzmann_line_pairs(
        intensity_ratios_data=result.intensity_ratio_data
    )

    plotter.plot_baseline_corrected_spectrum_with_the_major_peaks(
        spectrum_correction_data=result.spectrum_correction_data,
        peak_indices=result.peak_indices,
        wlen=config.prominence_window_length,
        xlim=[400, 410],
        ylim=[0, 200],
    )


if __name__ == "__main__":
    logger = Logger().new()
    plotter = Plotter()
    line_pair_checker = LinePairChecker()
    config = ApplicationConfig(
        spectrum_path="AuAg-Cu-Ar-2.0mm-100Hz-2s_gate500ns_g100_s500ns_N100_3.2mm.asc",
        first_species_target_peaks=np.array([312.278, 406.507, 479.26]),
        first_species_atom_name="Au I",
        first_species_ion_name="Au II",
        second_species_target_peaks=np.array([338.29, 520.9078, 546.54]),
        second_species_atom_name="Ag I",
        second_species_ion_name="Ag II",
        medium_species_atom_name="Ar I",
        medium_species_ion_name="Ar II",
        prominence_window_length=40,
        peak_minimum_requred_height=100,
    )
    app = Application(config)

    result = app.run()

    log_results(line_pair_checker, result)
    plot_figures(plotter, result)
