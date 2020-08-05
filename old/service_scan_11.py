import time

from subfunction_scan import scan_for_service_subfunction


def scan_for_service_11(diagnostic_pair,
                        can_socket,
                        start_sub_function=0,
                        end_sub_function=0xFF,
                        can_scan_timeout=0.1,
                        is_iso_extended_id=False,
                        subfunction_length=1,
                        request_delay=1
                        ):
    print("Starting Subfunction Scan for Service 11...")

    supported_subfunctions, unsupported_subfunctions = \
        scan_for_service_subfunction(diagnostic_pair, can_socket, start_sub_function, end_sub_function, 0x11,
                                     can_scan_timeout, is_iso_extended_id, subfunction_length)
    time.sleep(request_delay)

    return supported_subfunctions, unsupported_subfunctions
