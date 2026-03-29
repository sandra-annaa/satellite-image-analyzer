import cv2
import numpy as np

# Load image
image = cv2.imread('satellite.jpg')

# Check if image loaded properly
if image is None:
    print("Error: Image not found! Make sure 'satellite.jpg' is in the same folder.")
    exit()

# Convert image to HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# -------------------------------
# Detect Water (Blue regions)
# -------------------------------
lower_blue = np.array([80, 50, 50])
upper_blue = np.array([140, 255, 255])
water_mask = cv2.inRange(hsv, lower_blue, upper_blue)

# -------------------------------
# Detect Vegetation (Green regions)
# -------------------------------
lower_green = np.array([25, 40, 40])
upper_green = np.array([90, 255, 255])
veg_mask = cv2.inRange(hsv, lower_green, upper_green)

# -------------------------------
# Apply masks to original image
# -------------------------------
water_result = cv2.bitwise_and(image, image, mask=water_mask)
veg_result = cv2.bitwise_and(image, image, mask=veg_mask)
# --- Find contours (boundaries) ---
water_contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
veg_contours, _ = cv2.findContours(veg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Draw contours on original image
output_image = image.copy()

cv2.drawContours(output_image, water_contours, -1, (255, 0, 0), 2)  # Blue for water
cv2.drawContours(output_image, veg_contours, -1, (0, 255, 0), 2)    # Green for vegetation
# -------------------------------
# Calculate percentage
# -------------------------------
total_pixels = image.shape[0] * image.shape[1]

water_pixels = np.sum(water_mask == 255)
veg_pixels = np.sum(veg_mask == 255)

water_percent = (water_pixels / total_pixels) * 100
veg_percent = (veg_pixels / total_pixels) * 100

print(f"Water Area: {water_percent:.2f}%")
print(f"Vegetation Area: {veg_percent:.2f}%")

# -------------------------------
# Display results
# -------------------------------
# --- Put text on image ---
cv2.putText(output_image,
            f"Water: {water_percent:.2f}%",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 0, 0),
            2)

cv2.putText(output_image,
            f"Vegetation: {veg_percent:.2f}%",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2)
cv2.imshow("Original Image", image)
cv2.imshow("Water Mask", water_mask)
cv2.imshow("Vegetation Mask", veg_mask)
cv2.imshow("Water Detected (Color)", water_result)
cv2.imshow("Vegetation Detected (Color)", veg_result)
cv2.imshow("Detected Boundaries", output_image)

cv2.waitKey(0)
cv2.destroyAllWindows()