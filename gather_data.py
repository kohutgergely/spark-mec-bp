
import logging 
import pandas as pd
import lib.helper_functions as helper_functions


def main(config):
    if config["enabled"]:
        
        input_filename = config["input_filename"]
        output_filename = config["output_filename"]
        species = config["species"]
        upper_wavelength = config["upper_wavelength"]
        lower_wavelength = config["lower_wavelength"]
        constants = helper_functions.gather_nist_data(
            species=species,
            lower_wavelength=lower_wavelength,
            upper_wavelength=upper_wavelength
        )
        integrals = pd.read_csv(input_filename, sep="\s+", names=["exp_wl(nm)", "intensity"])
        integrals_with_constants = helper_functions.merge_constants_and_integrals(integrals, constants)
        integrals_with_constants.to_csv(output_filename, sep=" ", float_format="%.6e", header=False, index=False)


if __name__ == "__main__":
    config = helper_functions.read_config_file("config.yaml")
    main(config["gather_data"])
