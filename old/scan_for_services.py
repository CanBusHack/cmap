import isotp


def scan_for_services(diagnostic_tx_arb_id,
                      diagnostic_rx_arb_id,
                      start_service_id,
                      end_service_id,
                      can_socket='can0',
                      skip_response_only_service_ids=True,
                      add_extra_payload_byte=True,
                      payload_extra_byte=b'\x00'):
    # print("Starting Services Scan on {:03X}<==>{:03X} ...".format(diagnostic_tx_arb_id, diagnostic_rx_arb_id))

    tx_id, rx_id = [diagnostic_tx_arb_id, diagnostic_rx_arb_id]
    isotp_socket = isotp.socket(0.1)
    isotp_socket.set_opts(txpad=0x00, rxpad=0x00)
    address = isotp.Address(0, rxid=rx_id, txid=tx_id)
    isotp_socket.bind(can_socket, address)

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
                    elif response_service_id == service_id + 0x40 or (response_service_id == 0x7F and recv[2] != 0x11):
                        supported_services_set.add(service_id)
                    else:
                        non_supported_services_set.add(service_id)
                else:
                    break

    return supported_services_set
