class LineScraperConfig:
    
    url = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"
    
    limits_type = 0
    unit = 1
    de = 0
    format = 3
    line_out = 1
    remove_js = "on"
    en_unit = 0
    output = 0
    page_size = 15
    show_obs_wl = 1
    order_out = 0
    max_low_enrg = ""
    show_av = 2
    max_upp_enrg = ""
    tsb_value = 0
    min_str = ""
    A_out = 0
    max_str = ""
    min_accur = ""
    min_intens = ""
    allowed_out = 1
    enrg_out = "on"
    g_out = "on"
    submit = "Retrieve Data"

    def __init__(
        self,
        spectra: str,
        lower_wavelength: int,
        upper_wavelength: int,

    ) -> None:
        self.spectra = spectra
        self.low_w = lower_wavelength
        self.upp_w = upper_wavelength
