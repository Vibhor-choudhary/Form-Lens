"""Create one local English form screenshot for the end-to-end MVP check."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).parent / "fixtures" / "english_registration_form.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
image = Image.new("RGB", (1200, 1000), "#f5f7fb")
draw = ImageDraw.Draw(image)
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 28)
title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 42)

draw.rounded_rectangle((130, 55, 1070, 940), radius=18, fill="white", outline="#d9e0ea", width=2)
draw.text((190, 120), "Event Registration", fill="#152238", font=title_font)
draw.text((190, 185), "Please complete the form below.", fill="#52657a", font=font)

fields = [
    ("First Name", 280),
    ("Email Address", 410),
    ("Date of Birth", 540),
]
for label, y in fields:
    draw.text((190, y), label, fill="#1d2939", font=font)
    draw.rounded_rectangle((190, y + 42, 1000, y + 102), radius=7, fill="#ffffff", outline="#9caec2", width=3)

draw.rectangle((190, 700, 220, 730), fill="white", outline="#718096", width=3)
draw.text((240, 699), "I agree to receive event updates", fill="#1d2939", font=font)
draw.rounded_rectangle((190, 790, 430, 860), radius=8, fill="#1e6bd6")
draw.text((255, 810), "Submit", fill="white", font=font)
image.save(OUT)
print(OUT)
