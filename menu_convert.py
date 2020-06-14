from consolemenu import *
from consolemenu.items import *
import glob
from convert_csv import bin2csv

def wrapper(fname):
    bin2csv(fname)
    print("-"*80)
    print(f"Finished converting {fname}")
    input("Press enter to continue")

def main():
    # Create the root menu
    menu = ConsoleMenu("Convert binary to csv", "")

    files = glob.glob('*.bin')
    files.sort()
    files = files[::-1]


    # Create a menu item that calls a function
    for fname in files:
        function_item = FunctionItem(fname, wrapper, [fname])
        menu.append_item(function_item)

    menu.start()
    menu.join()

main()
