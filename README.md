# Spark Multi-element Combinatory Boltzmann Plot


## What is it?

<p align="justify">
Spark Multi-element Combinatory Boltzmann Plot is an OES-based approach to deduce the number concentration ratio of two elements present in a spark discharge plasma employed for binary NP generation in the gas phase. It is aimed to provide a tool for investigating the evolution of the concentration ratio corresponding to the ablated electrode materials in spark-based NP generators under real operational conditions. The method is based on the construction of a Boltzmann plot for the spectral line intensity ratios at every combination. The produced plots (the so-called multi-element combinatory Boltzmann plots, MEC-BPs) are directly related to the LTE plasma temperature and the number concentration ratio of the neutral atoms. The total concentration ratio – including ions – is calculated from a simple plasma model, without requiring further measurements.
</p>

## Table of Contents

- [Installation](#installation-from-sources)
- [Usage](#usage)
    - [Concentration calculation](#concentration-calculation)
        - [Running the app](#running-the-app)
        - [Configuring the app](#configuring-the-app)
        - [Accessing the results](#accessing-the-results)
        - [Validation and plotting](#validation-and-plotting)
    - [Querying data from NIST database](#querying-data-from-nist-database)
        - [Fetching data](#fetching-data)
            - [Fetching atomic lines data](#fetching-atomic-lines-data)
            - [Fetching atomic levels data](#fetching-atomic-levels-data)
            - [Fetching ionization energies](#fetching-ionization-energies)
        - [Parsing fetched data](#parsing-fetched-data)
            - [Parse atomic lines data](#parse-atomic-lines-data)
            - [Parse atomic levels data](#parse-atomic-levels-data)
            - [Parse ionization energy data](#parse-ionization-energy-data)
- [License](#license)
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
<p align="justify">
As shown above, the **App** class needs to be instantiated with its config, an instance of **AppConfig**.
</p>

#### Configuring the app

<p align="justify">
The **AppConfig** itself can be configured with instances of the following config (sub)classes:
</p>

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

    :warning: ***As the program uses the NIST database to query atomic data, atom and ion name parameters must conform with NIST query conventions. For more information see: https://physics.nist.gov/PhysRefData/ASD/lines_form.html***
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
-  **VoigtIntegrationConfig**: configures parameters related the calculations of peak integral intensities.
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
- ***total_concentration***: the total calculated concentration ratio of the two target elements (float)
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

#### Validation and plotting

<p align="justify">
To validate the results the lin pair deviations can be checked using the LinePairChecker class:
</p>

```
from spark-mec-bp.validation import LinePairChecker

line_pair_checker = LinePairChecker()
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
    f"{config.first_species.atom_name} linepair deviations: {AuI_linepair_check}"
)
print(
    f"{config.second_species.atom_name} linepair deviations: {AgI_linepair_check}"
)
```

To be able to further analyize the results some predifined plots are also provided as methods of a separate Plotter class:

```
from spark_mec_bp.plotting import Plotter

plotter = Plotter()

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
    xlim=[400, 410],
    ylim=[0, 2000],
)

plotter.plot_voigt_fit("Au I", result.first_species_integrals_data.fits)
plotter.plot_voigt_fit("Ag I", result.second_species_integrals_data.fits)

```

## Querying data from NIST database

### Fetching data

<p align="justify">
The software can also be used to fetch data directly from NIST.
All three forms (atomic lines data, atomic levels data, ionization energies) can be fetched, although some limitations are still present compared to the capabilities of the online forms.

:warning: ***As the program uses the NIST database to query atomic data, spectrum parameter must conform with NIST query conventions. For more information see: https://physics.nist.gov/PhysRefData/ASD/lines_form.html***

</p>

#### Fetching atomic lines data

Atomic lines data can be fetched using the AtomicLinesFetcher class:

```
from spark_mec_bp.nist import fetchers

new_fetcher = fetchers.AtomicLinesFetcher()

atomic_lines_data = new_fetcher.fetch(
    spectrum="Ag I", lower_wavelength=400, upper_wavelength=800
)

print(atomic_lines_data.data)

```
The fetch function expects the following parameters:

* ***spectrum***: name of spectrum to be fetched, conforming NIST conventions (str)
* ***lower_wavelength***: lower wavelength of spectrum (int)
* ***upper_wavelength***: upper wavelength  of spectrum (int)

For more information regarding the form details and output see [NIST atomic lines form](https://physics.nist.gov/PhysRefData/ASD/lines_form.html).

Example output (truncated):

| obs_wl_air(nm) | ritz_wl_air(nm) | unc_ritz_wl | obs-ritz | wn(cm-1) | Aki(s^-1) | fik | S(a.u.) | log_gf | Acc | Ei(cm-1) | Ek(cm-1)   | conf_i  | term_i | J_i  | conf_k  | term_k | J_k  | g_i | g_k | Type |
| -------------- | --------------- | ----------- | -------- | --------- | --------- | --- | ------- | ------ | --- | --------- | ----------- | ------- | ------ | ---- | -------- | ------ | ---- | --- | --- | ---- |
| "405.5476"     | "405.54750"     | "0.00003"   | "0.0001"  | "24651.06" | ""        | ""  | ""      | ""     | ""  | "29552.05741" | "54203.119" | "4d10.5p" | "2P*"  | "1/2" | "4d10.6d" | "2D"   | "3/2" | 2   | 4   |      |
| "408.343"      | ""              | ""          | ""       | "24482.3" | ""        | ""  | ""      | ""     | ""  | ""            | ""          | ""       | ""     | ""    | ""       | ""     | ""   | ""  | ""  |      |
| "421.0960"     | "421.09542"     | "0.00005"   | "0.0006"  | "23740.87" | ""        | ""  | ""      | ""     | ""  | "30472.66516" | "54213.564" | "4d10.5p" | "2P*"  | "3/2" | "4d10.6d" | "2D"   | "5/2" | 4   | 6   |      |



#### Fetching atomic levels data

Atomic levels data can be fetched using the AtomicLevelsFetcher class:

```
from spark_mec_bp.nist import fetchers

new_fetcher = fetchers.AtomicLevelsFetcher()

atomic_levels_data = new_fetcher.fetch(
    "Ag I", lower_wavelength=400, upper_wavelength=800
)

print(atomic_levels_data.data)

```

The fetch function expects the following parameters:

* ***spectrum***: name of spectrum to be fetched, conforming NIST conventions (str)
* ***temperature***: temperature in eV to calculate partition function for (float)

For more information regarding the form details and output see [NIST atomic levels form](https://physics.nist.gov/PhysRefData/ASD/levels_form.html).

Example output (truncated):


| Configuration | Term | J   | g | Prefix | Level (cm-1)  | Suffix | Uncertainty (cm-1) |
| ------------- | ---- | --- | - | ------ | ------------- | ------ | ------------------ |
| "4d10.5s"     | "2S" | "1/2" | 2 | ""     | "0.000000"    | ""     | ""                 |
| "4d10.5p"     | "2P*" | "1/2" | 2 | ""     | "29552.05741" | ""     | "0.00014"          |
| "4d10.5p"     | "2P*" | "3/2" | 4 | ""     | "30472.66516" | ""     | "0.00022"          |
| "4d9.5s2"     | "2D" | "5/2" | 6 | ""     | "30242.298349" | ""     | "0.000006"         |


Partition function for Te = 5 eV: Z = 117.92


#### Fetching ionization energies

The ionization energies form can also be fetched using the IonizationEnergiesFetcher class:

```
from spark_mec_bp.nist import fetchers

new_fetcher = fetchers.IonizationEnergyFetcher()

ionization_energies_data = new_fetcher.fetch(
    spectrum="Ag I"
)

print(ionization_energies_data.data)

```

The fetch function expects the following parameters:

* ***spectrum***: name of spectrum to be fetched, conforming NIST conventions (str)

For more information regarding the form details and output see [NIST ionization energies form](https://physics.nist.gov/PhysRefData/ASD/ionEnergy.html).

Example output (truncated):

| At. num | Sp. Name | Ion Charge | El. Name | Isoel. Seq. | Ground Shells (a)      | Ground Config. | Ground Level | Ionized Level | Prefix | Ionization Energy (1/cm) | Suffix | Uncertainty (1/cm) |
| ------- | -------- | ---------- | -------- | ------------ | ---------------------- | -------------- | ------------ | ------------- | ------ | ----------------------- | ------ | ------------------ |
| "47"    | "Ag I"   | "0"        | "Silver" | "Ag"         | "[Kr].4d10.5s"         | "4d10.5s"      | "2S<1/2>"    | "4d10 1S<0>"  | ""     | "61106.45"              | ""     | "0.20"             |

(a) Designations used in the ground shell lists:
     [Kr] = 1s2.2s2.2p6.3s2.3p6.3d10.4s2.4p6

### Parsing fetched data

<p align="justify">
Data parsers are available to safely load and process the fetched data, which makes it possible to easily integrate NIST querying with other python codes.

The fetched tables are parsed into [pandas dataframes](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html), which is the only supported way, currently.
</p>

#### Parse atomic lines data

Atomic lines data can be parsed using the AtomicLinesParser class the following way:

```
from spark_mec_bp.nist import fetchers, parsers

new_fetcher = fetchers.AtomicLinesFetcher()

atomic_lines_data = new_fetcher.fetch(
    spectrum="Ag I",
    lower_wavelength=400,
    upper_wavelength=800
)

new_parser = parsers.AtomicLinesParser()
parsed_data = new_parser.parse_atomic_lines(atomic_lines_data)

print(parsed_data)
```

Exampe output (truncated):

| obs_wl_air(nm) | ritz_wl_air(nm) | unc_ritz_wl | obs-ritz | wn(cm-1) | Aki(s^-1) | fik | J_i | conf_k  | term_k | J_k | g_i | g_k | Type |
| -------------- | --------------- | ----------- | -------- | -------- | --------- | --- | --- | ------- | ------ | --- | --- | --- | ---- |
| 405.5476      | 405.547500      | 0.000030    | 0.0001   | 24651.060 | NaN       | NaN | 1/2 | 4d10.6d | 2D     | 3/2 | 2.0 | 4.0 | NaN  |
| 408.3430      | NaN             | NaN         | NaN      | 24482.300 | NaN       | NaN | NaN | NaN     | NaN    | NaN | NaN | NaN | NaN  |
| 421.0960      | 421.095420      | 0.000050    | 0.0006   | 23740.870 | NaN       | NaN | 3/2 | 4d10.6d | 2D     | 5/2 | 4.0 | 6.0 | NaN  |

#### Parse atomic levels data

Atomic levels data can be parsed using the AtomicLevelsParser class the following way:


```
from spark_mec_bp.nist import fetchers, parsers

new_fetcher = fetchers.AtomicLevelsFetcher()

atomic_levels_data = new_fetcher.fetch(
    spectrum="Ag I",
    temperature=5
)

new_parser = parsers.AtomicLevelsParser()
parsed_data = new_parser.parse_atomic_levels(atomic_levels_data)
partition_function = new_parser.parse_partition_function(atomic_levels_data)

print(parsed_data)
print(partition_function)
```

Example output for table (truncated):
| Configuration | Term | J    | g   | Prefix | Level (cm-1)  | Suffix | Uncertainty (cm-1) |
| ------------- | ---- | ---- | --- | ------ | ------------- | ------ | ------------------ |
| 4d10.5s       | 2S   | 1/2  | 2.0 | NaN    | 0.000000      | NaN    | NaN                |
| 4d10.5p       | 2P*  | 1/2  | 2.0 | NaN    | 29552.057410  | NaN    | 0.000140           |
| 4d10.5p       | 2P*  | 3/2  | 4.0 | NaN    | 30472.665160  | NaN    | 0.000220           |
| 4d9.5s2       | 2D   | 5/2  | 6.0 | NaN    | 30242.298349  | NaN    | 0.000006           |
| 4d9.5s2       | 2D   | 3/2  | 4.0 | NaN    | 34714.226430  | NaN    | 0.000100           |

Example output for partition function:
```
117.92
```


#### Parse ionization energy data

Ionization energy data can be parsed using the IonizationEnergyParser class the following way:

```
from spark_mec_bp.nist import fetchers, parsers

new_fetcher = fetchers.IonizationEnergyFetcher()

ionization_energy_data = new_fetcher.fetch(
    spectrum="Ag I",
)
print(ionization_energy_data.data)

new_parser = parsers.IonizationEnergyParser()
parsed_data = new_parser.parse_ionization_energy(ionization_energy_data)

print(parsed_data)

```

Exampe output:

| At. num | Sp. Name | Ion Charge | El. Name | Isoel. Seq. | Ground Shells (a) | Ground Config. | Ground Level | Ionized Level | Prefix | Ionization Energy (1/cm) | Suffix | Uncertainty (1/cm) |
| ------- | -------- | ---------- | -------- | ------------ | ----------------- | -------------- | ------------ | ------------- | ------ | ----------------------- | ------ | ------------------ |
| 47      | Ag I     | 0.0        | Silver   | Ag           | [Kr].4d10.5s      | 4d10.5s        | 2S<1/2>      | 4d10 1S<0>    | NaN    | 61106.45                | NaN    | 0.2                |



## License
[BSD 3](LICENSE)

## Getting Help

If you have general or usage questions or having trouble using the program, feel free to open an issue.

If you have technical/scientific questions contact [us](mailto:akohut@titan.physx.u-szeged.hu).
