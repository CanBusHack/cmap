import isotp


def scan_for_service_subfunction(diagnostic_pair,
                                 can_socket='can0',
                                 start_sub_function=0,
                                 end_sub_function=0xFFFF,
                                 service_id=0x22,
                                 can_scan_timeout=0.1,
                                 subfunction_length=2,
                                 increment=1,
                                 extra_data_field=False,
                                 extra_data_field_byte_string=b''
                                 ):
    tx_id, rx_id = diagnostic_pair
    address = isotp.Address(0, rxid=rx_id, txid=tx_id)

    isotp_socket = isotp.socket(timeout=can_scan_timeout)
    isotp_socket.set_opts(txpad=0x00, rxpad=0x00)
    isotp_socket.bind(can_socket, address)

    if end_sub_function > start_sub_function:
        increment_direction = 1 * increment
    else:
        increment_direction = -1 * increment
        tmp_end_subfunction = start_sub_function
        start_sub_function = end_sub_function
        end_sub_function = tmp_end_subfunction

    supported_subfunctions = []
    unsupported_subfunctions = []

    for sub_function_id in range(start_sub_function, end_sub_function + 1, increment_direction):

        payload = (service_id << (8 * subfunction_length)) + sub_function_id
        l_payload = (len(hex(payload)) - 2) >> 1
        b_payload = payload.to_bytes(l_payload, 'big')
        if extra_data_field:
            b_payload += extra_data_field_byte_string

        isotp_socket.send(b_payload)
        recv = isotp_socket.recv()

        if recv is not None:

            if recv[0] == 0x7F:
                nrc = recv[2]
                unsupported_subfunctions.append([sub_function_id, nrc])
            elif recv[0] == service_id + 0x40:
                supported_subfunctions.append([sub_function_id, recv[1:]])
        else:
            print("Didn't Receive Anything!: {}".format(b_payload.hex()))

    return supported_subfunctions, unsupported_subfunctions
