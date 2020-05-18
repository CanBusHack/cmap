import time

from lib.subfunction_scan import scan_for_service_subfunction


def scan_for_service_10(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFF,
                        can_scan_timeout=0.1,
                        subfunction_length=1
                        ):
    print("Starting Subfucntion Scan for Service 10...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x10,
                                     can_scan_timeout, subfunction_length)

    return supported_subfunctions, unsupported_subfunctions


def scan_for_service_11(diagnostic_pair,
                        can_socket='can0',
                        start_sub_function=0,
                        end_sub_function=0xFF,
                        can_scan_timeout=0.1,
                        subfunction_length=1,
                        request_delay=1,
                        ):
    print("Starting Subfucntion Scan for Service 11...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x11,
                                     can_scan_timeout, subfunction_length)
    time.sleep(request_delay)

    return supported_subfunctions, unsupported_subfunctions


def remove_pid_lid(data, size):
    if len(data) > size:
        return data[size:]
    else:
        return None


def scan_for_service_22(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFFFF,
                        can_scan_timeout=0.4,
                        subfunction_length=2
                        ):
    print("Starting Subfucntion Scan for Service 22...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x22,
                                     can_scan_timeout, subfunction_length)

    supported_subfunctions_new = []
    for sub, data in supported_subfunctions:
        supported_subfunctions_new.append([sub, remove_pid_lid(data, subfunction_length)])

    supported_subfunctions = supported_subfunctions_new

    return supported_subfunctions, unsupported_subfunctions


def scan_for_service_27(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFF,
                        can_scan_timeout=0.1,
                        subfunction_length=1):
    print("Starting Subfucntion Scan for Service 27...")
    increment = 2

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair=diagnostic_pair,
                                     can_socket=can_socket,
                                     start_sub_function=start_sub_function,
                                     end_sub_function=end_sub_function,
                                     service_id=0x27,
                                     can_scan_timeout=can_scan_timeout,
                                     subfunction_length=subfunction_length,
                                     increment=increment)

    supported_subfunctions_new = []
    for sub, data in supported_subfunctions:
        supported_subfunctions_new.append([sub, remove_pid_lid(data, subfunction_length)])

    supported_subfunctions = supported_subfunctions_new

    return supported_subfunctions, unsupported_subfunctions


def scan_for_service_2e(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFFFF,
                        can_scan_timeout=0.4,
                        subfunction_length=2
                        ):
    print("Starting Subfucntion Scan for Service 2E...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x2E,
                                     can_scan_timeout, subfunction_length)

    supported_subfunctions_new = []
    for sub, data in supported_subfunctions:
        supported_subfunctions_new.append([sub, remove_pid_lid(data, subfunction_length)])

    supported_subfunctions = supported_subfunctions_new

    return supported_subfunctions, unsupported_subfunctions


def scan_for_service_2f(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFFFF,
                        can_scan_timeout=0.4,
                        subfunction_length=2
                        ):
    print("Starting Subfucntion Scan for Service 2F...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair=diagnostic_pair,
                                     can_socket=can_socket,
                                     start_sub_function=start_sub_function,
                                     end_sub_function=end_sub_function,
                                     service_id=0x2F,
                                     can_scan_timeout=can_scan_timeout,
                                     subfunction_length=subfunction_length,
                                     extra_data_field=True,
                                     extra_data_field_byte_string=b'\x00'
                                     )

    supported_subfunctions_new = []
    for sub, data in supported_subfunctions:
        supported_subfunctions_new.append([sub, remove_pid_lid(data, subfunction_length)])

    supported_subfunctions = supported_subfunctions_new

    return supported_subfunctions, unsupported_subfunctions
