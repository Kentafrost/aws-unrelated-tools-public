import time
import pyautogui
import threading
import keyboard
import win32gui
import win32process
from datetime import datetime

class GameAutoClicker:
    def __init__(self):
        self.running = False
        self.game_title = ""
        self.click_interval = 5
        self.target_window = None
        self.click_count = 0
        
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
            return foreground_window == self.target_window
        except:
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
    
    def focus_game_window(self, hwnd):
        """Focus/bring the game window to foreground"""
        try:
            # First check if window is minimized and restore it
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, 9)  # SW_RESTORE
                time.sleep(0.2)  # Small delay for window to restore
            
            # Bring window to foreground
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)  # Small delay for focus to take effect
            
            # Verify window is now focused
            focused_window = win32gui.GetForegroundWindow()
            return focused_window == hwnd
            
        except Exception as e:
            print(f"Error focusing window: {e}")
            return False
    
    def auto_click_loop(self):
        """Main clicking loop"""
        while self.running:
            try:
                # Check if game window still exists
                if self.target_window and win32gui.IsWindow(self.target_window):
                    # Check if game is active/focused
                    if self.is_game_active():
                        center = self.get_window_center(self.target_window)
                        if center:
                            pyautogui.press("enter")
                            self.click_count += 1
                            current_time = datetime.now().strftime("%H:%M:%S")
                            print(f"[{current_time}] Click #{self.click_count} - Game active")
                        else:
                            # Fallback to current mouse position
                            pyautogui.press("enter")
                            self.click_count += 1
                            print(f"Click #{self.click_count} - Using current position")
                    else:
                        # Try to focus the game window first
                        current_time = datetime.now().strftime("%H:%M:%S")
                        print(f"[{current_time}] Game not focused, attempting to focus...")
                        
                        if self.focus_game_window(self.target_window):
                            print(f"[{current_time}] Successfully focused game window")
                            # Now click since we focused the window
                            center = self.get_window_center(self.target_window)
                            if center:
                                # enter key click
                                pyautogui.press("enter")
                                self.click_count += 1
                                print(f"[{current_time}] Click #{self.click_count} - After focusing")
                        else:
                            print(f"[{current_time}] Failed to focus game window, skipping click")
                else:
                    print("Game window not found, stopping...")
                    self.stop()
                    break
                
                time.sleep(self.click_interval)
                
            except Exception as e:
                print(f"Error during clicking: {e}")
                time.sleep(1)
    
    def start(self, game_title="", click_interval=5):
        """Start the auto-clicker"""
        self.click_interval = click_interval
        
        if game_title:
            # Find specific game window
            windows = self.find_game_window(game_title)
            
            if not windows:
                print(f"Game window containing '{game_title}' not found!")
                print("\nAvailable windows:")
                self.show_available_windows()
                
                choice = input("\nDo you want to continue with any active window? (y/n): ")
                if choice.lower() != 'y':
                    return False
            else:
                self.target_window = windows[0][0]
                window_title = windows[0][1]
                print(f"Found target window: {window_title}")
                
                # Test initial focus
                if not self.is_game_active():
                    print("Game window not currently focused, will auto-focus when needed")
                else:
                    print("Game window is currently focused")
        
        print(f"Auto-clicker starting...")
        print(f"Click interval: {click_interval} seconds")
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
        print(f"\nAuto-clicker stopped! Total clicks: {self.click_count}")
    
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
    # Configuration - Change these values as needed
    GAME_TITLE = "Minecraft"  # Change to your game's window title (partial match)
    CLICK_INTERVAL = 5  # seconds between clicks
    
    print("=== Game Auto-Clicker for Recording ===")
    print("This will automatically click every 5 seconds when your game is active")
    print("It will also try to focus your game window if it's not active")
    print()
    
    # Allow user to customize game title
    user_game = input(f"Enter game window title (current: '{GAME_TITLE}', press Enter to use default): ").strip()
    if user_game:
        GAME_TITLE = user_game
    
    # Allow user to customize interval
    try:
        user_interval = input(f"Enter click interval in seconds (current: {CLICK_INTERVAL}, press Enter for default): ").strip()
        if user_interval:
            CLICK_INTERVAL = float(user_interval)
    except ValueError:
        print("Invalid interval, using default 5 seconds")
    
    clicker = GameAutoClicker()
    
    try:
        if clicker.start(GAME_TITLE, CLICK_INTERVAL):
            # Wait for ESC key to stop
            while clicker.running:
                if keyboard.is_pressed('esc'):
                    clicker.stop()
                    break
                time.sleep(0.1)
        
    except KeyboardInterrupt:
        clicker.stop()
        print("Stopped by user (Ctrl+C)")
    except ImportError as e:
        print(f"Missing required library: {e}")
        print("Please install: pip install pyautogui keyboard pywin32 psutil")
    except Exception as e:
        print(f"Error: {e}")
        if clicker.running:
            clicker.stop()

if __name__ == "__main__":
    main()
