import cv2
import pyautogui
import time

# Load a pre-trained Haar Cascade for detecting eyes
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

def track_iris(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    for (ex, ey, ew, eh) in eyes:
        iris_x = ex + ew // 2
        iris_y = ey + eh // 2

        return iris_x, iris_y

    return None, None

def perform_click(action):
    if action == 'single':
        pyautogui.click()
        print("Single Click")
    elif action == 'double':
        pyautogui.doubleClick()
        print("Double Click")
    elif action == 'right':
        pyautogui.rightClick()
        print("Right Click")

pyautogui.FAILSAFE = False

cam = cv2.VideoCapture(0)
screen_w, screen_h = pyautogui.size()

click_threshold = 5  # Allowed variance in iris position for double click
double_click_time = 4

last_click_time = time.time()
last_iris_position = None

while True:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)

    # Track the iris
    iris_x, iris_y = track_iris(frame)

    if iris_x is not None and iris_y is not None:
        # Now you have the position of the iris (iris_x, iris_y)
        screen_x = screen_w / frame.shape[1] * iris_x
        screen_y = screen_h / frame.shape[0] * iris_y

        # Apply margin to prevent getting stuck at the edges
        margin = 50
        screen_x = max(margin, min(screen_x, screen_w - margin))
        screen_y = max(margin, min(screen_y, screen_h - margin))

        pyautogui.moveTo(screen_x, screen_y)

        if last_iris_position is not None:
            # Check if variance is within threshold for double click
            x_diff = abs(iris_x - last_iris_position[0])
            y_diff = abs(iris_y - last_iris_position[1])

            if x_diff <= click_threshold and y_diff <= click_threshold:
                current_time = time.time()
                if current_time - last_click_time > double_click_time:
                    perform_click('double')
                    last_click_time = current_time

        last_iris_position = (iris_x, iris_y)

        print(f"Iris Position: ({iris_x}, {iris_y})")

    cv2.imshow('Eye Controlled Mouse', frame)

    key = cv2.waitKey(1)
    if key == ord('q'):  # Press 'q' to quit
        break
    elif key == ord('s'):  # Press 's' for single click
        perform_click('single')
    elif key == ord('r'):  # Press 'r' for right click
        perform_click('right')

cam.release()
cv2.destroyAllWindows()

