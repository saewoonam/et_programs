import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import uuid

DEVICE_NAME="NIST BT test"
DEVICE_NAME="NIST-GEN"
# DEVICE_NAME="Empty Example"
service_uuid = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
count_uuid   = uuid.UUID('292bd3d2-14ff-45ed-9343-55d125edb721')
rw_uuid      = uuid.UUID('56cd7757-5f47-4dcd-a787-07d648956068')
spp_uuid     = uuid.UUID('4880c12c-fdcb-4077-8920-a450d7f9b907')
spp_data_uuid= uuid.UUID('fec26ec4-6d71-4442-9f81-55bc21d658d6')
et_uuid      = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

def scan_for_peripheral(adapter):
    """Scan for BLE peripheral and return device if found"""
    print('  Searching for device...')
    try:
        adapter.start_scan()
        # Scan for the peripheral (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        # device = ble.find_device(name=DEVICE_NAME)
        device = ble.find_device(service_uuids=[et_uuid])
        print(devices)
        if device is None:
            raise RuntimeError('Failed to find device!')
        # print(device.id, device.name)
        # print("rssi", device.rssi)
        return device
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

# Main function implements the program logic so it can run in a background
# thread.  Most platforms require the main thread to handle GUI events and other
# asyncronous events like BLE actions.  All of the threading logic is taken care
# of automatically though and you just need to provide a main function that uses
# the BLE provider.
def main():
    # Clear any cached data because both bluez and CoreBluetooth have issues with
    # caching data and it going stale.
    ble.clear_cached_data()

    # Get the first available BLE network adapter and make sure it's powered on.
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))
    # Disconnect any currently connected UART devices.  Good for cleaning up and
    # starting from a fresh state.
    print('Disconnecting any connected UART devices...')
    UART.disconnect_devices()

    print('Searching for device...')
    connected_to_peripheral = False
    test_iteration = 0
    while not connected_to_peripheral:
        try:
            print('-- iteration #{} --'.format(test_iteration))
            peripheral = scan_for_peripheral(adapter)
            print("peripheral: ", peripheral.name)
            peripheral.connect(timeout_sec=10)
            connected_to_peripheral = True
            test_iteration += 1
        except BaseException as e:
            print("Connection failed: " + str(e))
            time.sleep(1)
            print("Retrying...")
    if True:
        global total_len, done_xfer, data_service, out
        peripheral.discover([service_uuid], [count_uuid, rw_uuid, spp_data_uuid])
        service = peripheral.find_service(service_uuid)
        count = service.find_characteristic(count_uuid)
        rw    = service.find_characteristic(rw_uuid)
        data_service = service.find_characteristic(spp_data_uuid)
        read_val = rw.read_value()
        print(service, count, rw, spp_data_uuid)
        print("rw: ", read_val)
        msg = f"Hello from my mac.\r\n"
        data_service.write_value(msg.encode())
        # num_records = int.from_bytes(count.read_value(), byteorder='little')
        total_len = 0
        done_xfer = False
        out = b''
        def received(data):
            global total_len, done_xfer, data_service, out
            out += data
            packet_len = len(data)
            total_len += packet_len
            print(total_len, out.hex(), data.hex())
            # print('Received {0} bytes total {1}'.format(packet_len, total_len))
            if total_len >= 8:
                print("Done with xfer")
                data_service.stop_notify()
                done_xfer = True

        # Turn on notification of RX characteristics using the callback above.
        print('Subscribing to spp_data characteristic changes...')
        data_service.start_notify(received)
        print("Send command to fetch data")
        start = time.time()
        rw.write_value(b'A')

        while total_len<8:
            # print("not done", done_xfer, total_len)
            time.sleep(0)
        stop = time.time()
        ts = int.from_bytes(out[:4], byteorder='little')
        overflow = int.from_bytes(out[4:], byteorder='little')
        print("ts, overflow: ", ts, overflow)
        print(f"start, stop, dt: {start:.2f}, {stop:.2f}, {stop-start:.3f}")
        mean = (start+stop)/2
        epochtime = int(mean)
        delta = int((mean-epochtime)*1000)
        ts = ts-delta
        print("epoch, ts, ovflw", epochtime, ts, overflow)
        msg_out = epochtime.to_bytes(4, byteorder='little')
        msg_out += ts.to_bytes(4, byteorder='little')
        msg_out += overflow.to_bytes(4, byteorder='little')
        data_service.write_value(msg_out)
        print('msg+out', msg_out, msg_out.hex())
        rw.write_value(b'O')
        read_val = rw.read_value()
        print("rw: ", read_val)



# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
