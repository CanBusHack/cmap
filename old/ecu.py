from old import scan_for_services


class Ecu:

    def __init__(self,
                 rx_ids=None,
                 tx_id=None,
                 networks=None,
                 supported_services=None,
                 supported_service_subfunctions=None):
        self.physical_rx_id = rx_ids[0]
        self.functional_rx_id = rx_ids[1]
        self.rx_ids = rx_ids
        self.tx_id = tx_id
        self.networks = networks
        self.supported_services = supported_services
        self.supported_service_subfunctions = supported_service_subfunctions

    def refresh_ecu_supported_services(self, starting_sid=0x00, ending_sid=None, service_count=0):

        if service_count == 0 and ending_sid is None:
            ending_sid = 0xFF

        if starting_sid < 0:
            starting_sid = 0
        elif starting_sid > 0xFF:
            starting_sid = 0xFF

        if ending_sid is None:

            if service_count + starting_sid > 0xFF:
                service_count = 0xFF - starting_sid

            ending_sid = starting_sid + service_count

        self.supported_services = scan_for_services(self.physical_rx_id, self.tx_id, starting_sid, ending_sid)


    def refresh_service_for_supported_subfunctions(self, service_id, subfunction):

        service_subfunction_size = {
            0x10: 1,
            0x11: 1,
            0x14: 3,
            0x19: 2,
            0x22: 2,
            0x23: 1,
            0x24: -1,
            0x2A: 1,
            0x2B: 1,
            0x2E: 2,
            0x2F: 2,
            0x31: 1,
            
        }


        return 0
