import argparse
import sys

from . import gst


def handle_dolphin(args):
    try:
        addr_gst_recorder_info_ptr: int = int(args.address, 0)
    except ValueError:
        print("Error! Address has an unknown number format!", file=sys.stderr)
        return

    print("Welcome to galaxygst! To find out how to set up the GST recorder in a galaxy, please refer to the GitHub\n"
          "repository's README file! If you want to cancel the tool's execution, press CTRL+C any time. To stop\n"
          "recording, press 2 on the first player's Wiimote!\n"
          "------------------------------------------------------------------------------")
    try:
        gst.record_gst_from_dolphin(args.output_folder_path, addr_gst_recorder_info_ptr)
    except KeyboardInterrupt:
        print("Execution canceled.")
    except RuntimeError as e:
        print(f"An error occurred: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Record GST object motion in SMG2 from Dolphin memory.")

    parser.add_argument("-address", nargs="?", default=f"0x{gst.ADDR_GST_RECORDER_INFO_PTR:08X}", help="address from which the tool retrieves GstRecordInfo*")
    parser.add_argument("output_folder_path", help="folder to save GST files to")
    parser.set_defaults(func=handle_dolphin)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
