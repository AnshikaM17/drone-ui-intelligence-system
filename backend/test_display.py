import cv2
import numpy as np

print("Testing OpenCV display capabilities...")

# Create a simple test image
test_image = np.zeros((480, 640, 3), dtype=np.uint8)
cv2.putText(test_image, "If you see this, display works!", (50, 240), 
            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
cv2.circle(test_image, (320, 240), 50, (255, 0, 0), -1)

print("Creating window...")
cv2.namedWindow("Display Test", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Display Test", 800, 600)

print("Displaying test image...")
cv2.imshow("Display Test", test_image)

print("Press any key to close...")
cv2.waitKey(0)
cv2.destroyAllWindows()
print("Test complete!")
