import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import uuid

from consolemenu import *
from consolemenu.items import *

DEVICE_NAME="NIST BT test"
DEVICE_NAME="Empty Example"
service_uuid = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
count_uuid   = uuid.UUID('292bd3d2-14ff-45ed-9343-55d125edb721')
rw_uuid      = uuid.UUID('56cd7757-5f47-4dcd-a787-07d648956068')
et_uuid      = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
# spp_uuid     = uuid.UUID('4880c12c-fdcb-4077-8920-a450d7f9b907')
spp_data_uuid= uuid.UUID('fec26ec4-6d71-4442-9f81-55bc21d658d6')

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
global menu

def item_func(peripheral, override=None):
    global total_len, done_xfer, data_service, out
    service = peripheral.find_service(service_uuid)
    count = service.find_characteristic(count_uuid)
    rw    = service.find_characteristic(rw_uuid)
    data_service = service.find_characteristic(spp_data_uuid)
    rw.write_value(b's')
    count_raw = int.from_bytes(count.read_value(), byteorder='little')
    print(f"count: {count_raw}")
    total_len = 0

    done_xfer = False
    out = b''
    def received(data):
        global total_len, done_xfer, data_service, out
        out += data
        packet_len = len(data)
        total_len += packet_len
        # print(total_len, out.hex(), data.hex())
        # print('Received {0} bytes total {1}'.format(packet_len, total_len))
        if total_len >= 1:
            # print("Done with xfer")
            data_service.stop_notify()
            done_xfer = True

    # Turn on notification of RX characteristics using the callback above.
    data_service.start_notify(received)
    # print("Send command to fetch info/status")
    rw.write_value(b'I')
    read_val = rw.read_value()
    # print('rw.read_value()', rw.read_value())
    while not done_xfer:
        # print('waiting')
        time.sleep(0.1)
    print(type(out))
    print(out)
    if out == b'\x00':
        write = f"OFF"
    elif out == b'\x01':
        write = f"ON"
    else:
        write =f"{out.hex()}"

    if override is None:
        selected = menu.selected_option
        menu.items[selected].text = f"{peripheral.name}: rw:{read_val} count:{count_raw} write:{write}"
        menu.epilogue_text = "Last result: " + menu.items[selected].text
    else:
        menu.items[override].text = f"{peripheral.name}: rw:{read_val} count:{count_raw} write:{write}"
    # print(menu.__dict__)
    # input("Press Enter to continue.")

def all_item_func(devices):
    for idx, k in enumerate(devices.keys()):
        peripheral = devices[k]
        item_func(peripheral, idx)

def m(devices):
    # Create the root menu
    global menu
    menu = ConsoleMenu("Bluetooth Gadget Stop writing to flash Menu", "")
    # Create a menu item that calls a function
    # for peripheral in devices:
    for k in devices.keys():
        peripheral = devices[k]
        item_name = peripheral.name + ': ' + str(peripheral.id)
        function_item = FunctionItem(item_name, item_func, [peripheral])
        menu.append_item(function_item)
    function_item = FunctionItem('All', all_item_func, [devices])
    menu.append_item(function_item)

    menu.start()
    menu.join()

def scan_for_peripheral(adapter):
    """Scan for BLE peripheral and return device if found"""
    try:
        adapter.start_scan()
        # Scan for the peripheral (will time out after 60 seconds
        # but you can specify an optional timeout_sec parameter to change it).
        # device = ble.find_device(name=DEVICE_NAME)
        # device = ble.find_device(service_uuids=[spp_uuid])
        time.sleep(5)
        all_devices = ble.list_devices()
        devices = ble.find_devices(service_uuids=[service_uuid])
        conn = {}
        for peripheral in devices:
            connected = False
            while not connected:
                try:
                    print("peripheral: ", peripheral.name, flush=True)
                    peripheral.connect(timeout_sec=10)
                    connected = True

                except BaseException as e:
                    print("Connection failed: " + str(e))
                    time.sleep(1)
                    print("Retrying...")
            conn[peripheral.name] = peripheral

        if len(devices) == 0:
            raise RuntimeError('Failed to find device!')
    finally:
        adapter.stop_scan()
    return conn

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

    print('Searching for device...')
    connected_to_peripheral = False
    test_iteration = 0
    conn = scan_for_peripheral(adapter)

    for k in conn.keys():
        print(k, conn[k])

    m(conn)
    # for peripheral in devices:
    #     try:
    #         print("peripheral: ", peripheral.name)
    #         peripheral.connect(timeout_sec=10)
    #         connected_to_peripheral = True
    #         test_iteration += 1
    #     except BaseException as e:
    #         print("Connection failed: " + str(e))
    #         time.sleep(1)
    #         print("Retrying...")
    #     # print(peripheral.list_services())
    #     # print(peripheral.id)
    #     # print(peripheral._peripheral.identifier())
    #     peripheral.discover([service_uuid], [count_uuid, rw_uuid, spp_data_uuid])
    #     service = peripheral.find_service(service_uuid)
    #     count = service.find_characteristic(count_uuid)
    #     rw    = service.find_characteristic(rw_uuid)
    #     data_service = service.find_characteristic(spp_data_uuid)
    #     read_val = rw.read_value()
    #     # print(service)
    #     # print(service, count, rw)
    #     print("rw: ", read_val)
    #     count_raw = int.from_bytes(count.read_value(), byteorder='little')
    #     print("count: ", count_raw)
    #
    #     rw.write_value(b'w')
    #     print('rw.read_value()', rw.read_value())

# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
