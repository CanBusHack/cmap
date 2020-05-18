class NetworkCanBus:
    socket_can_description = None
    can_interface = None
    bitrate = None
    nodes = None
    normal_mode_messages = None

    def __init__(self,
                 socket_can_description='can0',
                 can_interface='socketcan',
                 bitrate=500000,
                 nodes=None,
                 normal_mode_messages=None):

        self.socket_can_description = socket_can_description
        self.can_interface = can_interface
        self.bitrate = bitrate
        self.nodes = nodes
        self.normal_mode_messages = normal_mode_messages

    def scan_for_uds_ids(self,
                         service_id=0x3E,
                         anti_collision_buffer_time=6,  # Time in seconds to listen to the bus
                         message_length=2,
                         message_subfunctions=0,
                         arb_id_scan_low=0,
                         arb_id_scan_high=0x7FF,
                         scan_direction=1,
                         try_twice=True,
                         ):

        import can
        import logging
        import time
        from inputimeout import inputimeout, TimeoutOccurred

        bus = can.Bus(interface=self.can_interface, channel=self.socket_can_description, receive_own_messages=True)

        logging.info("Listening for Current Arb IDs So we Don't Clobber Them!...")
        normal_messages = set([])

        start_time = time.time()
        while time.time() < start_time + anti_collision_buffer_time:  # Wait some time collect data for Normal Messages
            msg = bus.recv(0.1)
            if msg is not None:
                normal_messages.add(msg.arbitration_id)

        del bus

        if len(normal_messages) == 0:
            logging.error("No Can Bus Activity Detected after {} seconds. \
                Is the network on and connected? Is this a gatewayed bus?".format(anti_collision_buffer_time))
            try:
                will_made_me_do_this = inputimeout(prompt='Would you like to continue?  ', timeout=10)
                if will_made_me_do_this in ['y', 'Y', '\n']:
                    pass
                else:
                    exit(-1)
            except TimeoutOccurred:
                pass

        message_length = 1 if message_length < 1 else message_length
        b_service_id = service_id.to_bytes(1, byteorder='big')
        b_message_length = message_length.to_bytes(1, byteorder='big')
        b_message_subfunctions = message_subfunctions.to_bytes(message_length - 1 if message_length > 1 else 1,
                                                               byteorder='big')
        b_padding = b'\x00' * (7 - message_length)
        payload = b_message_length + b_service_id + b_message_subfunctions + b_padding
        tx_msg = can.Message(arbitration_id=0, is_extended_id=False, data=payload, dlc=8)
        pairs_list = []

        for send_count, tx_arb_id in enumerate(range(arb_id_scan_low, arb_id_scan_high, scan_direction)):
            if tx_arb_id not in normal_messages:
                tx_msg.arbitration_id = tx_arb_id
                once_pairs_list = []
                twice_pairs_list = []

                try_t = 2 if try_twice else 1

                for tries in range(0, try_t):
                    logging.debug("send : {}".format(tx_msg))
                    bus2 = can.Bus(interface=self.can_interface, channel=self.socket_can_description, receive_own_messages=True)
                    start_time = time.time()
                    a = bus2.send(tx_msg)
                    print('****{} : {}******{}'.format(start_time, tx_msg, a))
                    for rx_message in bus2:
                        if rx_message.arbitration_id not in normal_messages:
                            print(rx_message)
                            if tries == 0:
                                once_pairs_list.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                                continue
                            elif tries == 1:
                                twice_pairs_list.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                                continue

                        if start_time + 0.5 < rx_message.timestamp:
                            break

                    del bus2
                    if try_twice is False:
                        twice_pairs_list = once_pairs_list

                common_pairs = self.common(once_pairs_list, twice_pairs_list)

                for pair in common_pairs:
                    if pair[0] == pair[1]:
                        common_pairs.remove(pair)

                if common_pairs:
                    pairs_list.append(common_pairs)

        self.nodes = pairs_list
        return pairs_list

    @staticmethod
    def _display_pair(arbitration_id, rx_arb_id):
        import logging

        result_info = "Response Pair Found: {:X} <--> {:X} (diff:{:05X})".format(arbitration_id, rx_arb_id,
                                                                                 arbitration_id - rx_arb_id)
        logging.debug(result_info)

    @staticmethod
    def common(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3
