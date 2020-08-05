class NetworkCanBus:
    socket_can_description = None
    can_interface = None
    bitrate = None
    nodes = None

    _is_quite_bus = False
    _noise_message_arb_id = 0x7FF
    _noise_message_payload = b'\xde\xad\xbe\xef\x04\xf1\xd0\x00'
    _noise_message_period = 0.1
    _stop_threading = False

    def __init__(self,
                 socket_can_description='can0',
                 can_interface='socketcan',
                 bitrate=500000,
                 nodes=None):

        self.socket_can_description = socket_can_description
        self.can_interface = can_interface
        self.bitrate = bitrate
        self.nodes = nodes

    def scan_for_uds_ids(self,
                         scan_service_id=0x3E,
                         anti_collision_buffer_time=6,  # Time in seconds to listen to the bus
                         message_length=2,
                         message_subfunctions=0,
                         arb_id_scan_low=0,
                         arb_id_scan_high=0x7FF,
                         scan_direction=1,
                         try_twice=True,
                         prompt_wait_timeout=10
                         ):

        import can
        import logging
        import time
        from inputimeout import inputimeout, TimeoutOccurred

        common_pairs = []

        bus = can.Bus(interface=self.can_interface, channel=self.socket_can_description, receive_own_messages=True)

        logging.info("Listening for Current Arb IDs So we Don't Clobber Them!...")
        normal_messages = set([])  # set of message IDs that we will filter out when listing to the bus later

        start_time = time.time()
        while time.time() < start_time + anti_collision_buffer_time:  # Wait some time collect data for Normal Messages
            msg = bus.recv(0.1)
            if msg is not None:
                normal_messages.add(msg.arbitration_id)

        del bus  # need a way to flush the CAN Bus Buffer.  This Seems to work.

        if len(normal_messages) == 0:
            self._is_quite_bus = True
            logging.error("No Can Bus Activity Detected after {} seconds. \
                Is the network on and connected? Is this a gatewayed bus?".format(anti_collision_buffer_time))
            try:
                will_made_me_do_this = inputimeout(prompt='Would you like to continue?  ', timeout=prompt_wait_timeout)
                if will_made_me_do_this in ['y', 'Y', '\n']:
                    pass
                else:
                    exit(-1)
            except TimeoutOccurred:
                pass

        message_length = 1 if message_length < 1 else message_length
        payload_service_id = scan_service_id.to_bytes(1, byteorder='big')
        payload_message_length = message_length.to_bytes(1, byteorder='big')
        payload_message_subfunction = message_subfunctions.to_bytes(message_length - 1 if message_length > 1 else 1,
                                                                    byteorder='big')
        payload_padding_bytes = b'\x00' * (7 - message_length)
        payload = payload_message_length + payload_service_id + payload_message_subfunction + payload_padding_bytes
        tx_msg = can.Message(arbitration_id=0, is_extended_id=False, data=payload, dlc=8)
        pairs_list = []

        if self._is_quite_bus:
            self._create_noise()  # CAN Socket needs some noise to receive data.

        for send_count, tx_arb_id in enumerate(range(arb_id_scan_low, arb_id_scan_high, scan_direction)):
            if tx_arb_id not in normal_messages:  # anti-collision
                tx_msg.arbitration_id = tx_arb_id
                first_pairs = []
                second_pairs = []

                tries = 2 if try_twice else 1

                for tries in range(0, tries):
                    logging.debug("send : {}".format(tx_msg))
                    bus2 = can.Bus(interface=self.can_interface,
                                   channel=self.socket_can_description,
                                   receive_own_messages=False)
                    start_time = time.time()
                    a = bus2.send(tx_msg)
                    logging.info('****{} : {}******{}'.format(start_time, tx_msg, a))

                    for rx_message in bus2:
                        if start_time + 0.05 < rx_message.timestamp:
                            break
                        if rx_message.arbitration_id not in normal_messages \
                                and rx_message.arbitration_id != tx_arb_id \
                                and rx_message.data != self._noise_message_payload \
                                and (rx_message.arbitration_id != 0x000 and rx_message.dlc != 4):  # Not an Error Frame
                            logging.info(rx_message)
                            if tries == 0:
                                first_pairs.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                                continue
                            elif tries == 1:
                                second_pairs.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                                continue

                    del bus2

                    if try_twice is False:
                        common_pairs = first_pairs
                    else:
                        common_pairs = self._common(first_pairs, second_pairs)

            for pair in common_pairs:
                if pair[0] == pair[1]:  # if the IDs match then this pair should be removed.
                    common_pairs.remove(pair)

            if common_pairs:
                pairs_list.append(common_pairs)

        self.nodes = pairs_list
        self._stop_threading = True
        return pairs_list

    @staticmethod
    def _display_pair(arbitration_id, rx_arb_id):
        import logging
        result_info = "Response Pair Found: {:X} <--> {:X} (diff:{:05X})".format(arbitration_id, rx_arb_id,
                                                                                 arbitration_id - rx_arb_id)
        logging.debug(result_info)

    @staticmethod
    def _common(lst1, lst2):
        lst3 = [value for value in lst1 if value in lst2]
        return lst3

    def _create_noise(self):
        import threading
        t = threading.Thread(name='_thread_worker', target=self._thread_worker)
        t.start()
        return 0

    def _thread_worker(self):
        import can
        import time

        work = can.Bus(interface=self.can_interface, channel=self.socket_can_description, receive_own_messages=True)
        payload = self._noise_message_payload
        tx_msg = can.Message(arbitration_id=self._noise_message_arb_id,
                             is_extended_id=False,
                             data=payload,
                             dlc=len(payload))
        while not self._stop_threading:
            work.send(tx_msg)
            time.sleep(self._noise_message_period)
