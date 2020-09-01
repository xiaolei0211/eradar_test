def track_on(case_file, app_node, nm_node):
    import can
    import time
    bus = can.interface.Bus(bustype='kvaser', channel=0, bitrate=500000)
    file = open(case_file, 'r')
    start_flag = 1
    for line in file.readlines():
        #   判断有效节点
        line_list = line.split(' ')
        tx_frame_flag = line_list[1]
        if tx_frame_flag == '0':
            tx_time = line_list[(line_list.__len__()) - 2]
            tx_time = float(tx_time)
            if start_flag == 1:
                start_time = tx_time
                start_flag = 0
            tx_id = line[6:15]
            tx_id = int(tx_id, 16)
            if tx_id != app_node and tx_id != nm_node:
                tx_len = line[23:24]
                tx_len = int(tx_len)
                tx_data = line[26:26 + 2 * (2 * tx_len - 1)]
                tx_data = bytearray.fromhex(tx_data)
                tx_data = list(map(int, tx_data))
                msg = can.Message(arbitration_id=tx_id,
                                  data=tx_data,
                                  is_extended_id=False)
                bus.send(msg)
                time.sleep(tx_time - start_time)
                start_time = tx_time
            else:
                start_time = tx_time
    file.close()
