import cv2
import numpy as np
import pyautogui
import keyboard
import pygetwindow as gw
import time
import threading

# Function to monitor keypress in the background
def listen_for_shutdown():
    while True:
        if keyboard.is_pressed('q'):
            print("Shutting down...")
            exit()

# Start the background thread for key press detection
thread = threading.Thread(target=listen_for_shutdown, daemon=True)
thread.start()

# Focus on the Metin game window (Asgard)
try:
    metin_window = gw.getWindowsWithTitle('Asgard')[0]
    metin_window.activate()
    time.sleep(0.5)
except IndexError:
    print("Metin window not found!")
    exit()

# Define function to apply blue mask filtering
def apply_blue_mask(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([130, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    return mask

# Define function to detect white spots and prioritize larger ones
def find_metin_candidates(filtered_image):
    contours, _ = cv2.findContours(filtered_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # Ignore small noise
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                candidates.append((cx, cy, area))
    
    # Sort by size (biggest first)
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates

# Main loop to continuously search for Metins
while True:
    # Capture the screen
    screenshot = pyautogui.screenshot()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # Apply blue mask filtering
    mask = apply_blue_mask(screenshot)
    cv2.imwrite("debug_mask.png", mask)  # Save debug image
    
    # Find potential Metins based on bright spots
    metin_candidates = find_metin_candidates(mask)
    
    debug_image = screenshot.copy()
    best_metin = None

    for (cx, cy, area) in metin_candidates:
        if cy < screenshot.shape[0] - 100:  # Ignore bottom 100px (taskbar region)
            cv2.circle(debug_image, (cx, cy), 10, (0, 255, 0), 2)  # Draw circles for debug
            if best_metin is None or area > best_metin[2]:
                best_metin = (cx, cy, area)
    
    cv2.imwrite("debug_contours.png", debug_image)  # Save debug image
    
    # If a Metin is found, interact with it
    if best_metin:
        cx, cy, _ = best_metin
        print(f"Found Metin at: {cx, cy} (Size: {_})")
        pyautogui.moveTo(cx, cy, duration=0.5)
        time.sleep(0.3)
        pyautogui.click()
        print("Waiting 25 seconds before looting...")
        time.sleep(25)
        keyboard.press('z')
        time.sleep(1)
        keyboard.release('z')
        print("Searching for the next Metin...\n")
    else:
        print("No Metin found. Retrying in 3 seconds...")
        time.sleep(3)