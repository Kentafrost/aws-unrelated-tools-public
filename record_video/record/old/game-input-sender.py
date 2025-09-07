import time
import pyautogui
import threading
import keyboard
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes
from datetime import datetime

# Windows API constants
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_CHAR = 0x0102

class GameInputSender:
    def __init__(self):
        self.running = False
        self.game_title = ""
        self.interval = 5
        self.target_window = None
        self.action_count = 0
        self.debug_mode = True
        self.action_type = "key"  # key, click, message
        self.key_code = 0x0D  # Enter key
        self.use_direct_input = True
        
    def find_game_window(self, game_title):
        """Find window by title (partial match)"""
        def enum_windows_proc(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if game_title.lower() in window_title.lower() and window_title:
                    windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_proc, windows)
        return windows
    
    def send_key_message(self, hwnd, key_code):
        """Send key message directly to window using Windows messages"""
        try:
            # Send WM_KEYDOWN
            win32api.SendMessage(hwnd, WM_KEYDOWN, key_code, 0)
            time.sleep(0.05)
            # Send WM_KEYUP
            win32api.SendMessage(hwnd, WM_KEYUP, key_code, 0)
            
            if self.debug_mode:
                print(f"[DEBUG] Sent key message (code: {key_code}) to window")
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error sending key message: {e}")
            return False
    
    def send_click_message(self, hwnd, x, y):
        """Send mouse click message directly to window"""
        try:
            # Calculate relative coordinates within window
            rect = win32gui.GetWindowRect(hwnd)
            rel_x = x - rect[0]
            rel_y = y - rect[1]
            
            # Create lParam for mouse position
            lParam = win32api.MAKELONG(rel_x, rel_y)
            
            # Send mouse down and up messages
            win32api.SendMessage(hwnd, WM_LBUTTONDOWN, 1, lParam)
            time.sleep(0.05)
            win32api.SendMessage(hwnd, WM_LBUTTONUP, 0, lParam)
            
            if self.debug_mode:
                print(f"[DEBUG] Sent click message to window at ({rel_x}, {rel_y})")
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error sending click message: {e}")
            return False
    
    def get_window_center(self, hwnd):
        """Get the center coordinates of a window"""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x = (rect[0] + rect[2]) // 2
            y = (rect[1] + rect[3]) // 2
            return (x, y)
        except:
            return None
    
    def focus_window(self, hwnd):
        """Bring window to foreground and focus"""
        try:
            # Check if minimized and restore
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
            
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)
            
            # Verify focus
            focused = win32gui.GetForegroundWindow()
            success = focused == hwnd
            
            if self.debug_mode:
                print(f"[DEBUG] Focus window - Success: {success}")
            
            return success
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error focusing window: {e}")
            return False
    
    def perform_action(self):
        """Perform the configured action"""
        if not self.target_window or not win32gui.IsWindow(self.target_window):
            print("Target window not found or invalid")
            return False
        
        try:
            if self.action_type == "message_key":
                # Send key via Windows message
                return self.send_key_message(self.target_window, self.key_code)
            
            elif self.action_type == "message_click":
                # Send click via Windows message
                center = self.get_window_center(self.target_window)
                if center:
                    return self.send_click_message(self.target_window, center[0], center[1])
                return False
            
            elif self.action_type == "focus_key":
                # Focus window then send key
                if self.focus_window(self.target_window):
                    time.sleep(0.1)
                    if self.key_code == 0x0D:  # Enter
                        pyautogui.press('enter')
                    elif self.key_code == 0x20:  # Space
                        pyautogui.press('space')
                    elif self.key_code == 0x45:  # E
                        pyautogui.press('e')
                    elif self.key_code == 0x46:  # F
                        pyautogui.press('f')
                    
                    if self.debug_mode:
                        print(f"[DEBUG] Focused window and sent key")
                    return True
                return False
            
            elif self.action_type == "focus_click":
                # Focus window then click
                if self.focus_window(self.target_window):
                    time.sleep(0.1)
                    center = self.get_window_center(self.target_window)
                    if center:
                        pyautogui.click(center[0], center[1])
                        if self.debug_mode:
                            print(f"[DEBUG] Focused window and clicked at {center}")
                        return True
                return False
            
            else:  # Default: regular pyautogui
                if self.key_code == 0x0D:  # Enter
                    pyautogui.press('enter')
                elif self.key_code == 0x20:  # Space
                    pyautogui.press('space')
                elif self.key_code == 0x45:  # E
                    pyautogui.press('e')
                elif self.key_code == 0x46:  # F
                    pyautogui.press('f')
                
                if self.debug_mode:
                    print(f"[DEBUG] Sent regular key press")
                return True
                
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error performing action: {e}")
            return False
    
    def action_loop(self):
        """Main action loop"""
        record()
        
        while self.running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                if self.perform_action():
                    self.action_count += 1
                    print(f"[{current_time}] Action #{self.action_count} completed")
                else:
                    print(f"[{current_time}] Action failed")
                
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"Error in action loop: {e}")
                time.sleep(1)
    
    def start(self, game_title, interval=5, action_type="message_key", key_code=0x0D):
        """Start the input sender"""
        self.interval = interval
        self.action_type = action_type
        self.key_code = key_code
        
        if game_title:
            windows = self.find_game_window(game_title)
            
            if not windows:
                print(f"Game window containing '{game_title}' not found!")
                print("\nAvailable windows:")
                self.show_available_windows()
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
            
            print(f"Target window: {window_title}")
            print(f"Action type: {action_type}")
            print(f"Interval: {interval} seconds")
            print("Press 'ESC' to stop\n")
        
        self.running = True
        
        # Start action loop in separate thread
        action_thread = threading.Thread(target=self.action_loop, daemon=True)
        action_thread.start()
        
        return True
    
    def stop(self):
        """Stop the input sender"""
        self.running = False
        print(f"\nStopped! Total actions performed: {self.action_count}")
    
    def show_available_windows(self):
        """Show all available windows"""
        def show_windows(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 3:
                    print(f"  - {title}")
            return True
        
        win32gui.EnumWindows(show_windows, [])

def main():
    print("=== Game Input Sender - Multiple Methods ===")
    print("This tool tries different ways to send input to games")
    print()
    
    # Get game title
    game_title = input("Enter game window title (partial match): ").strip()
    if not game_title:
        print("Game title is required!")
        return
    
    # Get interval
    try:
        interval_input = input("Enter interval in seconds (default: 5): ").strip()
        interval = float(interval_input) if interval_input else 5.0
    except ValueError:
        interval = 5.0
    
    # Choose method
    print("\nChoose input method:")
    print("1. Windows Message - Key (most compatible with games)")
    print("2. Windows Message - Click")
    print("3. Focus + PyAutoGUI Key")
    print("4. Focus + PyAutoGUI Click")
    print("5. Regular PyAutoGUI Key (least compatible)")
    
    method_choice = input("Enter choice (1-5, default: 1): ").strip()
    
    if method_choice == "2":
        action_type = "message_click"
        key_code = 0
    elif method_choice == "3":
        action_type = "focus_key"
    elif method_choice == "4":
        action_type = "focus_click"
        key_code = 0
    elif method_choice == "5":
        action_type = "regular"
    else:
        action_type = "message_key"
    
    # Choose key if needed
    key_code = 0x0D  # Default: Enter
    if "key" in action_type or action_type == "regular":
        print("\nChoose key:")
        print("1. Enter (default)")
        print("2. Space")
        print("3. E")
        print("4. F")
        
        key_choice = input("Enter choice (1-4): ").strip()
        
        if key_choice == "2":
            key_code = 0x20  # Space
        elif key_choice == "3":
            key_code = 0x45  # E
        elif key_choice == "4":
            key_code = 0x46  # F
        else:
            key_code = 0x0D  # Enter
    
    sender = GameInputSender()
    
    try:
        if sender.start(game_title, interval, action_type, key_code):
            # Wait for ESC to stop
            while sender.running:
                if keyboard.is_pressed('esc'):
                    sender.stop()
                    break
                time.sleep(0.1)
        
    except KeyboardInterrupt:
        sender.stop()
        print("Stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        if sender.running:
            sender.stop()

def record():

    pyautogui.keyDown("Alt")
    pyautogui.keyDown("r")
    pyautogui.keyUp("Alt")
    pyautogui.keyUp("r")
    
    pyautogui.keyDown("Alt")
    pyautogui.keyDown("r")
    pyautogui.keyUp("Alt")
    pyautogui.keyUp("r")
    
if __name__ == "__main__":
    
    main()
    