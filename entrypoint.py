import numpy as np
from spark_mec_bp import application
from spark_mec_bp.plotting import Plotter
from spark_mec_bp.lib import LinePairChecker


def log_results(line_pair_checker: LinePairChecker, result: application.Result):
    AuI_linepair_check = line_pair_checker.check_line_pairs(
        result.first_species_atomic_lines,
        result.first_species_integrals_data.integrals,
        result.temperature,
    )
    AgI_linepair_check = line_pair_checker.check_line_pairs(
        result.second_species_atomic_lines,
        result.second_species_integrals_data.integrals,
        result.temperature,
    )

    print(
        f"The number concentration ratio for \
            {config.first_species_atom_name}-{config.second_species_atom_name}: {result.total_concentration:8.5f}"
    )
    print(f"The temperature is: {result.temperature:6.3f} K")
    print(
        f"{config.first_species_atom_name} linepair deviations: {AuI_linepair_check}"
    )
    print(
        f"{config.second_species_atom_name} linepair deviations: {AgI_linepair_check}"
    )


def plot_figures(plotter: Plotter, result: application.Result):
    plotter.plot_original_spectrum(
        spectrum=result.original_spectrum,
        baseline=result.baseline,
        spectrum_intensity_column_index=config.spectrum_intensity_column_index
    )

    plotter.plot_saha_boltzmann_line_pairs(
        intensity_ratios=result.intensity_ratios,
        fitted_intensity_ratios=result.fitted_intensity_ratios
    )

    plotter.plot_baseline_corrected_spectrum_with_the_major_peaks(
        corrected_spectrum=result.corrected_spectrum,
        peak_indices=result.peak_indices,
        wlen=config.prominence_window_length,
        xlim=[400, 410],
        ylim=[0, 2000],
    )

    plotter.plot_voigt_fit("Au I", result.first_species_integrals_data.fits)
    plotter.plot_voigt_fit("Ag I", result.second_species_integrals_data.fits)


if __name__ == "__main__":
    plotter = Plotter()
    line_pair_checker = LinePairChecker()
    config = application.Config(
        spectrum_path="spark_mec_bp/application/test/test_data/input_data.asc",
        spectrum_wavelength_column_index=0,
        spectrum_intensity_column_index=10,
        first_species_target_peaks=np.array([312.278, 406.507, 479.26]),
        first_species_atom_name="Au I",
        first_species_ion_name="Au II",
        second_species_target_peaks=np.array([338.29, 520.9078, 546.54]),
        second_species_atom_name="Ag I",
        second_species_ion_name="Ag II",
        carrier_species_atom_name="Ar I",
        carrier_species_ion_name="Ar II",
        prominence_window_length=40,
        peak_minimum_requred_height=2000,
    )
    app = application.App(config)

    result = app.run()

    log_results(line_pair_checker, result)
    plot_figures(plotter, result)
