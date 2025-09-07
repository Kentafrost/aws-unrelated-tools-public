import time
import pyautogui
import threading
import keyboard
import win32gui
import win32process
from datetime import datetime

class ImprovedGameAutoClicker:
    def __init__(self):
        self.running = False
        self.game_title = ""
        self.click_interval = 5
        self.target_window = None
        self.click_count = 0
        self.key_to_press = "enter"  # Default key
        self.use_mouse_click = True
        self.debug_mode = True
        self.mouse_click_type = "single"  # single, double, right
        self.click_delay = 0.1  # delay between mouse down and up
        
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
    
    def is_game_active(self):
        """Check if the target game window is active/focused"""
        if not self.target_window:
            return False
        
        try:
            foreground_window = win32gui.GetForegroundWindow()
            is_active = foreground_window == self.target_window
            if self.debug_mode:
                current_title = win32gui.GetWindowText(foreground_window) if foreground_window else "None"
                target_title = win32gui.GetWindowText(self.target_window) if self.target_window else "None"
                print(f"[DEBUG] Current window: '{current_title}', Target: '{target_title}', Active: {is_active}")
            return is_active
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error checking if game active: {e}")
            return False
    
    def get_window_center(self, hwnd):
        """Get the center coordinates of a window"""
        try:
            rect = win32gui.GetWindowRect(hwnd)
            x = (rect[0] + rect[2]) // 2
            y = (rect[1] + rect[3]) // 2
            if self.debug_mode:
                print(f"[DEBUG] Window center: ({x}, {y}), Rect: {rect}")
            return (x, y)
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error getting window center: {e}")
            return None
    
    def focus_game_window(self, hwnd):
        """Focus/bring the game window to foreground"""
        try:
            # First check if window is minimized and restore it
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                time.sleep(0.3)  # Longer delay for window to restore
            
            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.2)  # Longer delay for focus to take effect
            
            # Verify window is now focused
            focused_window = win32gui.GetForegroundWindow()
            success = focused_window == hwnd
            
            if self.debug_mode:
                print(f"[DEBUG] Focus attempt - Success: {success}")
            
            return success
            
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error focusing window: {e}")
            return False
    
    def perform_action(self):
        """Perform the configured action (key press or mouse click)"""
        try:
            if self.use_mouse_click:
                if self.target_window:
                    # Click in the center of the game window
                    center = self.get_window_center(self.target_window)
                    if center:
                        # Save current mouse position
                        original_pos = pyautogui.position()
                        
                        # Perform different types of clicks based on configuration
                        if self.mouse_click_type == "double":
                            pyautogui.doubleClick(center[0], center[1])
                            if self.debug_mode:
                                print(f"[DEBUG] Double-clicked at game window center: {center}")
                        elif self.mouse_click_type == "right":
                            pyautogui.rightClick(center[0], center[1])
                            if self.debug_mode:
                                print(f"[DEBUG] Right-clicked at game window center: {center}")
                        elif self.mouse_click_type == "manual":
                            # Manual mouse down/up with delay
                            pyautogui.mouseDown(center[0], center[1], button='left')
                            time.sleep(self.click_delay)
                            pyautogui.mouseUp(center[0], center[1], button='left')
                            if self.debug_mode:
                                print(f"[DEBUG] Manual click (down/up) at game window center: {center}")
                        else:  # single click (default)
                            pyautogui.click(center[0], center[1], button='left')
                            if self.debug_mode:
                                print(f"[DEBUG] Single left-clicked at game window center: {center}")
                        
                        # Optionally restore mouse position (uncomment if needed)
                        # time.sleep(0.1)
                        # pyautogui.moveTo(original_pos.x, original_pos.y)
                    else:
                        # Fallback: click at current position
                        current_pos = pyautogui.position()
                        pyautogui.click(current_pos.x, current_pos.y, button='left')
                        if self.debug_mode:
                            print(f"[DEBUG] Fallback click at current position: ({current_pos.x}, {current_pos.y})")
                else:
                    # No target window, click at current position
                    current_pos = pyautogui.position()
                    pyautogui.click(current_pos.x, current_pos.y, button='left')
                    if self.debug_mode:
                        print(f"[DEBUG] Click at current position (no target): ({current_pos.x}, {current_pos.y})")
            else:
                # Press the configured key
                pyautogui.press(self.key_to_press)
                if self.debug_mode:
                    print(f"[DEBUG] Pressed key: {self.key_to_press}")
            return True
        except Exception as e:
            if self.debug_mode:
                print(f"[DEBUG] Error performing action: {e}")
            return False
    
    def auto_click_loop(self):
        """Main clicking loop"""
        while self.running:
            try:
                current_time = datetime.now().strftime("%H:%M:%S")
                
                # Check if game window still exists
                if self.target_window and win32gui.IsWindow(self.target_window):
                    # Check if game is active/focused
                    if self.is_game_active():
                        if self.perform_action():
                            self.click_count += 1
                            print(f"[{current_time}] Action #{self.click_count} - Game active")
                        else:
                            print(f"[{current_time}] Failed to perform action")
                    else:
                        # Try to focus the game window first
                        print(f"[{current_time}] Game not focused, attempting to focus...")
                        
                        if self.focus_game_window(self.target_window):
                            print(f"[{current_time}] Successfully focused game window")
                            # Wait a bit more after focusing, then perform action
                            time.sleep(0.5)
                            if self.perform_action():
                                self.click_count += 1
                                print(f"[{current_time}] Action #{self.click_count} - After focusing")
                        else:
                            print(f"[{current_time}] Failed to focus game window, skipping action")
                else:
                    print("Game window not found, stopping...")
                    self.stop()
                    break
                
                time.sleep(self.click_interval)
                
            except Exception as e:
                print(f"Error during clicking: {e}")
                time.sleep(1)
    
    def start(self, game_title="", click_interval=5, key_to_press="enter", use_mouse=False, mouse_type="single"):
        """Start the auto-clicker"""
        self.click_interval = click_interval
        self.key_to_press = key_to_press
        self.use_mouse_click = use_mouse
        self.mouse_click_type = mouse_type
        
        if game_title:
            # Find specific game window
            windows = self.find_game_window(game_title)
            
            if not windows:
                print(f"Game window containing '{game_title}' not found!")
                print("\nAvailable windows:")
                self.show_available_windows()
                
                choice = input("\nDo you want to continue anyway? (y/n): ")
                if choice.lower() != 'y':
                    return False
            else:
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
                            print("Invalid selection, using first window")
                            self.target_window = windows[0][0]
                            window_title = windows[0][1]
                    except ValueError:
                        print("Invalid input, using first window")
                        self.target_window = windows[0][0]
                        window_title = windows[0][1]
                else:
                    self.target_window = windows[0][0]
                    window_title = windows[0][1]
                
                print(f"Selected target window: {window_title}")
                
                # Test initial focus
                if not self.is_game_active():
                    print("Game window not currently focused, will auto-focus when needed")
                else:
                    print("Game window is currently focused")
        
        action_desc = f"mouse clicks" if use_mouse else f"'{key_to_press}' key presses"
        print(f"\nAuto-clicker starting...")
        print(f"Action: {action_desc}")
        print(f"Interval: {click_interval} seconds")
        print(f"Target: {'Specific game window' if self.target_window else 'Any active window'}")
        print("Press 'ESC' to stop\n")
        
        self.running = True
        
        # Start clicking in a separate thread
        click_thread = threading.Thread(target=self.auto_click_loop, daemon=True)
        click_thread.start()
        
        return True
    
    def stop(self):
        """Stop the auto-clicker"""
        self.running = False
        # left click
        if self.use_mouse_click:
            pyautogui.click(button='left')
        else:
            pyautogui.press(self.key_to_press)
        print(f"\nAuto-clicker stopped! Total actions: {self.click_count}")

    def show_available_windows(self):
        """Show all available game windows"""
        def show_windows(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and len(title) > 3:  # Filter out very short titles
                    print(f"  - {title}")
            return True
        
        win32gui.EnumWindows(show_windows, [])

def main():
    print("=== Improved Game Auto-Clicker ===")
    print("This tool will help you automatically continue game phrases")
    print()
    
    # Get game title
    game_title = input("Enter game window title (partial match, e.g., 'Minecraft', 'Steam'): ").strip()
    
    # Get interval
    try:
        interval_input = input("Enter interval in seconds (default: 5): ").strip()
        interval = float(interval_input) if interval_input else 5.0
    except ValueError:
        print("Invalid interval, using 5 seconds")
        interval = 5.0
    
    # Choose action type
    print("\nChoose action type:")
    print("1. Key press (default)")
    print("2. Mouse click")
    
    action_choice = input("Enter choice (1 or 2): ").strip()
    use_mouse = action_choice == "2"
    
    key_to_press = "enter"
    mouse_type = "single"
    
    if use_mouse:
        # Choose mouse click type
        print("\nChoose mouse click type:")
        print("1. Single left click (default)")
        print("2. Double left click")
        print("3. Right click")
        print("4. Manual click (mouse down/up with delay)")
        
        mouse_choice = input("Enter choice (1-4): ").strip()
        
        if mouse_choice == "2":
            mouse_type = "double"
        elif mouse_choice == "3":
            mouse_type = "right"
        elif mouse_choice == "4":
            mouse_type = "manual"
        else:
            mouse_type = "single"
        
        print(f"Selected: {mouse_type} click")
    else:
        # Choose key to press
        print("\nChoose key to press:")
        print("1. Enter (default)")
        print("2. Space")
        print("3. E")
        print("4. F")
        print("5. Custom key")
        
        key_choice = input("Enter choice (1-5): ").strip()
        
        if key_choice == "2":
            key_to_press = "space"
        elif key_choice == "3":
            key_to_press = "e"
        elif key_choice == "4":
            key_to_press = "f"
        elif key_choice == "5":
            custom_key = input("Enter custom key: ").strip().lower()
            if custom_key:
                key_to_press = custom_key
    
    clicker = ImprovedGameAutoClicker()
    
    try:
        if clicker.start(game_title, interval, key_to_press, use_mouse, mouse_type):
            # Wait for ESC key to stop
            while clicker.running:
                if keyboard.is_pressed('esc'):
                    clicker.stop()
                    break
                time.sleep(0.1)
        
    except KeyboardInterrupt:
        clicker.stop()
        print("Stopped by user (Ctrl+C)")
    except Exception as e:
        print(f"Error: {e}")
        if clicker.running:
            clicker.stop()

if __name__ == "__main__":
    main()
