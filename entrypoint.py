from spark_mec_bp import application
from spark_mec_bp.plotting import Plotter
from spark_mec_bp.validation import LinePairChecker


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
        f"The total number concentration ratio of the elements calculated from the \
            {config.first_species.atom_name}-{config.second_species.atom_name} lines: {result.total_concentration:8.5f}"
    )
    print(f"The temperature is: {result.temperature:6.3f} K")
    print(
        f"{config.first_species.atom_name} linepair deviations: {AuI_linepair_check}"
    )
    print(
        f"{config.second_species.atom_name} linepair deviations: {AgI_linepair_check}"
    )


def plot_figures(plotter: Plotter, result: application.Result):
    plotter.plot_original_spectrum(
        spectrum=result.original_spectrum,
        baseline=result.baseline,
        spectrum_intensity_column_index=config.spectrum.intensity_column_index
    )

    plotter.plot_saha_boltzmann_line_pairs(
        intensity_ratios=result.intensity_ratios,
        fitted_intensity_ratios=result.fitted_intensity_ratios
    )

    plotter.plot_baseline_corrected_spectrum_with_the_major_peaks(
        corrected_spectrum=result.corrected_spectrum,
        peak_indices=result.peak_indices,
        wlen=config.voigt_integration.prominence_window_length,
        xlim=[400, 522],
        ylim=[0, 0.05],
    )

    plotter.plot_voigt_fit("Au I", result.first_species_integrals_data.fits)
    plotter.plot_voigt_fit("Ag I", result.second_species_integrals_data.fits)


if __name__ == "__main__":
    plotter = Plotter()
    line_pair_checker = LinePairChecker()
    config = application.AppConfig(
        spectrum=application.SpectrumConfig(
            file_path="spark_mec_bp/application/test/test_data/noise_test.asc",
            wavelength_column_index=0,
            intensity_column_index=2
        ),
        first_species=application.SpeciesConfig(
            atom_name="Au I",
            ion_name="Au II",
            target_peaks=[312.278, 406.507, 479.26]
        ),
        second_species=application.SpeciesConfig(
            atom_name="Ag I",
            ion_name="Ag II",
            target_peaks=[338.29, 520.9078, 546.54]
        ),
        carrier_gas=application.CarrierGasConfig(
            atom_name="Ar I",
            ion_name="Ar II"
        ),
        spectrum_correction=application.SpectrumCorrectionConfig(
            iteration_limit=50,
            ratio=0.00001,
            lam=1000000
        ),
        peak_finding=application.PeakFindingConfig(
            minimum_requred_height=0.015
        ),
        voigt_integration=application.VoigtIntegrationConfig(
            prominence_window_length=60
        )
    )

    app = application.App(config)

    result = app.run()

    log_results(line_pair_checker, result)
    plot_figures(plotter, result)
