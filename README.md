# cmap
Hardware:
* Socket CAN Enabled Device
* ISO-TP Installed on Device (https://github.com/hartkopp/can-isotp-modules)

Python Requirements:
* python-can (https://python-can.readthedocs.io/en/master/installation.html)
* can-isotp (https://pypi.org/project/can-isotp/)

Practical Requirements:
* A hatred of vehicles
* Love for fellow man-kind

Class Information:
`// net_can_bus.py::NetworkCanBus(socket_can_desciption, can_interface, bitrate, nodes)::scan_for_uds_ids(scan_service_id, anti_collision_buffer_time, message_length, message_subfunctions, arb_id_scan_low, arb_id_scan_high, scan_direction, try_twice, prompt_wait_timeout) --`
This bad boy can scan a CAN Bus real quick-like.  So fast that you might not know it happened.  (Ok a little bit exagerated.)  But it will return a list of Nodes "Pairs".  These "Pairs" are the [Request_ID, Response_ID] of the node.  So if you send a node a "Request_ID" it will Respond using the, that's right you guessed it, "Response ID".

Ojbect Instantiation;
* "socket_can_description", just leave this as 'can0' unless of course it's not can0 you want to talk on.
* "can_interface". Don't mess with this one k.
* "bitrate" is the rate at which the bits do things on the bus.  500,000Kbps is default
* "nodes" is the list of node pairs associated with this network.  After a scan, you'll see things here.

[scan_for_uds_ids] A little info on the inputs for this method,
* "scan_service_id" is the 1 byte Service ID that you want to send (recommended default of 0x3E).
* "anti_collision_buffer_time" is the time we wait and listen and reflect on our life choices while also listening to the CAN Bus to see what IDs are on the bus.  We'll make a list of these IDs and not send requests using these IDs as that can cause odd effects on the vehicle itself. Like for instance, once I had the car start just because I sent a message.  Like start right up, crazy.  So we should try to avoid using existing IDs.
* "message_length" is the size of the message (not the size of the CAN Frame) that we are going to send.  This is typically 1 Byte (just the service ID) but some controllers are like, pish one byte is too few bytes.  So this lets you set a larger message size if you want.  We default at 2 Bytes.  Seems to work best.
* message_subfunctions". Services are like functions, subfunctions are the data bytes the go after the service ID.  This so if you do send more than 1 byte in your message you may want to change this from 0x00 (or not)
* "arb_id_scan_low" is a first Arbitration ID we're going to try.  Well not *we* the program.  Its going to try.  You're not doing anything really.
* "arb_id_scan_high" is the last Arbitration ID (minus one) that will be tried.
* "scan_direction" is the direction and step that we will increment the ID.  This can be 1 (increment by 1 from low ID to high ID) or -1 (decrement by 1) or any signed integer.  But keep it low.  Default is 1, that's good.
* "try_twice".  We're going to scan the bus.  We are esstentially sending a message and waiting for a new message to arrive, but sometimes the "new" message is just an old message that we didn't see before, so with try_twice we can try to send a message two times and if we get the same response twice then we can filter out this noisy sob.
* "prompt_wait_timeout".  Sometimes the bus has no traffic on it Normally.  This is ok, but sometimes it should have traffic but you forgot how to connect hardware to wires.  Yeah you know who you are.  So I put a little promt there to let you know the bus is quite, and ask you if you want to continue.  But you may be afk. So why not give you an opportunity to just ignore this prompt altogether, thus this handy little input. P.S. Will made me do it.


Class Information:
`// uds_node.py::UDSNode(physical_request_id, response_id, functional_request_id, socket_can_interface, start_service_id, end_service_id, enhanced_mode_session_byte)::find_services(skip_response_only_service_ids, scan_only_known_uds_services, payload_extra_byte, add_extra_payload_byte)`

Object Instantiation;
* "physical_request_id" is the Arbitration ID we'll use to send the data
* "response_id" is the Arbitration ID we'll received the response (hopefully)
* "functional_request_id" was a dumb idea.  I don't even use that anymore. Forget you even saw it.
* "socket_can_interface" is the 'can0' or "canX" that you are connected to.
* "start_service_id" first ID to scan.
* "end_service_id" last ID to scan (inclusive).
* "enhanced_mode_session_byte".  Sometime in the near future we will want to do a better job of what session we are in when scanning services.  The session byte will be important, but right now.  We don't care.

[find_services] A little info on this method,
* "skip_response_only_service_ids". Many service IDs are designated as response IDs and should only be used for this purpose.  So we can speed up our scan a lot by only scanning for valid service IDs.  But of course, if your goal is to find things that are INVALID, then don't skip anything.
* "scan_only_known_uds_services".  Similar to skip_response_only... this will be even faster and only send requests for known service IDs.
* "payload_extra_byte" is for those pesky services that need more data than what I thought they would need.
* "add_extra_payload_byte" is the on/off switch to send the extra byte. Off is default.


Class Information:
`// services.py::Services(request_phyiscal_id, response_id, service_id, subfunction_length, padding_byte, protocol, socketcan_interface, can_scan_timeout, extra_data_field, extra_data_field_byte_string, scan_increment_step).find_service_subfunctions()`

Objection Instantiation;
* "request_phyiscal_id" yeah this is the same thing as UDSNode's phyiscal_request_id.  Just rearanged the order of the words to confuse you.
* "response_id" same thing as UDSNode.
* "service_id" is the service ID we are scanning
* "subfunction_length" is the size of the subfunction.  This is typically automoatic, but you can override it if you wish.
* "padding_byte" is the padding byte we'll use to send with the data. (obvs. sorry but this is getting boring a bit).
* "protocol".  Later we'll want to support other diagnostic protocols, so this is placeholder for that. 0 is default.
* "socketcan_interface" = 'can0'
* "can_scan_timeout" is the timeout we'll wait for a response back from a controller.  Its really not working right now. So .. yeah.. not that useful.
* "extra_data_field" is the extra byte in the data field for some services to be happy.
* "extra_data_fiel_byte_string" this is a byte or bytestring that you want to put in the extra data field.
* "scan_increment_step". Some services work better when you decrement.  Some services you should both increment and decrement.  This give you the ability to do this.

[find_service_subfunctions] has no inputs.  You're welcome.
