from subfunction_scan import scan_for_service_subfunction


def remove_PID(data):
    if len(data) > 2:
        return data[2:]
    else:
        return None


def scan_for_service_22(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFFFF,
                        can_scan_timeout=0.4,
                        is_iso_extended_id=False,
                        subfunction_length=2
                        ):
    print("Starting Subfucntion Scan for Service 22...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x22,
                                     can_scan_timeout, is_iso_extended_id, subfunction_length)

    supported_subfunctions_new = []
    for sub, data in supported_subfunctions:
        supported_subfunctions_new.append([sub, remove_PID(data)])

    supported_subfunctions = supported_subfunctions_new

    return supported_subfunctions, unsupported_subfunctions
