# Example of displaying the device information service (DIS) info for a UART device.
#
# !!! NOTE !!!
#
# Only works on Mac OSX at this time.  On Linux bluez appears to hide the DIS
# service entirely. :(
#
# !!! NOTE !!!
#
# Author: Tony DiCola
import Adafruit_BluefruitLE
from Adafruit_BluefruitLE.services import UART, DeviceInformation
import time
import uuid

DEVICE_NAME="NIST BT test"
DEVICE_NAME="Empty Example"
service_uuid = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')
count_uuid   = uuid.UUID('292bd3d2-14ff-45ed-9343-55d125edb721')
rw_uuid      = uuid.UUID('56cd7757-5f47-4dcd-a787-07d648956068')
et_uuid      = uuid.UUID('7b183224-9168-443e-a927-7aeea07e8105')

# Get the BLE provider for the current platform.
ble = Adafruit_BluefruitLE.get_provider()

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
        print(len(devices))

        if len(devices) == 0:
            raise RuntimeError('Failed to find device!')
        return devices
    finally:
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
    devices = scan_for_peripheral(adapter)
    for peripheral in devices:
        try:
            print("peripheral: ", peripheral.name)
            peripheral.connect(timeout_sec=10)
            connected_to_peripheral = True
            test_iteration += 1
        except BaseException as e:
            print("Connection failed: " + str(e))
            time.sleep(1)
            print("Retrying...")
        # print(peripheral.list_services())
        print(peripheral.id)
        print(peripheral._peripheral.identifier())
        peripheral.discover([service_uuid], [count_uuid, rw_uuid])
        service = peripheral.find_service(service_uuid)
        count = service.find_characteristic(count_uuid)
        rw    = service.find_characteristic(rw_uuid)
        read_val = rw.read_value()
        print(service)
        # print(service, count, rw)
        print("rw: ", read_val)
        print("count: ", count.read_value())

# Initialize the BLE system.  MUST be called before other BLE calls!
ble.initialize()

# Start the mainloop to process BLE events, and run the provided function in
# a background thread.  When the provided main function stops running, returns
# an integer status code, or throws an error the program will exit.
ble.run_mainloop_with(main)
