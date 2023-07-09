# Spark Multi-element Combinatory Boltzmann Plots


## What is it?

Spark Multi-element Combinatory Boltzmann Plots is an OES-based approach to deduce the number concentration ratio of two elements present in a spark discharge plasma employed for binary NP generation in the gas phase. It is aimed to provide a tool for investigating the evolution of the concentration ratio corresponding to the ablated electrode materials in spark-based NP generators under real operational conditions. The method is based on the construction of a Boltzmann plot for the spectral line intensity ratios at every combination. The produced plots (the so-called multi-element combinatory Boltzmann plots, MEC-BPs) are directly related to the LTE plasma temperature and the number concentration ratio of the neutral atoms. The total concentration ratio – including ions – is calculated from a simple plasma model, without requiring further measurements.

## Table of Contents

- [Installation](#installation-from-sources)
- [License](#license)
- [Usage](#usage)
    - [Concentration calculation](#concentration-calculation)
        - [Running the app](#running-the-app)
        - [Configuring the app](#configuring-the-app)
        - [Accessing the results](#accessing-the-results)
- [Getting Help](#getting-help)


## Installation

You can install the package using pip:

pip install spark-mec-bp


## Usage

### Concentration calculation

#### Running the app

The program can be run in the following way:

```
from spark_mec_bp import application

config = application.AppConfig(
        spectrum=application.SpectrumConfig(
            file_path="spark_mec_bp/application/test/test_data/input_data.asc",
            wavelength_column_index=0,
            intensity_column_index=10
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
            minimum_requred_height=2000
        ),
        voigt_integration=application.VoigtIntegrationConfig(
            prominence_window_length=40
        )
    )

    app = application.App(config)

    result = app.run()
```
As shown above, the **App** class needs to be instantiated with its config, an instance of **AppConfig**.

#### Configuring the app


The **AppConfig** itself can be configured with instances of the following config (sub)classes:


- **SpectrumConfig**: configures parameters related to spectrum.
    ```
    SpectrumConfig(
            file_path="spark_mec_bp/application/test/test_data/input_data.asc",
            wavelength_column_index=0,
            intensity_column_index=10
        )
    ```
     Currently it can only read tabulated ascii spectrums:

        443.40219	33719.7	10634.2
        443.42908	31275.6	10916.1
        443.45596	32166.2	10073.6
        443.48285	31270.6	8646.38
        443.50974	28468.9	8518.12
    
    * ***file_path***: path to read ascii spectrum from
    * ***wavelength_column_index***: column index of the wavelengths, starting from zero
    * ***intensity_column_index***: column index of the intesities to use for calculation, starting from zero

-  **SpeciesConfig**: configures parameters for a species to estimate the concentration ratio for:
    ```
    SpeciesConfig(
        atom_name="Au I",
        ion_name="Au II",
        target_peaks=[312.278, 406.507, 479.26]
    )
    ```
    * ***atom_name***: neutral atom form of the target species.
    * ***ion_name***: ion form of the target species
    * ***target_peaks***: list of peaks to be used for concentration calculation

    :warning: ***As the program uses the NIST database to query atomic data, this field has to conform with NIST query conventions. For more information see: https://physics.nist.gov/PhysRefData/ASD/lines_form.html***
-  **CarrierGasConfig**: parameters related to the carrier gas. Used for electron concentration estimation.
    ```
    CarrierGasConfig(
        atom_name="Ar I",
        ion_name="Ar II"
    )
    ```
    * ***atom_name***: neutral atom form of the target species
    * ***ion_name***: ion form of the target species

-  **SpectrumCorrectionConfig**: configures parameters related to spectrum correction. It uses the [Asymmetrically Reweighted Penalized Least Squares Smoothing (arPLS)](https://doi.org/10.1039/C4AN01061B) algorithm
    ```
    SpectrumCorrectionConfig(
        iteration_limit=50,
        ratio=0.00001,
        lam=1000000
    )
    ```
    * ***iteration_limit***: number of iterations to perform
    * ***ratio***: wheighting deviations: 0 < ratio < 1, smaller values allow less negative values
    * ***lam***: parameter that can be adjusted by user. The larger lambda is, the smoother the resulting background
-  **PeakFindingConfig**: configures parameters related to peak finding. For more information see [scipy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html).
    ```
    PeakFindingConfig(
        minimum_requred_height=2000
    )
    ```
    * ***minimum_requred_height***: Required height of peak
-  **VoigtIntegrationConfig**: configures parameters related the calculations of peak integrals.
    ```
    VoigtIntegrationConfig(
        prominence_window_length=40
    )
    ```
    * ***prominence_window_length***: A window length in samples that optionally limits the evaluated area for each peak to a subset of x. For further information see [scipy documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.peak_prominences.html).

#### Accessing the results

The program provides the following results as an instance of a result class:

- ***original_spectrum*** the original spectrum (numpy.ndarray)
- ***corrected_spectrum***: the corrected spectrum (numpy.ndarray)
- ***baseline***: the calculated baseline (numpy.np.ndarray)
- ***peak_indices***: the detected peak indices (numpy.ndarray)
- ***intensity_ratios***: intensity ratios (numpy.ndarray)
- ***fitted_intensity_ratios***: fitted intensity ratios (np.ndarray)
- ***total_concentration***: the total calculated concentration (float)
- ***temperature***: the plasma temperature (float)
- ***first_species_atomic_lines***: the atomic lines data for the first species (numpy.ndarray)
- ***second_species_atomic_lines***: the atomic lines data for the second species (numpy.ndarray)
- ***first_species_integrals_data***: data related to integration of first species (VoigtIntegralData)
- ***second_species_integrals_data***: data related to integration of second species (VoigtIntegralData)

The integral data contains the following properties:

* ***integrals***: the integrals calculated for the selected peaks (numpy.ndarray)
* ***fits***: List of integral fits with the containing items having the follow properties:
    *  ***fit***: the fitted line (numpy.ndarray)
    *  ***wavelengths***: wavelengths used for integral calculation (numpy.ndarray)
    *  ***intensities***: the respective intensities (numpy.ndarray)

Example usage:
```
app = application.App(config)
result = app.run()
print(result.temperature)
print(result.second_species_integrals_data.fits[0].fit)
print(result.second_species_integrals_data.fits[0].wavelengths)
print(result.second_species_integrals_data.fits[0].intensities)
```

## License
[BSD 3](LICENSE)

## Getting Help

If you have general or usage questions or having trouble using the program, feel free to open an issue.

If you have technical/scientific questions contact [us](akohut@titan.physx.u-szeged.hu).
