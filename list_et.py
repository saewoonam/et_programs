import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import uuid
import sys

DEVICE_NAME="NIST BT test"
DEVICE_NAME="NIST-GEN"
# DEVICE_NAME="Empty Example"
service_uuid = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
count_uuid   = uuid.UUID('292bd3d2-14ff-45ed-9343-55d125edb721')
rw_uuid      = uuid.UUID('56cd7757-5f47-4dcd-a787-07d648956068')
et_uuid      = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
data_uuid    = uuid.UUID('fec26ec4-6d71-4442-9f81-55bc21d658d6')
dev_info_uuid= uuid.UUID('0000180A-0000-1000-8000-00805F9B34FB')
id_uuid      = uuid.UUID('00002A23-0000-1000-8000-00805F9B34FB')
gen_access_uuid = uuid.UUID('00001800-0000-1000-8000-00805F9B34FB')
dev_name_uuid   = uuid.UUID('00002A00-0000-1000-8000-00805F9B34FB')
# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()
# ble.initialize()
# ble.clear_cached_data()
#
# # Get the first available BLE network adapter and make sure it's powered on.
# adapter = ble.get_default_adapter()
# adapter.power_on()
# adapter.start_scan()
# # Scan for the peripheral (will time out after 60 seconds
# # but you can specify an optional timeout_sec parameter to change it).
# # device = ble.find_device(name=DEVICE_NAME)
# device = ble.find_device(service_uuids=[et_uuid])

if len(sys.argv)>=2:
    number_to_find = int(sys.argv[1])
else:
    number_to_find = 4
def scan_for_peripherals(adapter, num=4):
    """Scan for BLE peripheral and return device if found"""
    # try:
    #     adapter.start_scan()
    #     time.sleep(4)
    #     all_devices = ble.list_devices()
    #     devices = ble.find_devices(service_uuids=[et_uuid])
    #     if len(devices) == 0:
    #         raise RuntimeError('Failed to find  a device!')
    #     else:
    #         print(f"Found {len(all_devices)} bluetooth devices ")
    #     return devices
    # finally:
    #     # Make sure scanning is stopped before exiting.
    #     adapter.stop_scan()
    all_found = False
    while not all_found:
        try:
            adapter.start_scan()
            # Scan for the peripheral (will time out after 60 seconds
            # but you can specify an optional timeout_sec parameter to change it).
            time.sleep(3)
            all_devices = ble.list_devices()
            devices = ble.find_devices(service_uuids=[et_uuid])
            if len(devices) == 0:
                raise RuntimeError('Failed to find  a device!')
            if (len(devices)>=num):
                all_found = True
                return devices
            print(f"found {len(devices)}/{num}")
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

    print('Searching for devices...')
    connected_to_peripheral = False
    devices = scan_for_peripherals(adapter, number_to_find)
    loop_count = 0
    print(f"Found {len(devices)} NIST encounter tracing devices ")
    for peripheral in devices:
        print("peripheral: ", peripheral.name)

        # peripheral.connect(timeout_sec=10)
        # print("connected", peripheral.is_connected)
        if False:
            print("advertised", peripheral.advertised)
            peripheral.discover([service_uuid], [count_uuid, rw_uuid, data_uuid])
            service = peripheral.find_service(service_uuid)
            count = service.find_characteristic(count_uuid)
            rw    = service.find_characteristic(rw_uuid)
            data  = service.find_characteristic(data_uuid)
        if False:
            new_name = 'NIST%04d'%loop_count
            new_name = new_name.encode()
            print(f"new name: {new_name}")
            # print('data', data)
            data.write_value(new_name)
            rw.write_value(b'N')
            print(rw.read_value());
            loop_count += 1
        if False:
            peripheral.discover([dev_info_uuid], [id_uuid ])
            dev_info = peripheral.find_service(dev_info_uuid)
            print("dev_info", dev_info)
          
        if False:  #  this uuid is not available/advertised...
            peripheral.discover([gen_access_uuid], [dev_name_uuid])
            gen_access = peripheral.find_service(gen_access_uuid)
            print("gen_access", gen_access)
        # services = peripheral.list_services()
        # for s in services:
        #     print(s.__dict__)
        # dev_name_char = gen_access.find_characteristic(dev_name_uuid)
        # serial_num = dev_name_char.read_value()
        # print(s)
        # dev_name_char.write_value(b'0'*8)
        # serial_num = dev_name_char.read_value()
        # s = bytes(serial_num)
        # print(s.hex())
        # print(peripheral.list_services())

# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
