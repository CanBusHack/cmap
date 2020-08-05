from old import run_scan

log_file_name = 'LogFile'

''' 
:start_arb_id - The first Arbitration ID to Scan.  We will scan the Arb ID and wait to see if we get a reponse from it.

:end_arb_id - This is the last Arbitration ID to Scan (can be less than or greater than the start_arb_id).  If this
is less than the start_arb_id, we will decrement IDs.  This can be useful on some vehicles.

:scan_for_services_start_service - uint_8 Parameter representing the Service ID to start scanning. 0 is the lowest

:scan_for_services_end_service - uint_8 Parameter representing the final Service ID for scanning. 0xFF is highest.
Some vehicles and controllers you may want the scan_for_services_end_service to be lower than the 
scan_for_services_start_service

:socket_can_interface - which socket can interface to use for the scan.

:can_scan_timeout - Wait time after sending a request before aborting and moving to the next request.

:scan_for_service_subfunctions - Certain services can be probed more, such as requesting all of the possible 
subfunctions that may be associated with the service. This will increase the scan time.

:service_10_start_subfunction - If scan_for_service_subfunctions is True, then this is the first Subfuntion to scan 
with service 0x10 (Start Diagnostics).

:service_10_end_subfunction - If scan_for_service_subfunctions is True, then this is the last Subfuntion to scan 
with service 0x10 (Start Diagnostics).

:service_22_2e_2f_start_PID - If scan_for_service_subfunctions is True, then this is the first Subfuntion to scan 
with services 0x22, 0x2E, 0x2F.

:service_22_2e_2f_end_PID - If scan_for_service_subfunctions is True, then this is the last PID to scan 
with services 0x22, 0x2E, 0x2F.

:service_11_start_subfunction - If scan_for_service_subfunctions is True, then this is the first Subfuntion to scan 
with services 0x11 (Reset ECU)

:service_11_end_subfunction - If scan_for_service_subfunctions is True, then this is the last Subfuntion to scan 
with services 0x11 (Reset ECU)

:service_27_start_level - If scan_for_service_subfunctions is True, then this is the first security level to scan 
with services 0x27 (Security Access)

:service_27_end_level - If scan_for_service_subfunctions is True, then this is the last security level to scan 
with services 0x27 (Security Access)

:try_twice - When scanning Arbitration IDs, we wait for any message to return within the can_scan_timeout time. 
This will lead to a few false positives. By trying twice we can eliminate nearly all false positives. This will take 
longer to do the initial scan.

:verbose_mode - Print more information out.

'''

tree = run_scan(start_arb_id=0x600,
                end_arb_id=0x602,
                scan_for_services_start_service=0x0,
                scan_for_services_end_service=0xFF,
                socket_can_interface='can0',
                can_scan_timeout=0.4,
                scan_for_service_subfunctions=False,
                service_10_start_subfunction=1,
                service_10_end_subfunction=0xFF,
                service_22_2e_2f_start_PID=0x0000,
                service_22_2e_2f_end_PID=0x0000,
                service_11_start_subfunction=1,
                service_11_end_subfunction=0xFF,
                service_27_start_level=1,
                service_27_end_level=0xFF,
                try_twice=True,  # Run once isn't working
                verbose_mode=True,
                )

tree.show()
