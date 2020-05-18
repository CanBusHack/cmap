class UDSNode:
    physical_request_id = None
    response_id = None
    functional_request_id = None
    can_networks = set([])
    diagnostic_services = set([])
    periodic_messages = [[]]
    _diagnostic_services_scan_complete = False

    def __init__(self,
                 physical_request_id=None,
                 response_id=None,
                 functional_request_id=None
                 ):
        self.physical_request_id = physical_request_id
        self.response_id = response_id
        self.functional_request_id = functional_request_id
        self.can_networks = set([])
        self.diagnostic_services = set([])
        self.periodic_messages = [[]]
        self._diagnostic_services_scan_complete = False

    def scan_for_services(self,
                          start_service_id=0,
                          end_service_id=0xFF,
                          skip_response_only_service_ids=True,
                          payload_extra_byte=b'\x00',
                          add_extra_payload_byte=False,
                          can_socket='can0'):

        if self._diagnostic_services_scan_complete:
            return self.diagnostic_services

        import isotp

        isotp_socket = isotp.socket(0.1)
        isotp_socket.set_opts(txpad=0x00, rxpad=0x00)
        address = isotp.Address(0, rxid=self.response_id, txid=self.physical_request_id)
        isotp_socket.bind(can_socket, address)

        if 0 < start_service_id < 0xFF:
            start_service_id = 0
        if 0 < end_service_id < 0xFF:
            end_service_id = 0xFF

        end_service_id = end_service_id & 0xFF
        start_service_id = start_service_id & 0xFF

        if end_service_id > start_service_id:
            increment_direction = 1
        else:
            increment_direction = -1

        non_supported_services_set = set([])
        supported_services_set = set([])

        for service_id in range(start_service_id, end_service_id, increment_direction):

            if skip_response_only_service_ids and (
                    0x3E < service_id < 0x4F or 0x7E < service_id < 0x83 or 0xBE < service_id < 0xFF):
                continue
            else:
                payload = service_id
                if payload >= 0x10:
                    l_payload = (len(hex(payload)) - 2) >> 1
                else:
                    l_payload = 1

                b_payload = payload.to_bytes(l_payload, 'big')

                isotp_socket.send(b_payload + (payload_extra_byte if add_extra_payload_byte else b''))
                while True:
                    recv = isotp_socket.recv()

                    if recv is not None:
                        response_service_id = recv[0]
                        if (response_service_id == 0x7F and recv[2] == 0x7F) or (
                                response_service_id == 0x7F and recv[2] == 0x80):
                            isotp_socket.send(b'\x10\x03')
                            supported_services_set.add(service_id)
                        elif response_service_id == service_id + 0x40 or (
                                response_service_id == 0x7F and recv[2] != 0x11):
                            supported_services_set.add(service_id)
                        else:
                            non_supported_services_set.add(service_id)
                    else:
                        break

        self.diagnostic_services = supported_services_set
        self._diagnostic_services_scan_complete = True
        return supported_services_set


class Service(UDSNode):

    def __init__(self):
        super().__init__(physical_request_id=None, response_id=None, functional_request_id=None)

    def _scan_for_service_subfunction(self,
                                      service_id,
                                      subfunction_length=1,
                                      can_scan_timeout=0.1,
                                      can_socket='can0',
                                      start_sub_function=0,
                                      end_sub_function=0xFF,
                                      increment=1,
                                      extra_data_field=False,
                                      extra_data_field_byte_string=b''):
        return Service._scan_for_service_subfunction(self,
                                                     service_id=service_id,
                                                     subfunction_length=subfunction_length,
                                                     can_scan_timeout=can_scan_timeout,
                                                     can_socket=can_socket,
                                                     start_sub_function=start_sub_function,
                                                     end_sub_function=end_sub_function,
                                                     increment=increment,
                                                     extra_data_field=extra_data_field,
                                                     extra_data_field_byte_string=extra_data_field_byte_string)


class Service0x10(Service):

    def __init__(self):
        super().__init__()
        self.service_10_probe = None

    def probe(self):

        self.service_10_probe = self._scan_for_service_subfunction(service_id=0x10,
                                                                   extra_data_field=True,
                                                                   extra_data_field_byte_string=b'\x00')


class Service0x11(Service):

    def __init__(self):
        super().__init__()
        self.service_11_probe = None

    def probe(self):

        self.service_11_probe = self._scan_for_service_subfunction(service_id=0x11,
                                                                   extra_data_field=True,
                                                                   extra_data_field_byte_string=b'\x00')


class Service0x22(Service):

    def __init__(self):
        super().__init__()
        self.service_22_probe = None

    def probe(self):

        self.service_22_probe = self._scan_for_service_subfunction(service_id=0x22,
                                                                   extra_data_field=True,
                                                                   extra_data_field_byte_string=b'\x00',
                                                                   increment=2)


class Service0x2E(Service):

    def __init__(self):
        super().__init__()
        self.service_2e_probe = None

    def probe(self):
        self.service_2e_probe = self._scan_for_service_subfunction(service_id=0x2E,
                                                                   extra_data_field=True,
                                                                   extra_data_field_byte_string=b'\x00')
