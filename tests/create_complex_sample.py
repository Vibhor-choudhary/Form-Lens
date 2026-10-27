"""Create a denser multi-section English form fixture for FormLens."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).parent / "fixtures" / "complex_event_application_form.png"
OUT.parent.mkdir(parents=True, exist_ok=True)
image = Image.new("RGB", (1500, 1350), "#eef2f7")
draw = ImageDraw.Draw(image)
regular = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 24)
small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 34)
title = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)

draw.rounded_rectangle((70, 40, 1430, 1290), radius=18, fill="white", outline="#cbd5e1", width=3)
draw.text((125, 90), "Community Event Application", fill="#172b4d", font=title)
draw.text((125, 155), "Complete all required details before submitting your application.", fill="#52657a", font=regular)

def label(text, x, y):
    draw.text((x, y), text, fill="#172b4d", font=regular)

def input_box(x, y, w=520, h=58):
    draw.rounded_rectangle((x, y, x + w, y + h), radius=7, fill="white", outline="#91a4ba", width=3)

def checkbox(x, y, text):
    draw.rectangle((x, y, x + 28, y + 28), fill="white", outline="#718096", width=3)
    draw.text((x + 42, y - 3), text, fill="#27364a", font=small)

def radio(x, y, text):
    draw.ellipse((x, y, x + 28, y + 28), fill="white", outline="#718096", width=3)
    draw.text((x + 42, y - 3), text, fill="#27364a", font=small)

draw.line((125, 220, 1375, 220), fill="#d8e0ea", width=2)
label("Applicant details", 125, 255)
label("Full Name", 125, 315); input_box(125, 355)
label("Email Address", 760, 315); input_box(760, 355)
label("Phone Number", 125, 455); input_box(125, 495)
label("Organization", 760, 455); input_box(760, 495)

draw.line((125, 600, 1375, 600), fill="#d8e0ea", width=2)
label("Event preferences", 125, 635)
label("Preferred Event Date", 125, 695); input_box(125, 735)
label("Attendance Type", 760, 695); input_box(760, 735)
draw.text((780, 750), "Choose an option", fill="#7b8794", font=small)
draw.polygon([(1245, 760), (1265, 760), (1255, 775)], fill="#52657a")
label("Session Preference", 125, 835)
radio(130, 880, "Morning")
radio(300, 880, "Afternoon")
radio(500, 880, "Either")
label("Accessibility needs", 760, 835)
checkbox(765, 880, "Wheelchair access")
checkbox(1010, 880, "Sign-language interpreter")

draw.line((125, 955, 1375, 955), fill="#d8e0ea", width=2)
label("Additional information", 125, 990)
label("Tell us about your goals", 125, 1045)
draw.rounded_rectangle((125, 1085, 1240, 1195), radius=7, fill="white", outline="#91a4ba", width=3)
checkbox(125, 1225, "I agree to the event terms and privacy policy")
draw.rounded_rectangle((1130, 1220, 1345, 1280), radius=8, fill="#2166d1")
draw.text((1180, 1235), "Submit", fill="white", font=regular)
image.save(OUT)
print(OUT)
