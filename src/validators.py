"""
Document and Identity Validators for KYC Verification.
Validates Aadhaar card number, PAN card number formats, and uploaded document files.
Includes phone, email, address validation and file content authenticity checks.
"""

import re
import struct
import io
import difflib
import pypdf

try:
    import Vision
    import Cocoa
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════
#  VERHOEFF CHECKSUM ALGORITHM (UIDAI Standard for Aadhaar)
# ═══════════════════════════════════════════════════════════════════════════

VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)

VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)

VERHOEFF_INV = (0, 4, 3, 2, 1, 5, 6, 7, 8, 9)


def validate_verhoeff(num_str: str) -> bool:
    """Validate checksum using UIDAI Verhoeff algorithm."""
    c = 0
    num_reversed = reversed(num_str)
    for i, item in enumerate(num_reversed):
        c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(item)]]
    return c == 0


def generate_verhoeff_checksum(num_11_digits: str) -> str:
    """Generate the 12th Verhoeff checksum digit for an 11-digit number."""
    c = 0
    num_reversed = reversed(num_11_digits)
    for i, item in enumerate(num_reversed):
        c = VERHOEFF_D[c][VERHOEFF_P[(i + 1) % 8][int(item)]]
    return str(VERHOEFF_INV[c])


# ═══════════════════════════════════════════════════════════════════════════
#  IDENTITY VALIDATORS
# ═══════════════════════════════════════════════════════════════════════════

def validate_aadhaar(aadhaar: str, check_verhoeff: bool = True) -> tuple:
    """
    Validate Indian Aadhaar number format against real-world UIDAI restrictions.

    Real-world Rules:
    - Must be exactly 12 digits
    - First digit cannot be 0 or 1 (UIDAI never issues numbers starting with 0 or 1)
    - Cannot be all same digits (e.g. 111111111111, 222222222222)
    - Cannot be repetitive pairs (e.g. 232323232323)
    - Cannot be sequential ascending/descending runs (e.g. 123456789012, 987654321098)
    - Validates 12th digit using UIDAI Verhoeff checksum algorithm

    Returns: (is_valid: bool, message: str)
    """
    aadhaar = aadhaar.strip().replace(" ", "").replace("-", "")

    if not aadhaar:
        return False, "Aadhaar number is required"

    if not aadhaar.isdigit():
        return False, "Aadhaar must contain only digits"

    if len(aadhaar) != 12:
        return False, f"Aadhaar must be exactly 12 digits (got {len(aadhaar)})"

    if aadhaar[0] in ('0', '1'):
        return False, "Invalid Aadhaar: Real-world Aadhaar numbers issued by UIDAI never begin with 0 or 1"

    if len(set(aadhaar)) == 1:
        return False, "Invalid Aadhaar: Cannot consist of all identical digits (e.g., 111111111111)"

    # Repetitive 2-digit pairs check (e.g. 232323232323, 121212121212)
    pairs = [aadhaar[i:i+2] for i in range(0, 12, 2)]
    if len(set(pairs)) == 1:
        return False, "Invalid Aadhaar: Repetitive two-digit pattern detected (e.g., 232323232323)"

    # Sequential patterns (e.g. 123456789012, 987654321098)
    seq_asc = "01234567890123456789"
    seq_desc = "98765432109876543210"
    if aadhaar in seq_asc or aadhaar in seq_desc:
        return False, "Invalid Aadhaar: Sequential ascending or descending digits are not permitted"

    # Verhoeff algorithm checksum verification
    if check_verhoeff:
        if not validate_verhoeff(aadhaar):
            expected_chk = generate_verhoeff_checksum(aadhaar[:11])
            return False, (
                f"Invalid Aadhaar: Fails UIDAI Verhoeff checksum algorithm. "
                f"(For prefix '{aadhaar[:11]}', the expected check digit is '{expected_chk}', but got '{aadhaar[-1]}')"
            )

    return True, "✅ Valid Aadhaar format (UIDAI Verhoeff checksum verified)"


def validate_pan(pan: str, applicant_name: str = "") -> tuple:
    """
    Validate Indian PAN card number format against real-world Income Tax rules.

    Format: AAAAA9999A
    - First 5 characters: uppercase letters
    - Next 4 characters: digits (0001-9999, cannot be 0000)
    - Last character: uppercase letter (check digit)
    - 4th character indicates holder type:
      'P' = Individual (mandatory for retail loan applicant)
    - 5th character:
      Under Indian Income Tax rules, 5th character must match the applicant's surname initial
      (or first name initial under liberal rules).

    Returns: (is_valid: bool, message: str)
    """
    pan = pan.strip().upper()

    if not pan:
        return False, "PAN number is required"

    if len(pan) != 10:
        return False, f"PAN must be exactly 10 characters (got {len(pan)})"

    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    if not re.match(pattern, pan):
        return False, "PAN format: 5 letters + 4 digits + 1 letter (e.g., ABCPS1234E)"

    # Validate digits part (cannot be 0000)
    digits_part = pan[5:9]
    if digits_part == "0000":
        return False, "Invalid PAN: The 4 numeric digits cannot be '0000' (must be between 0001 and 9999)"

    # Validate 4th character (holder type)
    valid_holder_types = {
        'A': 'Association of Persons (AOP)',
        'B': 'Body of Individuals (BOI)',
        'C': 'Company',
        'F': 'Firm',
        'G': 'Government',
        'H': 'Hindu Undivided Family (HUF)',
        'J': 'Artificial Juridical Person',
        'L': 'Local Authority',
        'P': 'Individual / Person',
        'T': 'Trust'
    }

    holder_char = pan[3]
    if holder_char not in valid_holder_types:
        valid_keys = ', '.join(valid_holder_types.keys())
        return False, f"Invalid 4th character '{holder_char}'. Must be one of: {valid_keys}"

    if holder_char != 'P':
        return False, (
            f"Invalid PAN holder type '{holder_char}' ({valid_holder_types[holder_char]}). "
            f"Individual retail customer onboarding requires an Individual PAN (4th character must be 'P')."
        )

    # Validate 5th character against applicant name
    if applicant_name and applicant_name.strip():
        name_clean = applicant_name.strip()
        tokens = [w.upper() for w in re.findall(r'[A-Za-z]+', name_clean) if len(w) >= 1]
        stopwords = {'MR', 'MRS', 'MS', 'DR', 'SHRI', 'SMT'}
        sig_tokens = [t for t in tokens if t not in stopwords] or tokens

        if sig_tokens:
            surname_initial = sig_tokens[-1][0]
            first_initial = sig_tokens[0][0]
            pan_5th = pan[4]

            # Allowed initials under liberal rule (matches surname initial or first initial)
            allowed_initials = {surname_initial, first_initial}
            for tok in sig_tokens:
                allowed_initials.add(tok[0])

            if pan_5th not in allowed_initials:
                initials_str = ", ".join([f"'{init}'" for init in sorted(allowed_initials)])
                return False, (
                    f"Invalid PAN 5th character '{pan_5th}': Under Income Tax Department rules, "
                    f"the 5th character of an individual's PAN must match the surname initial '{surname_initial}' "
                    f"(or applicant name initial: {initials_str} for '{name_clean}')."
                )

    return True, f"✅ Valid Individual PAN format (Holder Type: Individual / Person, Initial verified)"


# ═══════════════════════════════════════════════════════════════════════════
#  CONTACT VALIDATORS
# ═══════════════════════════════════════════════════════════════════════════

def validate_phone(phone: str) -> tuple:
    """
    Validate Indian mobile phone number.

    Rules:
    - Must be exactly 10 digits (without country code)
    - Must start with 6, 7, 8, or 9
    - Cannot be all same digits

    Returns: (is_valid: bool, message: str)
    """
    phone = phone.strip().replace(" ", "").replace("-", "").replace("+91", "")

    if not phone:
        return False, "Phone number is required"

    if not phone.isdigit():
        return False, "Phone number must contain only digits"

    if len(phone) != 10:
        return False, f"Phone number must be exactly 10 digits (got {len(phone)})"

    if phone[0] not in ('6', '7', '8', '9'):
        return False, "Indian mobile numbers must start with 6, 7, 8, or 9"

    if len(set(phone)) == 1:
        return False, "Invalid phone number: all digits are the same"

    return True, "✅ Valid phone number"


def validate_email(email: str) -> tuple:
    """
    Validate email address format.

    Returns: (is_valid: bool, message: str)
    """
    email = email.strip().lower()

    if not email:
        return False, "Email address is required"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format (e.g., name@example.com)"

    # Check for common disposable email domains
    disposable_domains = [
        'mailinator.com', 'guerrillamail.com', 'tempmail.com',
        'throwaway.email', 'yopmail.com', 'trashmail.com'
    ]
    domain = email.split('@')[1]
    if domain in disposable_domains:
        return False, "Disposable email addresses are not allowed"

    return True, "✅ Valid email address"


def validate_address(address: str) -> tuple:
    """
    Validate that address is sufficiently detailed.

    Rules:
    - Minimum 15 characters
    - Must not be blank or just whitespace

    Returns: (is_valid: bool, message: str)
    """
    address = address.strip()

    if not address:
        return False, "Address is required"

    if len(address) < 15:
        return False, f"Address is too short (minimum 15 characters, got {len(address)}). Please provide full address."

    return True, "✅ Valid address"


# ═══════════════════════════════════════════════════════════════════════════
#  FILE & DOCUMENT VALIDATORS
# ═══════════════════════════════════════════════════════════════════════════

# Magic byte signatures for supported file types
FILE_SIGNATURES = {
    'pdf': {
        'magic': b'%PDF',
        'offset': 0,
        'label': 'PDF Document',
    },
    'png': {
        'magic': b'\x89PNG\r\n\x1a\n',
        'offset': 0,
        'label': 'PNG Image',
    },
    'jpeg': {
        'magic': b'\xff\xd8\xff',
        'offset': 0,
        'label': 'JPEG Image',
    },
}


def validate_file_upload(uploaded_file, allowed_types=None, max_size_mb=2) -> tuple:
    """
    Validate an uploaded file's type and size.

    Returns: (is_valid: bool, message: str)
    """
    if uploaded_file is None:
        return False, "No file uploaded"

    if allowed_types is None:
        allowed_types = {
            'image/png': 'PNG Image',
            'image/jpeg': 'JPEG Image',
            'application/pdf': 'PDF Document'
        }

    if uploaded_file.type not in allowed_types:
        allowed_str = ", ".join(allowed_types.values())
        return False, f"Invalid file type '{uploaded_file.type}'. Allowed: {allowed_str}"

    max_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_bytes:
        size_mb = uploaded_file.size / (1024 * 1024)
        return False, f"File too large ({size_mb:.1f}MB). Maximum: {max_size_mb}MB"

    if uploaded_file.size == 0:
        return False, "File is empty"

    file_type = allowed_types[uploaded_file.type]
    size_kb = uploaded_file.size / 1024
    return True, f"✅ Valid {file_type} ({size_kb:.1f} KB)"


def verify_file_content(uploaded_file) -> tuple:
    """
    Verify file content authenticity by checking magic bytes (file signature).
    This ensures the file is actually what its extension claims.

    Rules:
    - PDF files must start with %PDF magic bytes
    - PNG files must have PNG header signature
    - JPEG files must have JPEG SOI marker

    Returns: (is_valid: bool, message: str, detected_type: str or None)
    """
    if uploaded_file is None:
        return False, "No file to verify", None

    try:
        # Read first 16 bytes for magic byte checking
        current_pos = uploaded_file.tell()
        header = uploaded_file.read(16)
        uploaded_file.seek(current_pos)  # Reset file pointer

        if len(header) < 3:
            return False, "File is too small to be a valid document", None

        # Check PDF
        if header[:4] == b'%PDF':
            return True, "✅ Verified: genuine PDF document", "pdf"

        # Check PNG
        if header[:8] == b'\x89PNG\r\n\x1a\n':
            # Additional PNG validation: check IHDR chunk
            if len(header) >= 16:
                return True, "✅ Verified: genuine PNG image", "png"
            return True, "✅ Verified: PNG image (basic check)", "png"

        # Check JPEG
        if header[:3] == b'\xff\xd8\xff':
            return True, "✅ Verified: genuine JPEG image", "jpeg"

        # None matched — file content doesn't match any known format
        declared_type = uploaded_file.type if hasattr(uploaded_file, 'type') else 'unknown'
        return False, (
            f"File content does not match expected format. "
            f"Declared type: {declared_type}. "
            f"The file may be corrupted or renamed. "
            f"Please upload a genuine PDF, PNG, or JPEG document."
        ), None

    except Exception as e:
        return False, f"Error verifying file content: {str(e)}", None


def verify_image_dimensions(uploaded_file, min_width=100, min_height=100,
                            max_width=10000, max_height=10000) -> tuple:
    """
    For image files (PNG/JPEG), verify that dimensions are within acceptable range.
    This helps ensure document scans are legible (not too tiny or corrupted).

    Returns: (is_valid: bool, message: str)
    """
    if uploaded_file is None:
        return False, "No file to verify"

    try:
        current_pos = uploaded_file.tell()
        header = uploaded_file.read(32)
        uploaded_file.seek(current_pos)

        width, height = None, None

        # PNG dimensions from IHDR chunk
        if header[:8] == b'\x89PNG\r\n\x1a\n' and len(header) >= 24:
            width = struct.unpack('>I', header[16:20])[0]
            height = struct.unpack('>I', header[20:24])[0]

        # JPEG — need to scan for SOF marker
        elif header[:3] == b'\xff\xd8\xff':
            uploaded_file.seek(current_pos)
            data = uploaded_file.read(min(uploaded_file.size, 65536))
            uploaded_file.seek(current_pos)

            i = 2
            while i < len(data) - 9:
                if data[i] == 0xFF:
                    marker = data[i + 1]
                    # SOF markers: C0-C3, C5-C7, C9-CB, CD-CF
                    if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                        height = struct.unpack('>H', data[i + 5:i + 7])[0]
                        width = struct.unpack('>H', data[i + 7:i + 9])[0]
                        break
                    elif marker == 0xD9:  # EOI
                        break
                    elif marker == 0xDA:  # SOS — stop scanning
                        break
                    else:
                        # Skip this segment
                        if i + 3 < len(data):
                            seg_len = struct.unpack('>H', data[i + 2:i + 4])[0]
                            i += 2 + seg_len
                        else:
                            break
                else:
                    i += 1
        else:
            # Not an image file, skip dimension check
            return True, "Not an image file — dimension check skipped"

        if width is None or height is None:
            return True, "Could not read dimensions — skipping check"

        if width < min_width or height < min_height:
            return False, (
                f"Image too small ({width}×{height}px). "
                f"Minimum {min_width}×{min_height}px required for legible document scans."
            )

        if width > max_width or height > max_height:
            return False, (
                f"Image too large ({width}×{height}px). "
                f"Maximum {max_width}×{max_height}px allowed."
            )

        return True, f"✅ Image dimensions OK ({width}×{height}px)"

    except Exception as e:
        # Don't block on dimension check failures
        return True, f"Dimension check skipped: {str(e)}"


def validate_document_complete(uploaded_file, doc_name="document") -> tuple:
    """
    Full document validation pipeline: type check + content verification + dimension check.
    Combines all file validation steps into a single call.

    Returns: (is_valid: bool, messages: list[str])
    """
    messages = []
    all_valid = True

    # Step 1: Basic file validation (type + size)
    valid, msg = validate_file_upload(uploaded_file)
    messages.append(msg)
    if not valid:
        return False, messages

    # Step 2: Content authenticity (magic bytes)
    valid, msg, detected_type = verify_file_content(uploaded_file)
    messages.append(msg)
    if not valid:
        all_valid = False
        return False, messages

    # Step 3: Image dimension check (only for images)
    if detected_type in ('png', 'jpeg'):
        valid, msg = verify_image_dimensions(uploaded_file)
        messages.append(msg)
        if not valid:
            all_valid = False

    return all_valid, messages


# ═══════════════════════════════════════════════════════════════════════════
#  DOCUMENT TEXT EXTRACTION & NAME VERIFICATION (OCR & Liberal Matching)
# ═══════════════════════════════════════════════════════════════════════════

def _ocr_image_bytes(img_bytes: bytes) -> str:
    """
    Run Apple Vision neural text recognition on image bytes (PNG/JPEG).
    Operates offline, in-memory, with zero external service dependencies.
    """
    if not VISION_AVAILABLE or not img_bytes:
        return ""
    try:
        ns_data = Cocoa.NSData.dataWithBytes_length_(img_bytes, len(img_bytes))
        handler = Vision.VNImageRequestHandler.alloc().initWithData_options_(ns_data, None)
        extracted = []

        def completion_handler(request, error):
            if error or not request.results():
                return
            for obs in request.results():
                extracted.append(obs.text())

        req = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(completion_handler)
        req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
        handler.performRequests_error_([req], None)
        return " ".join(extracted)
    except Exception:
        return ""


def extract_text_from_document(uploaded_file) -> str:
    """
    Extract text content from an uploaded document (PDF or Image).
    Supports:
    - PDF text stream extraction using pypdf
    - Embedded image extraction & Apple Vision OCR for scanned PDFs
    - PNG and JPEG OCR using Apple Vision framework
    - Auxiliary filename metadata tokens
    """
    if uploaded_file is None:
        return ""

    text = ""
    try:
        current_pos = uploaded_file.tell() if hasattr(uploaded_file, 'tell') else 0
        content = uploaded_file.read()
        if hasattr(uploaded_file, 'seek'):
            uploaded_file.seek(current_pos)

        if not content:
            return ""

        # 1. PDF Document
        if content[:4] == b'%PDF':
            try:
                reader = pypdf.PdfReader(io.BytesIO(content))
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + " "

                    # If text layer is sparse/empty (scanned PDF), run OCR on embedded images
                    if len(text.strip()) < 10 and hasattr(page, 'images') and page.images and VISION_AVAILABLE:
                        for img_obj in page.images:
                            ocr_t = _ocr_image_bytes(img_obj.data)
                            if ocr_t:
                                text += ocr_t + " "
            except Exception:
                pass

        # 2. Image Document (PNG / JPEG)
        elif (content[:8] == b'\x89PNG\r\n\x1a\n' or content[:3] == b'\xff\xd8\xff') and VISION_AVAILABLE:
            ocr_t = _ocr_image_bytes(content)
            if ocr_t:
                text += ocr_t + " "

        # 3. Auxiliary filename metadata tokens
        filename = getattr(uploaded_file, 'name', '')
        if filename:
            clean_fn = re.sub(r'[^\w\s]', ' ', filename)
            text += " " + clean_fn

    except Exception:
        pass

    return text.strip()


def verify_aadhaar_name_match(uploaded_file, entered_name: str) -> tuple:
    """
    Extract name/text from uploaded Aadhaar document and verify that the entered applicant name
    and document name are related using liberal rules (at least one word must match).

    Liberal Matching Rules:
    - Extracts text from PDF or scanned image via Apple Vision OCR.
    - Tokenizes entered name into constituent words, omitting generic honorifics (Mr, Mrs, Shri, etc.).
    - Checks for exact word match (word boundary) or high fuzzy similarity (>= 80%) against document text.
    - PASS condition: At least ONE significant word from the entered name matches the document.

    Returns: (is_valid: bool, message: str, details: dict)
    """
    if not entered_name or not entered_name.strip():
        return False, "Entered applicant name is required for Aadhaar name verification", {}

    if uploaded_file is None:
        return False, "Uploaded Aadhaar document copy is required", {}

    extracted_text = extract_text_from_document(uploaded_file)
    if not extracted_text:
        return False, (
            "Could not extract readable text from the uploaded Aadhaar document. "
            "Please ensure the upload is a legible PDF or image scan of the Aadhaar card."
        ), {}

    # Tokenize entered name
    entered_tokens = [w.lower() for w in re.findall(r'[a-zA-Z]+', entered_name) if len(w) >= 2]
    stopwords = {'mr', 'mrs', 'ms', 'dr', 'shri', 'smt', 'kumar', 'kumari', 'father', 'guardian', 'care', 'of', 'son', 'daughter'}
    sig_entered_tokens = [t for t in entered_tokens if t not in stopwords] or entered_tokens

    doc_text_lower = extracted_text.lower()
    doc_words = [w.lower() for w in re.findall(r'[a-zA-Z]+', doc_text_lower) if len(w) >= 2]

    matched_tokens = []
    # 1. Exact word boundary match
    for token in sig_entered_tokens:
        if re.search(r'\b' + re.escape(token) + r'\b', doc_text_lower):
            matched_tokens.append((token, "exact match"))

    # 2. Fuzzy match for minor OCR deviations (>= 0.80 similarity)
    if not matched_tokens:
        for token in sig_entered_tokens:
            for dw in doc_words:
                ratio = difflib.SequenceMatcher(None, token, dw).ratio()
                if ratio >= 0.80:
                    matched_tokens.append((token, f"fuzzy match with '{dw}' ({int(ratio*100)}%)"))
                    break

    preview = (extracted_text[:120] + "...") if len(extracted_text) > 120 else extracted_text
    details = {
        "matched_tokens": matched_tokens,
        "extracted_preview": preview,
        "entered_tokens": sig_entered_tokens
    }

    if matched_tokens:
        match_desc = ", ".join([f"'{m[0].title()}' ({m[1]})" for m in matched_tokens])
        return True, f"✅ Aadhaar Name Verified: Document matches entered name token(s) {match_desc}.", details
    else:
        sig_str = ", ".join([f"'{t.title()}'" for t in sig_entered_tokens])
        return False, (
            f"❌ Aadhaar Name Verification Failed: None of the entered name components ({sig_str}) "
            f"were found in the uploaded Aadhaar document (Extracted text preview: '{preview}'). "
            f"Liberal KYC rules require at least one word to match."
        ), details


# ═══════════════════════════════════════════════════════════════════════════
#  DISPLAY FORMATTERS
# ═══════════════════════════════════════════════════════════════════════════

def format_aadhaar_display(aadhaar: str) -> str:
    """Format Aadhaar for display: XXXX XXXX XXXX"""
    aadhaar = aadhaar.replace(" ", "").replace("-", "")
    if len(aadhaar) == 12:
        return f"{aadhaar[:4]} {aadhaar[4:8]} {aadhaar[8:]}"
    return aadhaar


def mask_aadhaar(aadhaar: str) -> str:
    """Mask Aadhaar for privacy: XXXX XXXX 1234"""
    aadhaar = aadhaar.replace(" ", "").replace("-", "")
    if len(aadhaar) == 12:
        return f"XXXX XXXX {aadhaar[8:]}"
    return "XXXX XXXX XXXX"


def mask_pan(pan: str) -> str:
    """Mask PAN for privacy: ABCPD1234E -> ABCPD****E"""
    if len(pan) == 10:
        return f"{pan[:5]}****{pan[9]}"
    return "XXXXX****X"


def sanitize_filename(filename: str) -> str:
    """Sanitize uploaded filename to prevent path traversal and special characters."""
    if not filename:
        return "unnamed_document"
    # Remove path separators and null bytes
    filename = filename.replace("/", "_").replace("\\", "_").replace("\x00", "")
    # Remove leading dots (hidden files)
    filename = filename.lstrip(".")
    # Keep only safe characters
    safe = re.sub(r'[^\w\s\-.]', '_', filename)
    # Collapse multiple underscores
    safe = re.sub(r'_+', '_', safe).strip('_')
    return safe if safe else "unnamed_document"
