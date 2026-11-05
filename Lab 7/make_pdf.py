from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit

pages = [
    ("Step 2: Running the buggy processor.py",
     "Ran python processor.py on the original code. A malformed donor record (no pipe separators) crashed parse_donor_registry with an IndexError, because the code assumed the input always had 3 fields.",
     "s1.jpeg"),
    ("Step 4: Hypothesis tests failing on the buggy code",
     "Ran pytest test_processor.py. All 3 fuzz tests failed. Hypothesis found crashing inputs such as an empty string (IndexError) and None (AttributeError) for all three functions.",
     "s2.jpeg"),
    ("Step 5: Running the fixed processor.py",
     "After adding input validation, the same bad inputs (empty blood type, BP 120/0, malformed donor record) now return safe Invalid messages instead of crashing.",
     "s3.jpeg"),
    ("Step 6: Hypothesis tests passing on the fixed code",
     "Re-ran pytest test_processor.py against the fixed processor.py. All 3 tests passed.",
     "s4.jpeg"),
]

summary_title = "Summary of bugs found and fixes"
summary = [
    "validate_blood_type: crashed on None, empty or 1-character input and on invalid codes (KeyError). Fix: check the type, minimum length, valid antigen (A, B, AB, O) and Rh sign (+ or -).",
    "calculate_pulse_pressure: crashed on None, missing slash, non-numeric values and diastolic = 0 (ZeroDivisionError). Fix: check the type, split into exactly 2 parts, wrap int() in try/except, and require positive values.",
    "parse_donor_registry: crashed on None, wrong number of fields and non-numeric values. Fix: check the type, require exactly 3 fields, a non-empty ID, finite positive numbers (rejects nan and inf).",
    "All three functions now return a clear Invalid message instead of raising an exception.",
]

c = canvas.Canvas("Lab7_Screenshots.pdf", pagesize=A4)
W, H = A4
m = 40
for title, text, img in pages:
    c.setFont("Helvetica-Bold", 16)
    c.drawString(m, H - 60, title)
    c.setFont("Helvetica", 11)
    y = H - 85
    for line in simpleSplit(text, "Helvetica", 11, W - 2 * m):
        c.drawString(m, y, line)
        y -= 15
    ir = ImageReader(img)
    iw, ih = ir.getSize()
    s = min((W - 2 * m) / iw, (y - m - 10) / ih)
    c.drawImage(ir, m, y - 10 - ih * s, iw * s, ih * s)
    c.showPage()

c.setFont("Helvetica-Bold", 16)
c.drawString(m, H - 60, summary_title)
c.setFont("Helvetica", 11)
y = H - 90
for item in summary:
    for line in simpleSplit("- " + item, "Helvetica", 11, W - 2 * m):
        c.drawString(m, y, line)
        y -= 15
    y -= 10
c.showPage()
c.save()
