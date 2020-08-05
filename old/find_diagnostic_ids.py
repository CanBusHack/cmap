#! /usr/bin/python3

import can
import threading
import time
from inputimeout import inputimeout, TimeoutOccurred


def send_message(bus, message, time_between_messages=0.01):
    bus.send(message)
    time.sleep(time_between_messages)
    bus.send(message)
    time.sleep(time_between_messages)


def send_ping(can_socket, arbitration_id, diagnostic_payload, arb_ids_to_ignore_when_scanning, can_scan_timeout):
    can_socket.SendCAN(arbitration_id, 8, diagnostic_payload)
    messages = can_socket.FilteredRxCAN(arb_ids_to_ignore_when_scanning, arbitration_id, can_scan_timeout)
    return messages


def output_information(information, mode):
    if mode:
        print(information)


def display_pair(arbitration_id, rx_arb_id, verbose_mode):
    result_info = "Response Pair Found: {:X} <--> {:X} (diff:{:05X})".format(arbitration_id, rx_arb_id,
                                                                             arbitration_id - rx_arb_id)
    output_information(result_info, verbose_mode)


def count_u(arb_list):
    count = 0
    for things in arb_list:
        if things == -1:
            count += 1

    print("Found {} Arb IDs to Avoid.".format(count))
    return True


def scan_for_ids(can_socket,
                 arb_id_scan_low=0,
                 arb_id_scan_high=0x7FF,
                 can_scan_timeout=0.1,
                 scan_direction=1,
                 anti_collision_buffer_time=5,
                 service_id=0x3E,
                 message_length=2,
                 message_subfunctions=0,
                 extended_frames=False,
                 try_twice=False,
                 verbose_mode=False
                 ):
    bus = can.Bus(interface='socketcan', channel=can_socket, receive_own_messages=False)

    output_information("Listening for Current Arb IDs So we Don't Clobber Them!...", verbose_mode)
    normal_messages = set([])

    start_time = time.time()
    while time.time() < start_time + anti_collision_buffer_time:  # Wait some time collect data for Normal Messages
        msg = bus.recv(0.1)
        if msg is not None:
            normal_messages.add(msg.arbitration_id)

    if len(normal_messages) == 0:
        print("No Can Bus Activity Detected after {} seconds. \
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
    payload = b_message_length + b_service_id + b_message_subfunctions
    tx_msg = can.Message(arbitration_id=0, is_extended_id=False, data=payload, dlc=8)
    pairs_list = []

    for send_count, tx_arb_id in enumerate(range(arb_id_scan_low, arb_id_scan_high, scan_direction)):
        if tx_arb_id not in normal_messages:
            tx_msg.arbitration_id = tx_arb_id
            once_pairs_list = []
            twice_pairs_list = []
            received_messages_try_1 = set([])
            received_messages_try_2 = set([])

            try_t = 2 if try_twice else 1

            for tries in range(0, try_t):
                daig_messages = set([])
                print("send : {}".format(tx_msg))
                start_time = time.time()
                send_message(bus, tx_msg)
                for rx_message in bus:
                    if False:  # verbose_mode:
                        print(rx_message)
                    if tries == 0:
                        received_messages_try_1.add(rx_message.arbitration_id)
                        if rx_message.arbitration_id not in normal_messages \
                                and rx_message.arbitration_id not in daig_messages \
                                and rx_message.arbitration_id != tx_msg.arbitration_id:
                            once_pairs_list.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                            daig_messages.add(rx_message.arbitration_id)
                            print("recv0: {}".format(rx_message))
                            break
                    else:
                        received_messages_try_2.add(rx_message.arbitration_id)
                        if rx_message.arbitration_id not in normal_messages and rx_message.arbitration_id != tx_msg.arbitration_id:
                            twice_pairs_list.append([tx_msg.arbitration_id, rx_message.arbitration_id])
                            normal_messages.add(rx_message.arbitration_id)
                            print("recv1: {}".format(rx_message))
                            break

                    if send_count == 0:  # The first time we itterate through bus messages the rx is FULL so we need to wait longer
                        if start_time + 1.2 > time.time():  # TODO: Test THIS!!!
                            continue
                        else:
                            break
                    else:
                        if start_time + 0.1 > time.time():
                            continue
                        else:
                            break

            if try_twice:
                for pair in once_pairs_list:
                    if pair in twice_pairs_list:
                        pairs_list.append(pair)
                        display_pair(pair[0], pair[1], verbose_mode)

            else:
                try:
                    if once_pairs_list:
                        pairs_list.append(once_pairs_list)
                        display_pair(once_pairs_list[0][0], once_pairs_list[0][1], verbose_mode)
                except IndexError as e:
                    print('No Pairs Found')
        else:
            print("Skipping ID: {:03X} // this id is in the normal mode message list".format(tx_arb_id))

    return pairs_list
