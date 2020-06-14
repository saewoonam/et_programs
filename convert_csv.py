import numpy as np
# import matplotlib.pyplot as plt

import glob


def bin2csv(fname):
    rssi_dt = np.dtype([('mean',np.int8), ('n', np.int8), ('min', np.int8),
                        ('max', np.int8), ('var', np.int16)])
    dt = np.dtype([('rev_mac', 'V6'), ('first',np.int8), ('last', np.int8),
                   ('epoch_minute', np.uint32), ('id', 'V32'), ('rssi', rssi_dt, 3),
                   ('flag', np.uint8), ('flag1', np.uint8)])

    f = open(fname,'rb')
    line_count = 0
    last_mark = 0;
    while True:
        chunk = f.read(32)
        # print(chunk.hex().upper())
        marker = b'\x00'*32
        if chunk == marker:
            print(f'{line_count}:found marker')
            last_mark = line_count
        if len(chunk)==0:
            break;
        line_count += 1
    f.close()
    print('num 32 byte chunks: ', line_count)

    data = np.fromfile(fname, dtype=dt, offset=32*last_mark+64)
    bad = np.where(data['epoch_minute']==0)
    print("bad", bad[0])
    # data = data[:-2]
    data = np.delete(data, bad[0])

    datetime = [np.datetime64(int(d-6*3600), 's') for d  in data['epoch_minute'].astype(int)*60]
    f = open(fname+".csv", "w")
    header = "# time, epoch_time, first_sec, last_sec, mean37, n37, min37, max37, "
    header += "var37, mean38, n38, min38, max38, var38, mean39, n39, min39, max39, "
    header += "var39, crypto_flag, extra_flag, encounter_id\r\n"

    f.write(header)
    for idx in range(len(datetime)):
        msg = f"{datetime[idx]}, {data['epoch_minute'][idx]}, " 
        msg += f"{data['first'][idx]}, {data['last'][idx]}, "
        msg += data['rssi'][idx].__str__().replace(') (',
                                                ', ').replace('[(','').replace(')]',
                                                   '') + ', '
        msg += f"{data['flag'][idx]}, {data['flag1'][idx]}, "
        msg += f"{data['id'][idx].tobytes().hex().upper()}"
        f.write(msg+"\r\n")

    f.close()

if __name__ == '__main__':
    files = glob.glob('*.bin')
    files.sort()
    files = files[::-1]
    print(files)


    fname = files[0]

    bin2csv(fname)
