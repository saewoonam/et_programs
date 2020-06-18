import Adafruit_BluefruitLE
import menu_info
import sys

if __name__ == '__main__':
    global g_number_to_find, g_command, ble

    g_command=b'w'
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)
    elif len(sys.argv) >= 2:
        g_number_to_find = int(sys.argv[1])

    # Get the BLE provider for the current platform.
    ble = Adafruit_BluefruitLE.get_provider()
    menu_info.ble = ble
    menu_info.g_number_to_find = g_number_to_find
    menu_info.g_command = g_command
    # Initialize the BLE system.  MUST be called before other BLE calls!
    ble.initialize()

    # Start the mainloop to process BLE events, and run the provided function in
    # a background thread.  When the provided main function stops running, returns
    # an integer status code, or throws an error the program will exit.
    ble.run_mainloop_with(menu_info.main)
