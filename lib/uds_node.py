class UDSNode:
    physical_request_id = None
    response_id = None
    functional_request_id = None
    can_networks = set([])
    diagnostic_services = set([])
    periodic_messages = [[]]
    socket_can_interface = 'can0'
    start_service_id = 0
    end_service_id = 0xFF
    supported_services = set([])
    unsupported_service = set([])
    enhanced_mode_session_byte = b'\x03'
    can_scan_timeout = 0.01

    _diagnostic_services_scan_complete = False

    def __init__(self,
                 physical_request_id=None,
                 response_id=None,
                 functional_request_id=None,
                 socket_can_interface='can0',
                 start_service_id=0,
                 end_service_id=0xFF,
                 enhanced_mode_session_byte=b'\x03'
                 ):

        self.physical_request_id = physical_request_id
        self.response_id = response_id
        self.functional_request_id = functional_request_id
        self.can_networks = set([])
        self.diagnostic_services = set([])
        self.periodic_messages = [[]]
        self.socket_can_interface = socket_can_interface
        self.start_service_id = start_service_id
        self.end_service_id = end_service_id
        self.enhanced_mode_session_byte = enhanced_mode_session_byte
        self.supported_services = set([])

        self._diagnostic_services_scan_complete = False

    def find_services(self,
                      skip_response_only_service_ids=False,
                      scan_only_known_uds_services=True,
                      payload_extra_byte=b'\x00',
                      add_extra_payload_byte=False,
                      ):

        list_of_known_uds_services = [0x10, 0x11, 0x27, 0x28, 0x3E, 0x83, 0x84, 0x85, 0x86, 0x87, 0x22, 0x23,
                                      0x24, 0x2A, 0x2C, 0x2E, 0x3D, 0x14, 0x19, 0x2F, 0x34, 0x35, 0x36, 0x37]

        if self._diagnostic_services_scan_complete:
            return self.diagnostic_services

        import isotp
        import time

        isotp_socket = isotp.socket()
        isotp_socket.set_opts(txpad=0x00, rxpad=0x00)
        address = isotp.Address(0, rxid=self.response_id, txid=self.physical_request_id)
        isotp_socket.bind(self.socket_can_interface, address)

        if not (0 <= self.start_service_id <= 0xFF):
            self.start_service_id = 0
        if not (0 <= self.end_service_id <= 0xFF):
            self.end_service_id = 0xFF

        self.end_service_id = self.end_service_id & 0xFF
        self.start_service_id = self.start_service_id & 0xFF

        if self.end_service_id > self.start_service_id:
            increment_direction = 1
        else:
            increment_direction = -1

        for service_id in range(self.start_service_id, self.end_service_id, increment_direction):

            if skip_response_only_service_ids and (
                    0x3E < service_id < 0x4F or 0x7E < service_id < 0x83 or 0xBE < service_id < 0xFF):
                continue
            if scan_only_known_uds_services and not (service_id in list_of_known_uds_services):
                continue

            payload = service_id
            # fix to correct for the payload length
            if payload >= 0x10:
                payload_length = (len(hex(payload)) - 2) >> 1
            else:
                payload_length = 1

            payload_bytes = payload.to_bytes(payload_length, 'big')

            if add_extra_payload_byte:
                payload_bytes += b'\x00'

            # Some services only work with Extra Data
            isotp_socket.send(payload_bytes + payload_extra_byte)
            recv = isotp_socket.recv()

            current_time = time.time()
            while recv is None:
                loop_time = time.time()
                recv = isotp_socket.recv()
                if current_time + self.can_scan_timeout < loop_time:
                    break

            if recv is not None:
                response_service_id = recv[0]

                if response_service_id == 0x7F:
                    nrc = recv[2]

                    '''if nrc == 0x7F or nrc == 0x80:
                        isotp_socket.send(b'\x10' + self.enhanced_mode_session_byte)
                        recv = isotp_socket.recv()
                        time.sleep(0.1)
                        isotp_socket.send(b_payload + (payload_extra_byte if add_extra_payload_byte else b''))
                        continue'''
                    if nrc == 0x11:
                        self.unsupported_service.add(service_id)
                    else:
                        self.supported_services.add(service_id)
                else:
                    self.supported_services.add(service_id)

        self.diagnostic_services = self.supported_services
        self._diagnostic_services_scan_complete = True

        return self.supported_services
