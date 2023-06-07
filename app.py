import logging
from datetime import datetime
from nist_sdk.atomic_levels import AtomicLevelsFetcher
from parsers.atomic_levels import AtomicLevelsParser

def set_logging():
    logging.captureWarnings(True) 
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s | %(levelname)-8s | %(message)s')
    file_handler = logging.FileHandler("{:%Y-%m-%d-%H-%M}.log".format(datetime.now()))
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

if __name__ == "__main__":
    set_logging()
    # config = helper_functions.read_config_file("config.yaml")
    atomic_levels_data = AtomicLevelsFetcher().fetch(
        spectrum="Ag I",
        temperature=300,
    )
    data = AtomicLevelsParser().parse_atomic_levels(atomic_levels_data)
    print(data)
    # prepare_spectrum.main(config["prepare_spectrum"])
    # gather_data.main(config["gather_data"])
    # plasma_temperature.main(config["plasma_temperature"])