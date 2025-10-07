import pytesseract
from PIL import Image
import re

def extract_fields(text):
    # Normalize spaces and lines
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    result = {
        "Bank Name": "",
        "From": "",
        "To": "",
        "To Account": "",
        "Amount": "",
        "Reference": "",
        "Date": "",
        "Status": "",
        "Remarks": "",
        "Purpose": ""
    }

    # Find Bank Name
    for line in lines:
        if "MALDIVES ISLAMIC BANK" in line:
            result["Bank Name"] = "Maldives Islamic Bank"
            break
        elif "Bank of Maldives" in line:
            result["Bank Name"] = "Bank of Maldives"
            break

    # Find From & To
    from_to_pattern = re.compile(r'(Mohd\.? Niyaz|Mohamed Niyaz|MOHD\.NIYAZ|HAMID FAIZ|ALI NAJEEB|Saeeda Hussain Didi|Mom)[\s\-–]+(ALI NAJEEB|HAMID FAIZ|Saeeda Hussain Didi|Mom)', re.IGNORECASE)
    for idx, line in enumerate(lines):
        # Maldives Islamic Bank receipts
        if re.search(r'->|→', line):
            if idx > 0:
                result["From"] = lines[idx-1]
            if idx < len(lines)-1:
                result["To"] = lines[idx+1]
        # Bank of Maldives receipts
        m = re.match(r'From\s+(.*)', line)
        if m:
            result["From"] = m.group(1).strip()
        m = re.match(r'To\s+(.*)', line)
        if m:
            result["To"] = m.group(1).strip()

    # To Account
    for line in lines:
        m = re.match(r'To Account\s*([0-9]+)', line)
        if m:
            result["To Account"] = m.group(1)
        # Bank of Maldives format
        m = re.match(r'To\s+.*\s+([0-9]{9,})', line)
        if m and not result["To Account"]:
            result["To Account"] = m.group(1)
    
    # Amount
    for line in lines:
        if re.match(r'MVR\s*[0-9,]+\.\d{2}', line):
            result["Amount"] = line.replace('MVR', '').strip()
        elif re.match(r'[0-9,]+\.\d{2}\s*MVR', line):
            result["Amount"] = re.sub(r'\s*MVR', '', line).strip()
        elif re.match(r'Amount\s+MVR\s*[0-9,]+\.\d{2}', line):
            result["Amount"] = re.sub(r'Amount\s+MVR', '', line).strip()
    
    # Reference
    for line in lines:
        m = re.match(r'Reference\s*#?\s*([A-Z0-9]+)', line)
        if m:
            result["Reference"] = m.group(1)
        m = re.match(r'Reference\s*([A-Z0-9]+)', line)
        if m and not result["Reference"]:
            result["Reference"] = m.group(1)

    # Date
    for line in lines:
        m = re.match(r'Transaction Date\s*([\d\-\:\s]+)', line)
        if m:
            result["Date"] = m.group(1)
        m = re.match(r'Transaction date\s*([\d\/\s:]+)', line)
        if m and not result["Date"]:
            result["Date"] = m.group(1)
        m = re.match(r'Value Date\s*([\d\-\:\s]+)', line)
        if m and not result["Date"]:
            result["Date"] = m.group(1)

    # Status
    for line in lines:
        if 'SUCCESSFUL' in line.upper() or 'SUCCESS' in line.upper():
            result["Status"] = "SUCCESS"
        elif 'FAILED' in line.upper():
            result["Status"] = "FAILED"

    # Remarks / Purpose
    for line in lines:
        m = re.match(r'Purpose\s*(.+)', line)
        if m:
            result["Purpose"] = m.group(1).strip()
        m = re.match(r'Remarks\s*(.+)', line)
        if m:
            result["Remarks"] = m.group(1).strip()
        # Special case for Bank of Maldives
        if 'Rent of' in line or 'sticky cc do' in line:
            result["Purpose"] = line.strip()
        if 'Change' in line:
            result["Remarks"] = "Change"

    return result

def ocr_and_parse(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    fields = extract_fields(text)
    return fields

# Example usage:
if __name__ == "__main__":
    image_files = ["image1.jpg", "image2.png", "image3.png"]
    for img_path in image_files:
        data = ocr_and_parse(img_path)
        print(f"--- Data from {img_path} ---")
        for k, v in data.items():
            print(f"{k}: {v}")
        print()
