def diag_read_interpreter_sf_len(rx_data):
    read_len = int(rx_data[0:2]) - 3
    read_len = str(read_len)
    return read_len


def diag_read_interpreter_sf_data(rx_data):
    read_data_chr = ''
    read_len = int(rx_data[0:2]) - 3
    read_did = rx_data[6:8] + rx_data[9:11]
    for i in range(read_len):
        read_data = rx_data[12 + 3 * i:14 + 3 * i]
        read_data_chr = read_data_chr + read_data
    return read_data_chr


def diag_read_interpreter_sf_data_interpreter(rx_data):
    read_data_chr = ''
    read_len = int(rx_data[0:2], 16) - 3
    read_did = rx_data[6:8] + rx_data[9:11]
    for i in range(read_len):
        read_data = rx_data[12 + 3 * i:14 + 3 * i]
        read_data = int(read_data, 16)
        read_data = chr(read_data)
        read_data_chr = read_data_chr + read_data
    return read_data_chr


def diag_read_interpreter_ff_len(rx_data):
    read_len = int(rx_data[3:5], 16) - 3
    read_len = str(read_len)
    return read_len


def diag_read_interpreter_ff_data(rx_data):
    read_data_chr = ''
    read_len = 3
    read_did = rx_data[6:8] + rx_data[9:11]
    for i in range(read_len):
        read_data = rx_data[15 + 3 * i:17 + 3 * i]
        read_data_chr = read_data_chr + read_data
    return read_data_chr


def diag_read_interpreter_cf_data(rx_data, cf_len):
    read_data_chr = ''
    read_len = int(cf_len)
    for i in range(read_len):
        read_data = rx_data[3 + 3 * i:5 + 3 * i]
        read_data_chr = read_data_chr + read_data
    return read_data_chr


def diag_read_interpreter_cf_data_interpreter(rx_data):
    read_data_chr = ''
    cf_len = int(len(rx_data) / 2)
    for i in range(cf_len):
        read_data = rx_data[2 * i:2 * i + 2]
        read_data = int(read_data, 16)
        read_data = chr(read_data)
        read_data_chr = read_data_chr + read_data
    return read_data_chr


