from spark_mec_bp.nist.fetchers import IonizationEnergyFetcher
from spark_mec_bp.nist.parsers import IonizationEnergyParser


class IonizationEnergyDataGetter:
    def __init__(
        self,
        ionization_energy_fetcher: IonizationEnergyFetcher,
        ionization_energy_parser: IonizationEnergyParser,
    ) -> None:
        self.ionization_energy_fetcher = ionization_energy_fetcher
        self.ionization_energy_parser = ionization_energy_parser

    def get_data(self, species_name: str) -> float:
        ionziation_energy_data = self.ionization_energy_fetcher.fetch(species_name)
        parsed_ionization_energy_data = (
            self.ionization_energy_parser.parse_ionization_energy(
                ionziation_energy_data
            )
        )

        return float(parsed_ionization_energy_data["Ionization Energy (1/cm)"].iloc[0])
