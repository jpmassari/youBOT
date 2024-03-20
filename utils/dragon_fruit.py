import os
#TODO: #2 I don't like this solution. uninstall packages after finding a better one. #1Uninstall pynput
from pynput import mouse
import pyautogui
import time

#TODO: Verify in windows my proxy location to identify if dragonfruit in toggled on or off!
def connect_dragon():
    #if is up false, then add time for the application to load
    os.system('DragonFruit.OnionFruit.Windows')
    time.sleep(13)
    __toggle_dragon()
    time.sleep(6)
def __toggle_dragon():
    pyautogui.click(1880, 910)  # Example: Perform a click at the same position

def disconnect_dragon():
    #os.system('taskkill /F /IM DragonFruit.OnionFruit.Windows.exe')
    os.system('DragonFruit.OnionFruit.Windows') #pop up dragonfuit UI
    time.sleep(1)
    __toggle_dragon()
    time.sleep(6)