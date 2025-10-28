import pyautogui
import time
import keyboard

def test_key_press():
    print("Key Press Test - Testing different keys")
    print("This will test various key combinations that might work for continuing game phrases")
    print("Position your cursor in a text editor or game and wait...")
    
    for i in range(5, 0, -1):
        print(f"Starting in {i} seconds...")
        time.sleep(1)
    
    print("\nTesting keys:")
    
    # Test 1: Enter key
    print("1. Testing Enter key...")
    pyautogui.press('enter')
    time.sleep(1)
    
    # Test 2: Return key (alternative)
    print("2. Testing Return key...")
    pyautogui.press('return')
    time.sleep(1)
    
    # Test 3: Space key
    print("3. Testing Space key...")
    pyautogui.press('space')
    time.sleep(1)
    
    # Test 4: Tab key
    print("4. Testing Tab key...")
    pyautogui.press('tab')
    time.sleep(1)
    
    # Test 5: Left mouse click
    print("5. Testing Left mouse click...")
    pyautogui.click()
    time.sleep(1)
    
    # Test 6: E key (common continue key in games)
    print("6. Testing E key...")
    pyautogui.press('e')
    time.sleep(1)
    
    # Test 7: F key (another common interact key)
    print("7. Testing F key...")
    pyautogui.press('f')
    time.sleep(1)
    
    print("\nTest completed! Which key worked for your game?")

if __name__ == "__main__":
    try:
        test_key_press()
    except Exception as e:
        print(f"Error: {e}")
