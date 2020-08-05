
class UdsService:

    protocol = "ISO14229"
    is_supported = False


class DiagnosticSessionControl(UdsService):

    service_id = 0x10
    description = "Diagnostic Session Control"
    subfunction_bit_size = 7
    suppress_positive_response = False


class EcuReset(UdsService):

    service_id = 0x11
    description = "ECU Reset"
    subfunction_bit_size = 7
    suppress_positive_response = False


class HardReset(EcuReset):

    def __init__(self,
                 is_supported=False):
        self.is_supported = is_supported
        self.reset_type = 0x01
        self.description = "Hard Reset"


class KeyOffOnReset:

    def __init__(self,
                 is_supported=False):
        self.is_supported = is_supported
        self.reset_type = 0x02
        self.description = "Key Off On Reset"


class SoftReset:

    def __init__(self,
                 is_supported=False):
        self.is_supported = is_supported
        self.reset_type = 0x03
        self.description = "Soft Reset"


class EnableRapidPowerShutDown:

    def __init__(self,
                 is_supported=False):
        self.is_supported = is_supported
        self.reset_type = 0x04
        self.description = "Enable Rapid Power Shut Down"


class DisableRapidPowerShutDown:

    def __init__(self,
                 is_supported=False):
        self.is_supported = is_supported
        self.reset_type = 0x05
        self.description = "Disable Rapid Power Shut Down"

