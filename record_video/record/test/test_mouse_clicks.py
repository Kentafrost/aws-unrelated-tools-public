import pyautogui
import time
import win32gui

def test_mouse_clicks():
    print("Mouse Click Test - Testing different click methods")
    print("Position your game window where you want to test clicks")
    print()
    
    # Get current mouse position
    current_pos = pyautogui.position()
    print(f"Current mouse position: ({current_pos.x}, {current_pos.y})")
    
    # Find game window if user provides title
    game_title = input("Enter game window title (or press Enter to skip): ").strip()
    
    if game_title:
        def enum_windows_proc(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if game_title.lower() in window_title.lower() and window_title:
                    windows.append((hwnd, window_title))
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_proc, windows)
        
        if windows:
            window_hwnd = windows[0][0]
            window_title = windows[0][1]
            print(f"Found game window: {window_title}")
            
            # Get window center
            rect = win32gui.GetWindowRect(window_hwnd)
            center_x = (rect[0] + rect[2]) // 2
            center_y = (rect[1] + rect[3]) // 2
            print(f"Game window center: ({center_x}, {center_y})")
            print(f"Game window rect: {rect}")
        else:
            print(f"Game window '{game_title}' not found")
            center_x, center_y = current_pos.x, current_pos.y
    else:
        center_x, center_y = current_pos.x, current_pos.y
    
    print("\nStarting tests in 3 seconds...")
    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)
    
    print("\nTesting different click methods:")
    
    # Test 1: Simple left click at current position
    print("1. Left click at current mouse position...")
    pyautogui.click()
    time.sleep(1.5)
    
    # Test 2: Left click at game window center
    print(f"2. Left click at calculated center ({center_x}, {center_y})...")
    pyautogui.click(center_x, center_y)
    time.sleep(1.5)
    
    # Test 3: Double click
    print("3. Double click at center...")
    pyautogui.doubleClick(center_x, center_y)
    time.sleep(1.5)
    
    # Test 4: Right click
    print("4. Right click at center...")
    pyautogui.rightClick(center_x, center_y)
    time.sleep(1.5)
    
    # Test 5: Click with explicit button
    print("5. Explicit left button click...")
    pyautogui.click(center_x, center_y, button='left')
    time.sleep(1.5)
    
    # Test 6: Mouse down and up separately
    print("6. Mouse down/up separately...")
    pyautogui.mouseDown(center_x, center_y, button='left')
    time.sleep(0.1)
    pyautogui.mouseUp(center_x, center_y, button='left')
    time.sleep(1.5)
    
    # Test 7: Move then click
    print("7. Move to position then click...")
    pyautogui.moveTo(center_x, center_y)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(1.5)
    
    print("\nTest completed! Which click method worked for your game?")
    print("Note: Some games may require specific timing or may not accept")
    print("clicks when not in focus, or may need the mouse to be in a")
    print("specific area of the game window.")

if __name__ == "__main__":
    try:
        # Disable pyautogui fail-safe (be careful!)
        pyautogui.FAILSAFE = False
        test_mouse_clicks()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Re-enable fail-safe
        pyautogui.FAILSAFE = True
