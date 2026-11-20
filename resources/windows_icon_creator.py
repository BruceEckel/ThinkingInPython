# /// script
# requires-python = ">=3.13"
# dependencies = ["pillow>=12.3.0"]
# ///
# Build ThinkingInPython.ico from the cover art. Run with:
#   uv run resources/windows_icon_creator.py
from pathlib import Path
from PIL import Image

# Both files sit beside this script, in resources/
resources = Path(__file__).resolve().parent
input_path = resources / "cover-source.jpg"
output_path = resources / "ThinkingInPython.ico"

# Open the original wide image
img = Image.open(input_path).convert("RGBA")
width, height = img.size

# Create a square canvas in the image's background color
bg_color = img.getpixel((0, 0))
square_size = max(width, height)
square_img = Image.new(
    "RGBA", (square_size, square_size), bg_color
)

# Center the snake artwork on the square canvas
offset = (
    (square_size - width) // 2,
    (square_size - height) // 2,
)
square_img.paste(img, offset)

# Save as a multi-resolution Windows .ico
icon_sizes = [
    (16, 16),
    (32, 32),
    (48, 48),
    (64, 64),
    (128, 128),
    (256, 256),
]
square_img.save(output_path, format="ICO", sizes=icon_sizes)
print(f"Created {output_path}")
