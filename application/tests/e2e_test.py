import numpy as np
from pytest import approx
from application import Application, ApplicationConfig


def test_application_e2e(mocker):
    first_species_atomic_lines = np.array(
        [
            [3.1227800e02, 1.9000000e07, 4.0000000e00, 4.1174613e04],
            [4.0650700e02, 8.5000000e07, 4.0000000e00, 6.1951600e04],
            [4.7925800e02, 8.9000000e07, 6.0000000e00, 6.2033700e04],
        ]
    )
    second_species_atomic_lines = np.array(
        [
            [3.38288700e02, 1.30000000e08, 2.00000000e00, 2.95520574e04],
            [5.20907800e02, 7.50000000e07, 4.00000000e00, 4.87439690e04],
            [5.46549700e02, 8.60000000e07, 6.00000000e00, 4.87642190e04],
        ]
    )
    partition_function_first_species_atom = 5.0
    partition_function_second_species_atom = 3.04
    partition_function_carrier_species_atom = 1.0
    partition_function_carrier_species_ion = 5.7
    partition_function_first_species_ion = 3.44
    ionization_energy_carrier_species = 127109.842
    ionization_energy_first_species = 74409.11
    partition_function_second_species_ion = 1.19
    ionization_energy_second_species = 61106.45

    atomic_lines_getter = mocker.patch(
        "application.app.AtomicLinesDataGetter",
    )
    atomic_lines_getter.return_value.get_data.side_effect = [
        first_species_atomic_lines,
        second_species_atomic_lines,
    ]
    partition_function_getter = mocker.patch(
        "application.app.PartitionFunctionDataGetter",
    )
    partition_function_getter.return_value.get_data.side_effect = [
        partition_function_first_species_atom,
        partition_function_first_species_ion,
        partition_function_second_species_atom,
        partition_function_second_species_ion,
        partition_function_carrier_species_atom,
        partition_function_carrier_species_ion,
    ]

    ioniztion_energy_getter = mocker.patch(
        "application.app.IonizationEnergyDataGetter",
    )
    ioniztion_energy_getter.return_value.get_data.side_effect = [
        ionization_energy_first_species,
        ionization_energy_second_species,
        ionization_energy_carrier_species,
    ]

    config = ApplicationConfig(
        spectrum_path="application/tests/test_data/input_data.asc",
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
        peak_minimum_requred_height=100,
    )
    app = Application(config)

    result = app.run()

    assert result.temperature == approx(12770.740, 0.001)
    assert result.total_concentration == approx(1.11428, 0.001)