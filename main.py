import signal
import sys
import subprocess
from web_driver import WebDriver
from channel_watcher import ChannelWatcher
from db.database_operations import get_all_mapped_channels
#TODO: check state of dragonfruit and disconnected in excpetion if its on
from utils.dragon_fruit import disconnect_dragon

def signal_handler(sig, frame):
    print("Ctrl + C pressed. Exiting gracefully...")
    try:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], check=True)
        print("Google Chrome process killed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    # Your cleanup code or additional handling here, if needed
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    mapped_channels = get_all_mapped_channels()
    filtered_dict = {}

    # Iterate over the original array
    for channel, my_channel in mapped_channels:
        if channel not in filtered_dict:
            # If the key doesn't exist in the dictionary, create a new list
            filtered_dict[channel] = [my_channel]
        else:
            # If the key already exists, append to the existing list
            filtered_dict[channel].append(my_channel)

    # Convert the dictionary items to a list of tuples
    result_array = [(key, value) for key, value in filtered_dict.items()]
    print("RESULT ARRAY: ", result_array)

    channelWatcher = ChannelWatcher(result_array)
    channelWatcher.start_monitoring()
    """ video = Youbot(driver, 'https://www.youtube.com/watch?v=zxjlkk7tl_A', 'German', 'translate', 'pt')
    video.process_video() """

if __name__ == "__main__":
    main()