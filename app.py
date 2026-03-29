import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import sqlite3
import os
import csv
# Create DB
conn = sqlite3.connect("results.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_name TEXT,
    water REAL,
    vegetation REAL
)
""")

conn.commit()
def process_image(path):
    image = cv2.imread(path)
    if image is None:
        print("Error loading image")
        return None

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Blue (Water)
    lower_blue = np.array([80, 50, 50])
    upper_blue = np.array([140, 255, 255])
    water_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Green (Vegetation)
    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    veg_mask = cv2.inRange(hsv, lower_green, upper_green)

    # Contours
    water_contours, _ = cv2.findContours(water_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    veg_contours, _ = cv2.findContours(veg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output = image.copy()
    cv2.drawContours(output, water_contours, -1, (255, 0, 0), 2)
    cv2.drawContours(output, veg_contours, -1, (0, 255, 0), 2)

    # Percentages
    total_pixels = image.shape[0] * image.shape[1]
    water_pixels = np.sum(water_mask == 255)
    veg_pixels = np.sum(veg_mask == 255)

    water_percent = (water_pixels / total_pixels) * 100
    veg_percent = (veg_pixels / total_pixels) * 100
    image_name = os.path.basename(path)

    cursor.execute("INSERT INTO analysis (image_name, water, vegetation) VALUES (?, ?, ?)",
               (image_name, water_percent, veg_percent))

    conn.commit()
    # Add text
    cv2.putText(output, f"Water: {water_percent:.2f}%", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.putText(output, f"Vegetation: {veg_percent:.2f}%", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    return output
def show_history():
    history_window = tk.Toplevel(root)
    history_window.title("Analysis History")

    rows = cursor.execute("SELECT * FROM analysis")

    for i, row in enumerate(rows):
        text = f"{row[1]} | Water: {row[2]:.2f}% | Veg: {row[3]:.2f}%"
        label = tk.Label(history_window, text=text)
        label.pack()


def export_csv():
    with open("results.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Image", "Water %", "Vegetation %"])

        rows = cursor.execute("SELECT image_name, water, vegetation FROM analysis")
        for row in rows:
            writer.writerow(row)

    print("Exported to results.csv")
def clear_history():
    cursor.execute("DELETE FROM analysis")
    conn.commit()
    print("History cleared")
def upload_image():
    file_path = filedialog.askopenfilename()
    if not file_path:
        return

    result = process_image(file_path)
    if result is None:
        return

    # Convert for display
    result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(result_rgb)
    img = img.resize((400, 400))

    img_tk = ImageTk.PhotoImage(img)

    panel.config(image=img_tk)
    panel.image = img_tk

# GUI window
root = tk.Tk()
root.title("Satellite Image Analyzer")

btn = tk.Button(root, text="Upload Image", command=upload_image)
btn.pack(pady=10)
history_btn = tk.Button(root, text="Show History", command=show_history)
history_btn.pack(pady=10)
export_btn = tk.Button(root, text="Export CSV", command=export_csv)
export_btn.pack(pady=10)
clear_btn = tk.Button(root, text="Clear History", command=clear_history)
clear_btn.pack(pady=10)
panel = tk.Label(root)
panel.pack()
for row in cursor.execute("SELECT * FROM analysis"):
    print(row)
root.geometry("500x500")
root.configure(bg="lightblue")
root.mainloop()