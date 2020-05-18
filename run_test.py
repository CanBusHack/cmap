from lib.scan_main import run_scan

log_file_name = 'LogFile'

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
