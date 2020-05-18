from lib.uds_node import UDSNode
from lib.net_can_bus import NetworkCanBus

can0 = NetworkCanBus()

can0.scan_for_uds_ids(service_id=0x10, arb_id_scan_low=0x5FF, arb_id_scan_high=0x604)

for pair in can0.nodes:
    tx_id, rx_id = pair[0]
    print("{:03X}<==>{:03X}".format(tx_id, rx_id))

    node = UDSNode(tx_id, rx_id)

    node.scan_for_services()
    service_print = ""

    for service_id in node.diagnostic_services:
        service_id.probe()

        service_print += "{:02X}, ".format(service_id)
    print(service_print[:-2])



