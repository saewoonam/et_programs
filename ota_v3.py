import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import uuid
import datetime

from consolemenu import *
from consolemenu.items import *

DEVICE_NAME="NIST-GEN"
service_uuid = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
count_uuid   = uuid.UUID('292bd3d2-14ff-45ed-9343-55d125edb721')
rw_uuid      = uuid.UUID('56cd7757-5f47-4dcd-a787-07d648956068')
spp_uuid     = uuid.UUID('4880c12c-fdcb-4077-8920-a450d7f9b907')
spp_data_uuid= uuid.UUID('fec26ec4-6d71-4442-9f81-55bc21d658d6')
et_uuid      = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

def scan_for_peripherals(adapter):
    """Scan for BLE peripheral and return device if found"""
    print('Searching for devices...')
    try:
        adapter.start_scan()
        # Scan for the peripheral (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        time.sleep(3)
        all_devices = ble.list_devices()
        devices = ble.find_devices(service_uuids=[et_uuid])
        if len(devices) == 0:
            raise RuntimeError('Failed to find  a device!')
        return devices
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
    # print('Disconnecting any connected UART devices...')
    # UART.disconnect_devices()

    devices = scan_for_peripherals(adapter)

    def download(peripheral):
        connected_to_peripheral = False
        test_iteration = 0
        try:
            print('-- iteration #{} --'.format(test_iteration))
            print("peripheral: ", peripheral.name)
            peripheral.connect(timeout_sec=10)
            connected_to_peripheral = True
            test_iteration += 1
        except BaseException as e:
            print("Connection failed: " + str(e))
            time.sleep(1)
            print("Retrying...")

        global total_len, done_xfer, data_service, fp_out, num_records
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
        num_records = int.from_bytes(count.read_value(), byteorder='little')
        num_chunks = num_records*32 / 240
        if (num_records*32)%240 == 0:
            num_chunks -= 1
        print("num_32byte_records, num bytes, num_chunks to fetch: ", num_records, num_records*32,
              num_chunks)
        total_len = 0
        done_xfer = False
        if num_records==0:
            done_xfer = True
        else:
            date_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            fp_out = open('raw_'+date_suffix+'.bin', 'wb')
        print('*'*40)
        start=time.time()
        def received(data):
            # print("Trying to receive")
            global total_len, done_xfer, data_service, fp_out, num_records
            packet_len = len(data) - 4
            total_len += packet_len
            if packet_len>0:
                fp_out.write(data[4:])
            # fp_out.flush()

            # print(data.hex())
            idx = int.from_bytes(data[:4], byteorder='little')
            # print('got idx: ', idx)
            print(f'\ridx: {idx} packet_len:{packet_len} received:{total_len} / {num_records*32}', end='')
            # check if done
            if total_len == (num_records<<5):
                print("\nDone with xfer")
                data_service.stop_notify()
                fp_out.close()
                done_xfer = True
            else:
                # not done, request next packet
                get_idx = idx+1
                # print('send get_idx: ', get_idx, get_idx.to_bytes(4, byteorder='little'))
                data_service.write_value(get_idx.to_bytes(4, byteorder='little'))

        # Turn on notification of RX characteristics using the callback above.
        print('Subscribing to spp_data characteristic changes...')
        data_service.start_notify(received)
        print("Send command to fetch data")
        rw.write_value(b'f')
        get_idx = 0
        data_service.write_value(get_idx.to_bytes(4, byteorder='little'))
        last = 0
        while (not done_xfer):
            time.sleep(1)
        stop = time.time()
        print(f'dt: {stop-start}')
        rw.write_value(b'F')
        peripheral.disconnect()

    def m(devices):
        # Create the root menu
        menu = ConsoleMenu("Bluetooth Devices Menu", "")
        def item_func(peripheral):
            download(peripheral)
            input("Press Enter to continue.")

        # Create a menu item that calls a function
        for peripheral in devices:
            item_name = peripheral.name + ': ' + str(peripheral.id)
            function_item = FunctionItem(item_name, item_func, [peripheral])
            menu.append_item(function_item)

        menu.start()
        menu.join()
    m(devices)
    # for peripheral in devices:
    #     download(peripheral)
    return
# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
