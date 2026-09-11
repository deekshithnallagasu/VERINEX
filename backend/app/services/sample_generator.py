import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from ..config import SAMPLES_DIR

def draw_grid_pattern(draw, width, height, color=(220, 230, 242)):
    """Draws subtle guilloche-like security waves / grid in background"""
    for y in range(0, height, 18):
        draw.line([(0, y), (width, y + 10)], fill=color, width=1)
    for x in range(0, width, 25):
        draw.line([(x, 0), (x + 15, height)], fill=color, width=1)

def draw_specimen_watermark(draw, width, height):
    """Adds clear non-deceptive watermark overlay"""
    draw.rectangle([(width - 290, 10), (width - 15, 38)], fill=(220, 38, 38, 200), outline=(185, 28, 28))
    draw.text((width - 280, 16), "FICTIONAL TEST SPECIMEN", fill=(255, 255, 255))

def generate_sample_documents():
    """
    Programmatically creates 4 high-quality fictional identity document images.
    Strictly defensive fictional demo materials.
    """
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Clean Fictional Passport (Low Risk)
    p1 = SAMPLES_DIR / "sample_passport_clean.png"
    if not p1.exists():
        w, h = 860, 560
        img = Image.new("RGB", (w, h), color=(245, 248, 253))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (220, 235, 250))
        
        # Header banner
        draw.rectangle([(0, 0), (w, 65)], fill=(15, 32, 67))
        draw.text((30, 20), "PASSPORT  /  PASSEPORT", fill=(255, 255, 255))
        draw.text((280, 20), "UNITED STATES OF AMERICA", fill=(200, 225, 255))
        draw_specimen_watermark(draw, w, h)

        # Photo frame & avatar silhouette
        draw.rectangle([(40, 95), (230, 340)], fill=(210, 220, 235), outline=(100, 120, 150), width=2)
        # Head & shoulders
        draw.ellipse([(95, 130), (175, 210)], fill=(140, 160, 190))
        draw.ellipse([(65, 220), (205, 340)], fill=(120, 140, 175))
        draw.text((50, 315), "AUTHENTIC PHOTO", fill=(70, 90, 120))

        # Text fields (Visual Inspection Zone)
        fields = [
            ("Type / Type:", "P", "Code / Code:", "USA", "Passport No / No de Passeport:", "E84920194"),
            ("Surname / Nom:", "ABERNATHY", "", "", "", ""),
            ("Given Names / Prenoms:", "CLARA ELEANOR", "", "", "", ""),
            ("Nationality / Nationalite:", "UNITED STATES OF AMERICA", "", "", "", ""),
            ("Date of Birth / Date de Naissance:", "14 MAY 1989", "Sex / Sexe:", "F", "Place of Birth:", "CALIFORNIA, USA"),
            ("Date of Issue / Date de Delivrance:", "12 JUN 2019", "Authority / Autorite:", "U.S. DEPT OF STATE", "", ""),
            ("Date of Expiration / Date d'expiration:", "11 JUN 2029", "Endorsements:", "NONE", "", "")
        ]

        y_pos = 95
        for row in fields:
            draw.text((260, y_pos), row[0], fill=(100, 115, 135))
            draw.text((260, y_pos + 16), row[1], fill=(15, 23, 42))
            if row[2]:
                draw.text((520, y_pos), row[2], fill=(100, 115, 135))
                draw.text((520, y_pos + 16), row[3], fill=(15, 23, 42))
            if row[4]:
                draw.text((680, y_pos), row[4], fill=(100, 115, 135))
                draw.text((680, y_pos + 16), row[5], fill=(15, 23, 42))
            y_pos += 37

        # MRZ Zone
        draw.rectangle([(0, 420), (w, h)], fill=(235, 240, 248), outline=(190, 205, 225), width=2)
        mrz1 = "P<USAABERNATHY<<CLARA<ELEANOR<<<<<<<<<<<<<<<"
        mrz2 = "E849201943USA8905145F2906117<<<<<<<<<<<<<<04"
        draw.text((40, 445), mrz1, fill=(20, 25, 40))
        draw.text((40, 485), mrz2, fill=(20, 25, 40))

        img.save(p1)

    # 2. Expired Driver's License (Medium Risk)
    p2 = SAMPLES_DIR / "sample_license_expired.png"
    if not p2.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(250, 252, 255))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (230, 240, 245))

        # Green header for Washington State DL
        draw.rectangle([(0, 0), (w, 75)], fill=(22, 101, 52))
        draw.text((30, 15), "WASHINGTON", fill=(255, 255, 255))
        draw.text((30, 42), "DRIVER LICENSE / PERMIS DE CONDUIRE", fill=(200, 245, 215))
        draw_specimen_watermark(draw, w, h)

        # Photo frame
        draw.rectangle([(40, 100), (220, 330)], fill=(225, 235, 245), outline=(120, 140, 160), width=2)
        draw.ellipse([(85, 130), (175, 220)], fill=(130, 150, 175))
        draw.ellipse([(55, 230), (205, 330)], fill=(110, 130, 160))

        # Fields
        draw.text((250, 95), "DL NO:", fill=(100, 116, 139))
        draw.text((320, 95), "WDL82947102", fill=(15, 23, 42))

        # EXPIRED NOTICE ON CARD
        draw.rectangle([(550, 90), (740, 125)], fill=(254, 242, 242), outline=(239, 68, 68), width=2)
        draw.text((560, 98), "EXP: 2023-04-18 (EXPIRED)", fill=(185, 28, 28))

        draw.text((250, 140), "LN: VANCE", fill=(15, 23, 42))
        draw.text((250, 170), "FN: ARTHUR LIAM", fill=(15, 23, 42))
        draw.text((250, 205), "DOB: 1982-11-23", fill=(15, 23, 42))
        draw.text((450, 205), "SEX: M", fill=(15, 23, 42))
        draw.text((550, 205), "HGT: 5'-11\"", fill=(15, 23, 42))
        draw.text((250, 240), "ISS: 2017-04-19", fill=(15, 23, 42))
        draw.text((250, 275), "ADDR: 1042 NORTHWEST PINE ST, SEATTLE, WA 98101", fill=(15, 23, 42))
        draw.text((250, 310), "CLASS: D - STANDARD AUTO", fill=(71, 85, 105))

        # Barcode strip representation
        draw.rectangle([(40, 390), (w - 40, 480)], fill=(255, 255, 255), outline=(148, 163, 184))
        for x in range(50, w - 50, 6):
            draw.line([(x, 400), (x, 470)], fill=(30, 41, 59), width=(x % 3) + 1)

        img.save(p2)

    # 3. Tampered MRZ / Mismatched Identity Card (High Risk)
    p3 = SAMPLES_DIR / "sample_national_id_tampered.png"
    if not p3.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(253, 248, 248))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (245, 220, 220))

        # Red/Dark header
        draw.rectangle([(0, 0), (w, 65)], fill=(69, 10, 10))
        draw.text((30, 20), "REPUBLIC OF METROPOLIS  |  NATIONAL IDENTITY CARD", fill=(255, 255, 255))
        draw_specimen_watermark(draw, w, h)

        # Photo frame
        draw.rectangle([(40, 95), (220, 330)], fill=(230, 220, 220), outline=(180, 120, 120), width=2)
        draw.ellipse([(85, 130), (175, 220)], fill=(160, 120, 120))
        draw.ellipse([(55, 230), (205, 330)], fill=(140, 100, 100))

        # Printed visual text: Marcus Reid
        draw.text((250, 95), "SURNAME / NOM:", fill=(100, 116, 139))
        draw.text((250, 115), "REID", fill=(15, 23, 42))

        draw.text((250, 150), "GIVEN NAMES:", fill=(100, 116, 139))
        draw.text((250, 170), "MARCUS", fill=(15, 23, 42))

        draw.text((250, 205), "DOCUMENT NO:", fill=(100, 116, 139))
        draw.text((250, 225), "ID-90184712", fill=(15, 23, 42))

        draw.text((500, 205), "EXPIRY DATE:", fill=(100, 116, 139))
        draw.text((500, 225), "2028-08-14", fill=(15, 23, 42))

        draw.text((250, 260), "DATE OF BIRTH: 1994-08-15", fill=(15, 23, 42))
        draw.text((500, 260), "NATIONALITY: MET", fill=(15, 23, 42))

        # MRZ zone contains DIFFERENT NAME: DEVON JONES (Discrepancy)
        draw.rectangle([(0, 390), (w, h)], fill=(240, 235, 240), outline=(200, 170, 180), width=2)
        mrz1 = "I<MET90184712<<9<<<<<<<<<<<<<<"
        mrz2 = "9408155M2808143METJONES<<DEVON<8"
        draw.text((40, 420), mrz1, fill=(20, 25, 40))
        draw.text((40, 465), mrz2, fill=(20, 25, 40))

        img.save(p3)

    # 4. Low Quality / Blurry Residence Permit (Medium-High Risk)
    p4 = SAMPLES_DIR / "sample_residence_blurry.png"
    if not p4.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(240, 242, 245))
        draw = ImageDraw.Draw(img)

        # Header
        draw.rectangle([(0, 0), (w, 65)], fill=(30, 41, 59))
        draw.text((30, 20), "EUROPEAN UNION  /  RESIDENCE PERMIT", fill=(255, 255, 255))
        draw_specimen_watermark(draw, w, h)

        # Photo frame
        draw.rectangle([(40, 95), (220, 330)], fill=(200, 210, 220), outline=(130, 140, 150), width=2)
        draw.ellipse([(85, 130), (175, 220)], fill=(140, 150, 160))
        draw.ellipse([(55, 230), (205, 330)], fill=(120, 130, 140))

        # Faint text
        draw.text((250, 110), "NAME: HELENA SANTO", fill=(80, 90, 100))
        draw.text((250, 155), "DOB: 1991-03-20", fill=(80, 90, 100))
        draw.text((250, 200), "CARD NO: RC-448219", fill=(80, 90, 100))
        draw.text((250, 245), "VALID UNTIL: 2027-10-15", fill=(80, 90, 100))

        # Optical glare spot in the center
        for r in range(120, 0, -4):
            alpha = int((1 - (r / 120)) * 140)
            draw.ellipse([(450 - r, 200 - r), (450 + r, 200 + r)], fill=(255, 255, 255, alpha))

        # Apply Gaussian Blur filter to simulate unreadable / degraded photograph
        blurred = img.filter(ImageFilter.GaussianBlur(radius=3.8))
        blurred.save(p4)

    # 5. Fictional Aadhaar Card (Valid ID-1)
    p5 = SAMPLES_DIR / "sample_aadhaar.png"
    if not p5.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(253, 253, 255))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (235, 240, 245))

        # Top banner with Govt of India & UIDAI branding
        draw.rectangle([(0, 0), (w, 65)], fill=(234, 88, 12))  # Saffron header accent
        draw.text((30, 15), "GOVERNMENT OF INDIA", fill=(255, 255, 255))
        draw.text((30, 38), "UNIQUE IDENTIFICATION AUTHORITY OF INDIA", fill=(255, 240, 230))
        draw_specimen_watermark(draw, w, h)

        # Portrait zone
        draw.rectangle([(40, 95), (220, 330)], fill=(225, 235, 245), outline=(120, 140, 160), width=2)
        draw.ellipse([(85, 125), (175, 215)], fill=(140, 160, 185))
        draw.ellipse([(55, 225), (205, 330)], fill=(120, 140, 170))
        draw.text((50, 305), "HOLDER PHOTO", fill=(80, 100, 125))

        # Fields
        draw.text((250, 105), "To:", fill=(100, 115, 135))
        draw.text((250, 130), "RAJESH KUMAR SHARMA", fill=(15, 23, 42))
        draw.text((250, 170), "DOB: 12/08/1985", fill=(15, 23, 42))
        draw.text((250, 205), "Gender / Ling: Male / Purush", fill=(15, 23, 42))

        # 12-Digit UID Number
        draw.rectangle([(250, 260), (750, 320)], fill=(245, 248, 255), outline=(200, 215, 235))
        draw.text((320, 278), "1234  5678  9012", fill=(194, 65, 12))

        # Bottom slogan
        draw.rectangle([(0, 480), (w, h)], fill=(22, 101, 52))
        draw.text((280, 500), "Mera Aadhaar, Meri Pehchan", fill=(255, 255, 255))

        img.save(p5)

    # 6. Fictional PAN Card (Valid ID-1)
    p6 = SAMPLES_DIR / "sample_pan_card.png"
    if not p6.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(240, 248, 255))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (215, 230, 245))

        # Income Tax Dept header
        draw.rectangle([(0, 0), (w, 75)], fill=(30, 58, 138))
        draw.text((30, 15), "INCOME TAX DEPARTMENT", fill=(255, 255, 255))
        draw.text((30, 42), "GOVT. OF INDIA  /  PERMANENT ACCOUNT NUMBER CARD", fill=(200, 225, 255))
        draw_specimen_watermark(draw, w, h)

        # Portrait zone
        draw.rectangle([(40, 100), (220, 330)], fill=(220, 230, 245), outline=(100, 120, 150), width=2)
        draw.ellipse([(85, 130), (175, 220)], fill=(130, 150, 175))
        draw.ellipse([(55, 230), (205, 330)], fill=(110, 130, 160))

        # PAN fields
        draw.text((250, 100), "Permanent Account Number:", fill=(100, 116, 139))
        draw.text((250, 125), "ABCDE1234F", fill=(15, 23, 42))

        draw.text((250, 170), "Name:", fill=(100, 116, 139))
        draw.text((250, 195), "VIKRAM RAO", fill=(15, 23, 42))

        draw.text((250, 235), "Father's Name:", fill=(100, 116, 139))
        draw.text((250, 260), "SURESH RAO", fill=(15, 23, 42))

        draw.text((250, 300), "Date of Birth:", fill=(100, 116, 139))
        draw.text((250, 325), "24/11/1990", fill=(15, 23, 42))

        # Signature box
        draw.rectangle([(40, 370), (220, 440)], fill=(255, 255, 255), outline=(150, 160, 180))
        draw.line([(60, 410), (90, 390), (130, 420), (160, 395), (200, 415)], fill=(10, 20, 40), width=2)
        draw.text((80, 425), "Signature", fill=(140, 150, 170))

        img.save(p6)

    # 7. Fictional Voter ID Card (Valid ID-1)
    p7 = SAMPLES_DIR / "sample_voter_id.png"
    if not p7.exists():
        w, h = 860, 540
        img = Image.new("RGB", (w, h), color=(252, 250, 245))
        draw = ImageDraw.Draw(img)
        draw_grid_pattern(draw, w, h, (235, 230, 220))

        # Header
        draw.rectangle([(0, 0), (w, 75)], fill=(67, 56, 202))
        draw.text((30, 15), "ELECTION COMMISSION OF INDIA", fill=(255, 255, 255))
        draw.text((30, 42), "ELECTOR PHOTO IDENTITY CARD", fill=(225, 220, 255))
        draw_specimen_watermark(draw, w, h)

        # Portrait
        draw.rectangle([(40, 100), (220, 330)], fill=(235, 230, 225), outline=(130, 120, 110), width=2)
        draw.ellipse([(85, 130), (175, 220)], fill=(150, 140, 135))
        draw.ellipse([(55, 230), (205, 330)], fill=(130, 120, 115))

        # Fields
        draw.text((250, 100), "EPIC NO:", fill=(100, 116, 139))
        draw.text((350, 100), "WBM1948201", fill=(15, 23, 42))

        draw.text((250, 150), "Elector's Name:", fill=(100, 116, 139))
        draw.text((250, 175), "ANANYA DESHMUKH", fill=(15, 23, 42))

        draw.text((250, 215), "Father's Name:", fill=(100, 116, 139))
        draw.text((250, 240), "RAMESH DESHMUKH", fill=(15, 23, 42))

        draw.text((250, 280), "Sex: Female", fill=(15, 23, 42))
        draw.text((450, 280), "DOB: 15/07/1992", fill=(15, 23, 42))

        draw.text((250, 330), "Assembly Constituency: 142 - CENTRAL", fill=(71, 85, 105))

        img.save(p7)

    # 8. Signature Image Only (Non-Document / Rejected Input)
    p8 = SAMPLES_DIR / "sample_signature.png"
    if not p8.exists():
        w, h = 550, 220
        img = Image.new("RGB", (w, h), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        # Draw cursive ink strokes simulating a standalone signature
        points = [
            (40, 120), (70, 80), (95, 140), (120, 70), (150, 130),
            (180, 100), (210, 125), (240, 90), (280, 140), (320, 85),
            (360, 130), (410, 105), (460, 125), (490, 95)
        ]
        draw.line(points, fill=(15, 23, 42), width=4)
        # Add underline flourish
        draw.line([(60, 155), (470, 145)], fill=(15, 23, 42), width=3)
        img.save(p8)

    # 9. Blank Uniform Image (Invalid Input)
    p9 = SAMPLES_DIR / "sample_blank.png"
    if not p9.exists():
        w, h = 800, 600
        img = Image.new("RGB", (w, h), color=(252, 252, 252))
        img.save(p9)

    # 10. Random Scenic Photo without Identity Document Structure
    p10 = SAMPLES_DIR / "sample_random_photo.png"
    if not p10.exists():
        w, h = 800, 600
        img = Image.new("RGB", (w, h), color=(135, 206, 235))  # Sky blue
        draw = ImageDraw.Draw(img)
        # Sun
        draw.ellipse([(600, 50), (720, 170)], fill=(255, 223, 0))
        # Hills
        draw.polygon([(0, 600), (250, 300), (500, 600)], fill=(34, 139, 34))
        draw.polygon([(300, 600), (550, 250), (800, 600)], fill=(46, 139, 87))
        img.save(p10)

    return {
        "CLEAN_PASSPORT": str(p1),
        "EXPIRED_LICENSE": str(p2),
        "TAMPERED_MRZ_ID": str(p3),
        "BLURRY_CARD": str(p4),
        "VALID_AADHAAR": str(p5),
        "VALID_PAN": str(p6),
        "VALID_VOTER_ID": str(p7),
        "SAMPLE_SIGNATURE": str(p8),
        "SAMPLE_BLANK": str(p9),
        "SAMPLE_RANDOM_PHOTO": str(p10),
    }
