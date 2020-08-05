class Service:
    physical_id = None
    response_id = None
    extra_data_field = False
    service_id = 0
    increment = 1
    subfunction_ceiling = b'\xFF'
    subfunction_floor = b'\x00'
    subfunction_length = 1
    padding_byte = 0x00
    protocol = 0
    can_scan_timeout = 1
    service_description = ""
    socketcan_interface = 'can0'
    results_subfuntions = []
    extra_data_field_byte_string = b''

    def __init__(self,
                 request_phyiscal_id=0x7E0,
                 response_id=0x7E8,
                 service_id=0x00,
                 subfunction_length=1,
                 padding_byte=0x00,
                 protocol=0,
                 socketcan_interface='can0',
                 can_scan_timeout=5,
                 extra_data_field=False,
                 extra_data_field_byte_string=b'',
                 scan_increment_step=1):

        self.physical_id = request_phyiscal_id
        self.response_id = response_id
        self.service_id = service_id
        self.subfunction_length = subfunction_length
        self.padding_byte = padding_byte
        self.results_subfuntions = []
        self.protocol = protocol
        self.can_scan_timeout = can_scan_timeout
        self.extra_data_field = extra_data_field
        self.extra_data_field_byte_string = extra_data_field_byte_string
        self.increment = scan_increment_step
        self.socketcan_interface = socketcan_interface

        self._set_subfunction_ceiling()
        self._set_subfunction_floor()
        self._set_service_description()

    def _get_socket(self):
        import isotp

        address = isotp.Address(0, rxid=self.response_id, txid=self.physical_id)

        isotp_socket = isotp.socket(timeout=self.can_scan_timeout)
        isotp_socket.set_opts(txpad=self.padding_byte, rxpad=self.padding_byte)
        isotp_socket.bind(self.socketcan_interface, address)

        return isotp_socket

    def _find_service_subfunction(self):

        try:

            import logging
            import time

            isotp_socket = self._get_socket()

            if self.subfunction_ceiling > self.subfunction_floor:
                increment_direction = 1 * self.increment
                lcoal_subfunction_floor = int.from_bytes(self.subfunction_floor, 'big')
                local_subfunction_ceiling = int.from_bytes(self.subfunction_ceiling, 'big')
            else:
                increment_direction = -1 * self.increment
                tmp_end_subfunction = int.from_bytes(self.subfunction_floor, 'big')
                lcoal_subfunction_floor = int.from_bytes(self.subfunction_ceiling, 'big')
                local_subfunction_ceiling = tmp_end_subfunction

            for sub_function_id in range(lcoal_subfunction_floor, local_subfunction_ceiling + 1, increment_direction):

                subfunction = sub_function_id.to_bytes(self.subfunction_length, 'big')
                payload = self.service_id.to_bytes(1, 'big') + subfunction

                if self.extra_data_field:
                    payload += self.extra_data_field_byte_string

                isotp_socket.send(payload)
                recv = isotp_socket.recv()

                current_time = time.time()
                while recv is None:
                    loop_time = time.time()
                    recv = isotp_socket.recv()
                    if current_time + self.can_scan_timeout < loop_time:
                        break

                temp_results = {}
                response_payload = None
                nrc = None
                is_supported = False

                if recv is not None:

                    response_service_id = recv[0]
                    if response_service_id == 0x7F:
                        nrc = recv[2]
                        logging.debug("Failed: {:02x}".format(nrc))

                    elif response_service_id == self.service_id + 0x40:
                        response_payload = recv[1:]  # TODO: Remove Echo of PID or LID in response_payload
                        # response_payload = recv[1 + subfunction_length:]  # This will remove the echo.
                        is_supported = True

                        logging.debug("Success: {}".format(payload))

                else:
                    logging.error("Didn't Receive Anything!: {}".format(payload))

                temp_results["Service ID"] = self.service_id
                temp_results["Service Description"] = self.service_description
                temp_results["Supported"] = is_supported
                temp_results["Subfunction Length"] = self.subfunction_length
                temp_results["Subfunction ID"] = sub_function_id
                temp_results["Data"] = response_payload
                temp_results["Negative Response Code"] = nrc

                self.results_subfuntions.append(temp_results)
        except KeyboardInterrupt:
            pass

        return self.results_subfuntions

    def find_subfunctions(self):
        zero_byte_subfunction = [0x02, 0x03, 0x04, 0x07, 0x0A]
        two_byte_subfunctions = [0x22, 0x2E]

        if self.service_id in two_byte_subfunctions:
            self.subfunction_length = 2
        elif self.service_id in zero_byte_subfunction:
            self.subfunction_length = 0
        else:
            self.subfunction_length = 1

        self._set_ceiling_floor()
        ret = self._find_service_subfunction()

        return ret

    def update_service_description(self):
        self._set_service_description()
        return 0

    def _set_service_description(self):
        if self.protocol == 0:
            #  UDS Services
            service_descriptions = {
                0x00: "None",
                0x01: "Request Current Powertrain Diagnostic Data",
                0x02: "Request Freeze Frame Data",
                0x03: "Request Emission-Related DTCs",
                0x04: "Clear/Reset Emission-Related DTCs",
                0x05: "Request O2 Sensor Monitoring Test Results",
                0x06: "Request On-Board Monitoring Test Results for Specific Monitored Systems",
                0x07: "Request Emission-Related DTCs Detected During Current or Last Completed Driving Cycle",
                0x08: "Request Control of On-Board Systems, Test or Component",
                0x09: "Request Vehicle Information",
                0x0a: "Request Emission-Related DTCs with Permanent Status",
                0x0b: "None",
                0x0c: "None",
                0x0d: "None",
                0x0e: "None",
                0x0f: "None",
                0x10: "Diagnostic Session Control",
                0x11: "ECU Reset",
                0x12: "None",
                0x13: "None",
                0x14: "Clear DTCs",
                0x15: "None",
                0x16: "None",
                0x17: "None",
                0x18: "None",
                0x19: "Read DTCs",
                0x1a: "None",
                0x1b: "None",
                0x1c: "None",
                0x1d: "None",
                0x1e: "None",
                0x1f: "None",
                0x20: "None",
                0x21: "None",
                0x22: "Read Data by ID",
                0x23: "Read Memory by Address",
                0x24: "Read Scaling by ID",
                0x25: "None",
                0x26: "None",
                0x27: "Security Access",
                0x28: "Communication Control",
                0x29: "None",
                0x2a: "Read Data by DID",
                0x2b: "None",
                0x2c: "Dynamically Controlled ID",
                0x2d: "None",
                0x2e: "Write Data by ID",
                0x2f: "Input Output Control",
                0x30: "None",
                0x31: "Routine Control",
                0x32: "None",
                0x33: "None",
                0x34: "Request Download",
                0x35: "Request Upload",
                0x36: "None",
                0x37: "Request Transfer Exit",
                0x38: "None",
                0x39: "None",
                0x3a: "None",
                0x3b: "None",
                0x3c: "None",
                0x3d: "Write Memory by Address",
                0x3e: "Tester Present",
                0x3f: "None",
                0x40: "None",
                0x41: "None",
                0x42: "None",
                0x43: "None",
                0x44: "None",
                0x45: "None",
                0x46: "None",
                0x47: "None",
                0x48: "None",
                0x49: "None",
                0x4a: "None",
                0x4b: "None",
                0x4c: "None",
                0x4d: "None",
                0x4e: "None",
                0x4f: "None",
                0x50: "None",
                0x51: "None",
                0x52: "None",
                0x53: "None",
                0x54: "None",
                0x55: "None",
                0x56: "None",
                0x57: "None",
                0x58: "None",
                0x59: "None",
                0x5a: "None",
                0x5b: "None",
                0x5c: "None",
                0x5d: "None",
                0x5e: "None",
                0x5f: "None",
                0x60: "None",
                0x61: "None",
                0x62: "None",
                0x63: "None",
                0x64: "None",
                0x65: "None",
                0x66: "None",
                0x67: "None",
                0x68: "None",
                0x69: "None",
                0x6a: "None",
                0x6b: "None",
                0x6c: "None",
                0x6d: "None",
                0x6e: "None",
                0x6f: "None",
                0x70: "None",
                0x71: "None",
                0x72: "None",
                0x73: "None",
                0x74: "None",
                0x75: "None",
                0x76: "None",
                0x77: "None",
                0x78: "None",
                0x79: "None",
                0x7a: "None",
                0x7b: "None",
                0x7c: "None",
                0x7d: "None",
                0x7e: "None",
                0x7f: "None",
                0x80: "None",
                0x81: "None",
                0x82: "None",
                0x83: "Access Timing Parameters",
                0x84: "Secured Data Transmission",
                0x85: "Control DTC Setting",
                0x86: "Respond On Event",
                0x87: "Link Control",
                0x88: "None",
                0x89: "None",
                0x8a: "None",
                0x8b: "None",
                0x8c: "None",
                0x8d: "None",
                0x8e: "None",
                0x8f: "None",
                0x90: "None",
                0x91: "None",
                0x92: "None",
                0x93: "None",
                0x94: "None",
                0x95: "None",
                0x96: "None",
                0x97: "None",
                0x98: "None",
                0x99: "None",
                0x9a: "None",
                0x9b: "None",
                0x9c: "None",
                0x9d: "None",
                0x9e: "None",
                0x9f: "None",
                0xa0: "None",
                0xa1: "None",
                0xa2: "None",
                0xa3: "None",
                0xa4: "None",
                0xa5: "None",
                0xa6: "None",
                0xa7: "None",
                0xa8: "None",
                0xa9: "None",
                0xaa: "None",
                0xab: "None",
                0xac: "None",
                0xad: "None",
                0xae: "None",
                0xaf: "None",
                0xb0: "None",
                0xb1: "None",
                0xb2: "None",
                0xb3: "None",
                0xb4: "None",
                0xb5: "None",
                0xb6: "None",
                0xb7: "None",
                0xb8: "None",
                0xb9: "None",
                0xba: "None",
                0xbb: "None",
                0xbc: "None",
                0xbd: "None",
                0xbe: "None",
                0xbf: "None",
                0xc0: "None",
                0xc1: "None",
                0xc2: "None",
                0xc3: "None",
                0xc4: "None",
                0xc5: "None",
                0xc6: "None",
                0xc7: "None",
                0xc8: "None",
                0xc9: "None",
                0xca: "None",
                0xcb: "None",
                0xcc: "None",
                0xcd: "None",
                0xce: "None",
                0xcf: "None",
                0xd0: "None",
                0xd1: "None",
                0xd2: "None",
                0xd3: "None",
                0xd4: "None",
                0xd5: "None",
                0xd6: "None",
                0xd7: "None",
                0xd8: "None",
                0xd9: "None",
                0xda: "None",
                0xdb: "None",
                0xdc: "None",
                0xdd: "None",
                0xde: "None",
                0xdf: "None",
                0xe0: "None",
                0xe1: "None",
                0xe2: "None",
                0xe3: "None",
                0xe4: "None",
                0xe5: "None",
                0xe6: "None",
                0xe7: "None",
                0xe8: "None",
                0xe9: "None",
                0xea: "None",
                0xeb: "None",
                0xec: "None",
                0xed: "None",
                0xee: "None",
                0xef: "None",
                0xf0: "None",
                0xf1: "None",
                0xf2: "None",
                0xf3: "None",
                0xf4: "None",
                0xf5: "None",
                0xf6: "None",
                0xf7: "None",
                0xf8: "None",
                0xf9: "None",
                0xfa: "None",
                0xfb: "None",
                0xfc: "None",
                0xfd: "None",
                0xfe: "None",
                0xff: "None",
            }
        elif self.protocol == 1:
            #  GMLAN Services
            service_descriptions = {
                0x00: "None",
                0x01: "Request Current Powertrain Diagnostic Data",
                0x02: "Request Freeze Frame Data",
                0x03: "Request Emission-Related DTCs",
                0x04: "Clear/Reset Emission-Related DTCs",
                0x05: "Request O2 Sensor Monitoring Test Results",
                0x06: "Request On-Board Monitoring Test Results for Specific Monitored Systems",
                0x07: "Request Emission-Related DTCs Detected During Current or Last Completed Driving Cycle",
                0x08: "Request Control of On-Board Systems, Test or Component",
                0x09: "Request Vehicle Information",
                0x0a: "Request Emission-Related DTCs with Permanent Status",
                0x0b: "None",
                0x0c: "None",
                0x0d: "None",
                0x0e: "None",
                0x0f: "None",
                0x10: "Initiate Diagnostics",
                0x11: "None",
                0x12: "Read Failure Record",
                0x13: "None",
                0x14: "None",
                0x15: "None",
                0x16: "None",
                0x17: "None",
                0x18: "None",
                0x19: "None",
                0x1a: "Read DID",
                0x1b: "None",
                0x1c: "None",
                0x1d: "None",
                0x1e: "None",
                0x1f: "None",
                0x20: "Return to Normal",
                0x21: "None",
                0x22: "Read Data by ID",
                0x23: "Read Memory by Address",
                0x24: "None",
                0x25: "None",
                0x26: "None",
                0x27: "Security Access",
                0x28: "Disable Normal Communication",
                0x29: "None",
                0x2a: "None",
                0x2b: "None",
                0x2c: "Define Dynamic DPID",
                0x2d: "Define PID by Memory Address",
                0x2e: "None",
                0x2f: "None",
                0x30: "None",
                0x31: "None",
                0x32: "None",
                0x33: "None",
                0x34: "Request Download",
                0x35: "None",
                0x36: "Transfer Data",
                0x37: "None",
                0x38: "None",
                0x39: "None",
                0x3a: "None",
                0x3b: "None",
                0x3c: "None",
                0x3d: "None",
                0x3e: "Tester Present",
                0x3f: "None",
                0x40: "None",
                0x41: "None",
                0x42: "None",
                0x43: "None",
                0x44: "None",
                0x45: "None",
                0x46: "None",
                0x47: "None",
                0x48: "None",
                0x49: "None",
                0x4a: "None",
                0x4b: "None",
                0x4c: "None",
                0x4d: "None",
                0x4e: "None",
                0x4f: "None",
                0x50: "None",
                0x51: "None",
                0x52: "None",
                0x53: "None",
                0x54: "None",
                0x55: "None",
                0x56: "None",
                0x57: "None",
                0x58: "None",
                0x59: "None",
                0x5a: "None",
                0x5b: "None",
                0x5c: "None",
                0x5d: "None",
                0x5e: "None",
                0x5f: "None",
                0x60: "None",
                0x61: "None",
                0x62: "None",
                0x63: "None",
                0x64: "None",
                0x65: "None",
                0x66: "None",
                0x67: "None",
                0x68: "None",
                0x69: "None",
                0x6a: "None",
                0x6b: "None",
                0x6c: "None",
                0x6d: "None",
                0x6e: "None",
                0x6f: "None",
                0x70: "None",
                0x71: "None",
                0x72: "None",
                0x73: "None",
                0x74: "None",
                0x75: "None",
                0x76: "None",
                0x77: "None",
                0x78: "None",
                0x79: "None",
                0x7a: "None",
                0x7b: "None",
                0x7c: "None",
                0x7d: "None",
                0x7e: "None",
                0x7f: "None",
                0x80: "None",
                0x81: "None",
                0x82: "None",
                0x83: "None",
                0x84: "None",
                0x85: "None",
                0x86: "None",
                0x87: "None",
                0x88: "None",
                0x89: "None",
                0x8a: "None",
                0x8b: "None",
                0x8c: "None",
                0x8d: "None",
                0x8e: "None",
                0x8f: "None",
                0x90: "None",
                0x91: "None",
                0x92: "None",
                0x93: "None",
                0x94: "None",
                0x95: "None",
                0x96: "None",
                0x97: "None",
                0x98: "None",
                0x99: "None",
                0x9a: "None",
                0x9b: "None",
                0x9c: "None",
                0x9d: "None",
                0x9e: "None",
                0x9f: "None",
                0xa0: "None",
                0xa1: "None",
                0xa2: "Report Programming State",
                0xa3: "None",
                0xa4: "None",
                0xa5: "Programming Mode",
                0xa6: "None",
                0xa7: "None",
                0xa8: "None",
                0xa9: "Check Codes",
                0xaa: "Read Data by Packet ID",
                0xab: "None",
                0xac: "None",
                0xad: "None",
                0xae: "Device Control",
                0xaf: "None",
                0xb0: "None",
                0xb1: "None",
                0xb2: "None",
                0xb3: "None",
                0xb4: "None",
                0xb5: "None",
                0xb6: "None",
                0xb7: "None",
                0xb8: "None",
                0xb9: "None",
                0xba: "None",
                0xbb: "None",
                0xbc: "None",
                0xbd: "None",
                0xbe: "None",
                0xbf: "None",
                0xc0: "None",
                0xc1: "None",
                0xc2: "None",
                0xc3: "None",
                0xc4: "None",
                0xc5: "None",
                0xc6: "None",
                0xc7: "None",
                0xc8: "None",
                0xc9: "None",
                0xca: "None",
                0xcb: "None",
                0xcc: "None",
                0xcd: "None",
                0xce: "None",
                0xcf: "None",
                0xd0: "None",
                0xd1: "None",
                0xd2: "None",
                0xd3: "None",
                0xd4: "None",
                0xd5: "None",
                0xd6: "None",
                0xd7: "None",
                0xd8: "None",
                0xd9: "None",
                0xda: "None",
                0xdb: "None",
                0xdc: "None",
                0xdd: "None",
                0xde: "None",
                0xdf: "None",
                0xe0: "None",
                0xe1: "None",
                0xe2: "None",
                0xe3: "None",
                0xe4: "None",
                0xe5: "None",
                0xe6: "None",
                0xe7: "None",
                0xe8: "None",
                0xe9: "None",
                0xea: "None",
                0xeb: "None",
                0xec: "None",
                0xed: "None",
                0xee: "None",
                0xef: "None",
                0xf0: "None",
                0xf1: "None",
                0xf2: "None",
                0xf3: "None",
                0xf4: "None",
                0xf5: "None",
                0xf6: "None",
                0xf7: "None",
                0xf8: "None",
                0xf9: "None",
                0xfa: "None",
                0xfb: "None",
                0xfc: "None",
                0xfd: "None",
                0xfe: "None",
                0xff: "None",
            }
        else:
            # None
            service_descriptions = {
                0x00: "None",
                0x01: "Request Current Powertrain Diagnostic Data",
                0x02: "Request Freeze Frame Data",
                0x03: "Request Emission-Related DTCs",
                0x04: "Clear/Reset Emission-Related DTCs",
                0x05: "Request O2 Sensor Monitoring Test Results",
                0x06: "Request On-Board Monitoring Test Results for Specific Monitored Systems",
                0x07: "Request Emission-Related DTCs Detected During Current or Last Completed Driving Cycle",
                0x08: "Request Control of On-Board Systems, Test or Component",
                0x09: "Request Vehicle Information",
                0x0a: "Request Emission-Related DTCs with Permanent Status",
                0x0b: "None",
                0x0c: "None",
                0x0d: "None",
                0x0e: "None",
                0x0f: "None",
                0x10: "Diagnostic Session Control",
                0x11: "ECU Reset",
                0x12: "None",
                0x13: "None",
                0x14: "Clear DTCs",
                0x15: "None",
                0x16: "None",
                0x17: "None",
                0x18: "None",
                0x19: "Read DTCs",
                0x1a: "None",
                0x1b: "None",
                0x1c: "None",
                0x1d: "None",
                0x1e: "None",
                0x1f: "None",
                0x20: "None",
                0x21: "None",
                0x22: "Read Data by ID",
                0x23: "Read Memory by Address",
                0x24: "Read Scaling by ID",
                0x25: "None",
                0x26: "None",
                0x27: "Security Access",
                0x28: "Communication Control",
                0x29: "None",
                0x2a: "Read Data by DID",
                0x2b: "None",
                0x2c: "Dynamically Controlled ID",
                0x2d: "None",
                0x2e: "Write Data by ID",
                0x2f: "Input Output Control",
                0x30: "None",
                0x31: "Routine Control",
                0x32: "None",
                0x33: "None",
                0x34: "Request Download",
                0x35: "Request Upload",
                0x36: "None",
                0x37: "Request Transfer Exit",
                0x38: "None",
                0x39: "None",
                0x3a: "None",
                0x3b: "None",
                0x3c: "None",
                0x3d: "Write Memory by Address",
                0x3e: "Tester Present",
                0x3f: "None",
                0x40: "None",
                0x41: "None",
                0x42: "None",
                0x43: "None",
                0x44: "None",
                0x45: "None",
                0x46: "None",
                0x47: "None",
                0x48: "None",
                0x49: "None",
                0x4a: "None",
                0x4b: "None",
                0x4c: "None",
                0x4d: "None",
                0x4e: "None",
                0x4f: "None",
                0x50: "None",
                0x51: "None",
                0x52: "None",
                0x53: "None",
                0x54: "None",
                0x55: "None",
                0x56: "None",
                0x57: "None",
                0x58: "None",
                0x59: "None",
                0x5a: "None",
                0x5b: "None",
                0x5c: "None",
                0x5d: "None",
                0x5e: "None",
                0x5f: "None",
                0x60: "None",
                0x61: "None",
                0x62: "None",
                0x63: "None",
                0x64: "None",
                0x65: "None",
                0x66: "None",
                0x67: "None",
                0x68: "None",
                0x69: "None",
                0x6a: "None",
                0x6b: "None",
                0x6c: "None",
                0x6d: "None",
                0x6e: "None",
                0x6f: "None",
                0x70: "None",
                0x71: "None",
                0x72: "None",
                0x73: "None",
                0x74: "None",
                0x75: "None",
                0x76: "None",
                0x77: "None",
                0x78: "None",
                0x79: "None",
                0x7a: "None",
                0x7b: "None",
                0x7c: "None",
                0x7d: "None",
                0x7e: "None",
                0x7f: "None",
                0x80: "None",
                0x81: "None",
                0x82: "None",
                0x83: "Access Timing Parameters",
                0x84: "Secured Data Transmission",
                0x85: "Control DTC Setting",
                0x86: "Respond On Event",
                0x87: "Link Control",
                0x88: "None",
                0x89: "None",
                0x8a: "None",
                0x8b: "None",
                0x8c: "None",
                0x8d: "None",
                0x8e: "None",
                0x8f: "None",
                0x90: "None",
                0x91: "None",
                0x92: "None",
                0x93: "None",
                0x94: "None",
                0x95: "None",
                0x96: "None",
                0x97: "None",
                0x98: "None",
                0x99: "None",
                0x9a: "None",
                0x9b: "None",
                0x9c: "None",
                0x9d: "None",
                0x9e: "None",
                0x9f: "None",
                0xa0: "None",
                0xa1: "None",
                0xa2: "None",
                0xa3: "None",
                0xa4: "None",
                0xa5: "None",
                0xa6: "None",
                0xa7: "None",
                0xa8: "None",
                0xa9: "None",
                0xaa: "None",
                0xab: "None",
                0xac: "None",
                0xad: "None",
                0xae: "None",
                0xaf: "None",
                0xb0: "None",
                0xb1: "None",
                0xb2: "None",
                0xb3: "None",
                0xb4: "None",
                0xb5: "None",
                0xb6: "None",
                0xb7: "None",
                0xb8: "None",
                0xb9: "None",
                0xba: "None",
                0xbb: "None",
                0xbc: "None",
                0xbd: "None",
                0xbe: "None",
                0xbf: "None",
                0xc0: "None",
                0xc1: "None",
                0xc2: "None",
                0xc3: "None",
                0xc4: "None",
                0xc5: "None",
                0xc6: "None",
                0xc7: "None",
                0xc8: "None",
                0xc9: "None",
                0xca: "None",
                0xcb: "None",
                0xcc: "None",
                0xcd: "None",
                0xce: "None",
                0xcf: "None",
                0xd0: "None",
                0xd1: "None",
                0xd2: "None",
                0xd3: "None",
                0xd4: "None",
                0xd5: "None",
                0xd6: "None",
                0xd7: "None",
                0xd8: "None",
                0xd9: "None",
                0xda: "None",
                0xdb: "None",
                0xdc: "None",
                0xdd: "None",
                0xde: "None",
                0xdf: "None",
                0xe0: "None",
                0xe1: "None",
                0xe2: "None",
                0xe3: "None",
                0xe4: "None",
                0xe5: "None",
                0xe6: "None",
                0xe7: "None",
                0xe8: "None",
                0xe9: "None",
                0xea: "None",
                0xeb: "None",
                0xec: "None",
                0xed: "None",
                0xee: "None",
                0xef: "None",
                0xf0: "None",
                0xf1: "None",
                0xf2: "None",
                0xf3: "None",
                0xf4: "None",
                0xf5: "None",
                0xf6: "None",
                0xf7: "None",
                0xf8: "None",
                0xf9: "None",
                0xfa: "None",
                0xfb: "None",
                0xfc: "None",
                0xfd: "None",
                0xfe: "None",
                0xff: "None",
            }

        if 0 <= self.service_id <= 0xFF:
            self.service_description = service_descriptions[self.service_id]

            return self.service_description

        return "Service ID Out of Range"

    def _scan_memory(self, memorySize_parameter=1,
                     memoryAddress_parameter=4,
                     memorySize=4,
                     start_memory_address=0,
                     end_percent_of_address_space=100,
                     increment_speed=1):
        import time
        import logging

        isotp_socket = self._get_socket()

        service_23_subfunction = ((memorySize_parameter & 0xF) << 4 + (memoryAddress_parameter & 0xF)).to_bytes(1, 'big')
        memory_size = memorySize.to_bytes(memorySize_parameter, 'big')
        memory_address_ceiling = b'\xFF' * memorySize_parameter
        mem_ceiling = int(memory_address_ceiling, 16)
        end_memory_address = int(mem_ceiling * (end_percent_of_address_space / 100))

        memory_dump_results = []
        temp_results = {}

        for address in range(start_memory_address, end_memory_address, increment_speed):

            memory_address = address.to_bytes(memorySize_parameter, 'big')

            payload = b'\x23' + service_23_subfunction + memory_address + memory_size
            isotp_socket.send(payload)
            recv = isotp_socket.recv()

            current_time = time.time()
            while recv is None:
                loop_time = time.time()
                if current_time + self.can_scan_timeout < loop_time:
                    break

            nrc = 0
            memory_data = None
            is_supported = False

            if recv is not None:
                response_service_id = recv[0]

                if response_service_id == 0x7F:
                    nrc = recv[2]
                    # logging.debug("Failed: {:02x}".format(nrc))
                    is_supported = True
                elif response_service_id == 0x63:
                    memory_data = recv[1:]
                else:
                    logging.debug("Incorrect Response Service ID: {:02X}".format(response_service_id))
            else:
                logging.debug("No Response Received for Address {:{}X}".format(address, memorySize_parameter))

            temp_results["Service ID"] = self.service_id
            temp_results["Service Description"] = self.service_description
            temp_results["Supported"] = is_supported
            temp_results["Subfunction Length"] = self.subfunction_length
            temp_results["Data"] = memory_data
            temp_results["Negative Response Code"] = nrc

        return memory_dump_results.append(temp_results)

    def _set_subfunction_ceiling(self):
        self.subfunction_ceiling = b'\xFF' * self.subfunction_length
        return self.subfunction_ceiling

    def _set_subfunction_floor(self):
        self.subfunction_floor = b'\x00'
        return self.subfunction_floor

    def _set_ceiling_floor(self):
        self._set_subfunction_floor()
        self._set_subfunction_ceiling()
        return 0

    def scan_service_10(self, start_subfunction=b'\x00', end_subfunction=b'\xFF'):
        self.service_id = 0x10
        self.subfunction_length = 1
        self.subfunction_floor = start_subfunction
        self.subfunction_ceiling = end_subfunction
        return self.find_subfunctions()

    def scan_service_22(self, start_subfunction=b'\x00', end_subfunction=b'\xFF\xFF'):
        self.service_id = 0x22
        self.subfunction_floor = start_subfunction
        self.subfunction_ceiling = end_subfunction
        return self.find_subfunctions()

    def scan_service_23(self):
        self.service_id = 0x23
        self.extra_data_field = True
        self.extra_data_field_byte_string = b'0x24'
        return self.find_subfunctions()

    def dump_memory_using_service_23(self, memorySize_parameter=1, memoryAddress_parameter=4):
        self.service_id = 0x23
        self._scan_memory(memorySize_parameter=memorySize_parameter, memoryAddress_parameter=memoryAddress_parameter)

    def scan_serivce_27(self, start_level=b'\x01', end_level=b'\xFE'):
        self.service_id = 0x27
        self.subfunction_floor = start_level
        self.subfunction_ceiling = end_level
        self.increment = 2
        return self.find_subfunctions()
