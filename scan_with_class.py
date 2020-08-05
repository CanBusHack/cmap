from lib.uds_node import UDSNode
from lib.net_can_bus import NetworkCanBus
from lib.service import Service
import time
import logging


logging.basicConfig(filename="scan_{}.log".format(time.time()), filemode='w', level=logging.DEBUG)

can0 = NetworkCanBus()  # Sets up the CAN Bus network for the Nodes

can0.scan_for_uds_ids(  # scans the CAN Bus for Tx/Rx Diagnostic IDs
    scan_service_id=0x3E,  # Choose between 0x10 or 0x3E for best results
    arb_id_scan_low=0x442,
    arb_id_scan_high=0x7E2,
    try_twice=False,
    prompt_wait_timeout=1,
    anti_collision_buffer_time=2)

for pair in can0.nodes:
    tx_id, rx_id = pair[0]
    print("{:03X}<==>{:03X}".format(tx_id, rx_id))

    node = UDSNode(tx_id, rx_id, can0.socket_can_description, enhanced_mode_session_byte=b'\x92')

    node.find_services(add_extra_payload_byte=True)

    list_of_services = ""
    for services in node.supported_services:
        list_of_services += "{:02X}, ".format(services)
    print(list_of_services[:-2])

    for service_id in node.diagnostic_services:
        result_data = Service(node.physical_request_id, node.response_id, service_id).find_subfunctions()

        report = "-----------------------------------------------------------------------------------------\n" \
                 "||  {:03X}||  Service {:02X}                                                                  ||\n" \
                 "||-----|| -----------------------------------------------------------------------------||\n" \
                 "||     || 00|| 01|| 02|| 03|| 04|| 05|| 06|| 07|| 08|| 09|| 0A|| 0B|| 0C|| 0D|| 0E|| 0F||\n" \
                 "||-----||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||---||\n" \
                 "".format(rx_id, service_id)

        for count, data in enumerate(result_data):
            if data["Supported"]:
                cell_info = "+ "
            elif data["Negative Response Code"] is not None:
                cell_info = "{:02x}".format(data["Negative Response Code"])
            else:
                cell_info = "  "

            if data["Subfunction Length"] > 0:
                if count % 0x10 == 0:
                    report += "|| {:04X}||".format(count)

                report += " {}||".format(cell_info)

                if count % 0x10 == 0x0F:
                    report += "\n"
        report += "-----------------------------------------------------------------------------------------"
        print(report)
        logging.debug(report)

        for d in result_data:
            if d["Supported"]:
                print(d["Data"])
