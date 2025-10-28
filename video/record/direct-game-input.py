# -*- coding: utf-8 -*-
# Direct Game Input - Advanced Windows API
# This script uses multiple Windows API methods to send input directly to games.
# Most effective for games that ignore regular automation.
# Requires 'keyboard' package. The script will attempt to install it if missing.
# Click the specific button automatically as much as you need

import subprocess
import sys

required = ["keyboard", "pywin32"]
missing = []

print("Checking required packages...")
for pkg in required:
    try:
        if pkg == "pywin32":
            # Special check for pywin32
            import win32gui
            print(f"[OK] {pkg} - Available")
        else:
            __import__(pkg)
            print(f"[OK] {pkg} - Available")
    except ImportError:
        print(f"[MISSING] {pkg} - Not found")
        missing.append(pkg)

# Install missing packages and restart
if missing:
    print(f"\nMissing packages: {missing}")
    print("Installing missing packages...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        print("[OK] Successfully installed missing packages.")
        print("Restarting script...")
        
        # Restart the script
        subprocess.check_call([sys.executable] + sys.argv)
        sys.exit(0)
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install packages: {e}")
        print("Please install packages manually:")
        for pkg in missing:
            print(f"  pip install {pkg}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error during installation: {e}")
        sys.exit(1)
else:
    print("All required packages are available.\n")

import time
import keyboard
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import threading
from datetime import datetime

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Virtual key codes
VK_RETURN = 0x0D
VK_SPACE = 0x20
VK_E = 0x45
VK_F = 0x46

class DirectGameInput:
    def __init__(self):
        self.running = False
        self.target_window = None
        self.interval = 5
        self.action_count = 0
        self.key_code = VK_RETURN
        self.debug = True
        
    def find_game_window(self, title):
        """Find game window"""
        def enum_windows_proc(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if title.lower() in window_title.lower() and window_title:
                    windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_proc, windows)
        return windows
    
    def send_input_method1(self):
        """Method 1: PostMessage"""
        try:
            win32api.PostMessage(self.target_window, win32con.WM_KEYDOWN, self.key_code, 0)
            time.sleep(0.05)
            win32api.PostMessage(self.target_window, win32con.WM_KEYUP, self.key_code, 0)
            if self.debug:
                print(f"[DEBUG] PostMessage sent (key: {self.key_code})")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] PostMessage failed: {e}")
            return False
    
    def send_input_method2(self):
        """Method 2: SendInput with focus"""
        try:
            # Force focus
            win32gui.SetForegroundWindow(self.target_window)
            win32gui.SetFocus(self.target_window)
            time.sleep(0.1)
            
            # Create INPUT structure for key press
            class INPUT(ctypes.Structure):
                class _INPUT(ctypes.Union):
                    class _ki(ctypes.Structure):
                        _fields_ = [("wVk", wintypes.WORD),
                                  ("wScan", wintypes.WORD),
                                  ("dwFlags", wintypes.DWORD),
                                  ("time", wintypes.DWORD),
                                  ("dwExtraInfo", ctypes.POINTER(wintypes.ULONG))]
                    _fields_ = [("ki", _ki)]
                _fields_ = [("type", wintypes.DWORD),
                          ("ii", _INPUT)]
            
            # Key down
            inp_down = INPUT()
            inp_down.type = 1  # INPUT_KEYBOARD
            inp_down.ii.ki.wVk = self.key_code
            inp_down.ii.ki.wScan = 0
            inp_down.ii.ki.dwFlags = 0
            inp_down.ii.ki.time = 0
            inp_down.ii.ki.dwExtraInfo = None
            
            # Key up
            inp_up = INPUT()
            inp_up.type = 1  # INPUT_KEYBOARD
            inp_up.ii.ki.wVk = self.key_code
            inp_up.ii.ki.wScan = 0
            inp_up.ii.ki.dwFlags = 2  # KEYEVENTF_KEYUP
            inp_up.ii.ki.time = 0
            inp_up.ii.ki.dwExtraInfo = None
            
            # Send input
            user32.SendInput(1, ctypes.byref(inp_down), ctypes.sizeof(INPUT))
            time.sleep(0.05)
            user32.SendInput(1, ctypes.byref(inp_up), ctypes.sizeof(INPUT))
            
            if self.debug:
                print(f"[DEBUG] SendInput sent (key: {self.key_code})")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] SendInput failed: {e}")
            return False
    
    def send_input_method3(self):
        """Method 3: SetKeyboardState manipulation"""
        try:
            # Get current keyboard state
            keyboard_state = (ctypes.c_ubyte * 256)()
            user32.GetKeyboardState(ctypes.byref(keyboard_state))
            
            # Set key as pressed
            keyboard_state[self.key_code] = 0x80
            user32.SetKeyboardState(ctypes.byref(keyboard_state))
            
            # Focus window
            win32gui.SetForegroundWindow(self.target_window)
            time.sleep(0.05)
            
            # Release key
            keyboard_state[self.key_code] = 0x00
            user32.SetKeyboardState(ctypes.byref(keyboard_state))
            
            if self.debug:
                print(f"[DEBUG] KeyboardState manipulation sent (key: {self.key_code})")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] KeyboardState manipulation failed: {e}")
            return False
    
    def send_input_method4(self):
        """Method 4: Multiple approaches combined"""
        try:
            # Method 4a: Focus and wait
            win32gui.SetForegroundWindow(self.target_window)
            win32gui.BringWindowToTop(self.target_window)
            time.sleep(0.2)
            
            # Method 4b: Try WM_CHAR message
            if self.key_code == VK_RETURN:
                win32api.SendMessage(self.target_window, win32con.WM_CHAR, 13, 0)  # CR
            elif self.key_code == VK_SPACE:
                win32api.SendMessage(self.target_window, win32con.WM_CHAR, 32, 0)  # Space
            else:
                win32api.SendMessage(self.target_window, win32con.WM_CHAR, self.key_code, 0)
            
            if self.debug:
                print(f"[DEBUG] Combined method sent (key: {self.key_code})")
            return True
        except Exception as e:
            if self.debug:
                print(f"[DEBUG] Combined method failed: {e}")
            return False
    
    def try_all_methods(self):
        """Try all input methods in sequence"""
        methods = [
            ("PostMessage", self.send_input_method1),
            ("SendInput", self.send_input_method2),
            ("KeyboardState", self.send_input_method3),
            ("Combined", self.send_input_method4)
        ]
        
        for method_name, method_func in methods:
            if self.debug:
                print(f"[DEBUG] Trying {method_name}...")
            if method_func():
                if self.debug:
                    print(f"[DEBUG] {method_name} succeeded")
                return True
            time.sleep(0.1)
        
        return False
    
    def action_loop(self):
        """Main action loop"""
        while self.running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                if self.try_all_methods():
                    self.action_count += 1
                    print("Currently running... Press 'ESC' to stop.")
                    print(f"[{current_time}] Action #{self.action_count} - Success")
                else:
                    print(f"[{current_time}] All methods failed")
                    print("Exiting due to repeated failures.")
                    time.sleep(5)
                    exit(1)
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error in action loop: {e}")
                time.sleep(1)
    
    def start(self, game_title, interval=5, key_code=VK_RETURN):
        """Start the direct input sender"""
        self.interval = interval
        self.key_code = key_code
        
        # Find game window
        windows = self.find_game_window(game_title)
        
        if not windows:
            print(f"Game window containing '{game_title}' not found!")
            return False
        
        if len(windows) > 1:
            print(f"Found {len(windows)} matching windows:")
            for i, (hwnd, title) in enumerate(windows):
                print(f"  {i+1}. {title}")
            
            try:
                choice = int(input("Select window (number): ")) - 1
                if 0 <= choice < len(windows):
                    self.target_window = windows[choice][0]
                    window_title = windows[choice][1]
                else:
                    self.target_window = windows[0][0]
                    window_title = windows[0][1]
            except ValueError:
                self.target_window = windows[0][0]
                window_title = windows[0][1]
        else:
            self.target_window = windows[0][0]
            window_title = windows[0][1]
        
        print(f"Target: {window_title}")
        print(f"Key code: {key_code}")
        print(f"Interval: {interval} seconds")
        print("This will try multiple Windows API methods")
        print("Press 'ESC' to stop\n")
        
        self.running = True
        
        # Start action loop
        action_thread = threading.Thread(target=self.action_loop, daemon=True)
        action_thread.start()
        
        return True
    
    def stop(self):
        """Stop the input sender"""
        self.running = False
        print(f"\nStopped! Total actions: {self.action_count}")

def main():
    print("=== Direct Game Input - Advanced Windows API ===")
    print("This uses multiple Windows API methods to send input directly to games")
    print("Most effective for games that ignore regular automation\n")
    
    # Get game title
    game_title = input("Enter a word in game window title (Example: Minecraft): ").strip()
    if not game_title:
        print("You need to enter a game title. Please try again.")
        return
    
    # Get interval
    try:
        interval = float(input("Please set interval in seconds (default 5): ").strip() or "5")
    except ValueError:
        interval = 5
    
    # Choose key
    print("\nChoose key to press automatically:")
    print("1. Enter (default)")
    print("2. Space")
    print("3. E")
    print("4. F")
    
    key_choice = input("Enter choice (1-4): ").strip()
    
    if key_choice == "2":
        key_code = VK_SPACE
        key_name = "Space"
    elif key_choice == "3":
        key_code = VK_E
        key_name = "E"
    elif key_choice == "4":
        key_code = VK_F
        key_name = "F"
    else:
        key_code = VK_RETURN
        key_name = "Enter"
    
    print(f"Selected key: {key_name}")
    
    sender = DirectGameInput()
    
    try:
        if sender.start(game_title, interval, key_code):
            # Wait for ESC
            while sender.running:
                if keyboard.is_pressed('esc'):
                    sender.stop()
                    break
                time.sleep(0.1)
    except KeyboardInterrupt:
        sender.stop()
    except Exception as e:
        print(f"Error: {e}")
        if sender.running:
            sender.stop()

if __name__ == "__main__":
    main()
