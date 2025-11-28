from PIL import Image
import os

input_path = "dashboard_header.png"
output_path = "dashboard_header.png"
target_size = (1550, 450)

if os.path.exists(input_path):
    try:
        with Image.open(input_path) as img:
            # Resize using LANCZOS for high quality
            resized_img = img.resize(target_size, Image.Resampling.LANCZOS)
            resized_img.save(output_path)
            print(f"Successfully resized {input_path} to {target_size}")
    except Exception as e:
        print(f"Error resizing image: {e}")
else:
    print(f"Error: {input_path} not found.")
