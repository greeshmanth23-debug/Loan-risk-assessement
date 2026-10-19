"""
Insert or update mock customer data for testing the Loan Risk Assessment System.
Provides:
1. 'Rahul Sharma' — Fully verified KYC with all 3 mandatory documents (Aadhaar, PAN, Salary Slip).
   Eligible for Loan Risk Evaluation.
2. 'Amit Verma' — Pending KYC (missing documents).
   Locked from Loan Risk Evaluation until documents are uploaded and verified.
"""
import io
import struct
import datetime
from src.database import DatabaseManager


class MockDocFile:
    def __init__(self, name, content_type, data_bytes):
        self.name = name
        self.type = content_type
        self.size = len(data_bytes)
        self._buf = io.BytesIO(data_bytes)

    def read(self, *args):
        return self._buf.read(*args)

    def seek(self, pos, whence=0):
        return self._buf.seek(pos, whence)

    def tell(self):
        return self._buf.tell()


db = DatabaseManager()

if not db.connected:
    print("❌ MongoDB is not running. Start MongoDB first.")
    exit(1)

# Generate mock document files with valid magic bytes
pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
ihdr_data = struct.pack(">IIBBBBB", 200, 200, 8, 2, 0, 0, 0)
png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR" + ihdr_data + b"\x00\x00\x00\x00IEND\xaeB`\x82"

docs_rahul = {
    "aadhaar": MockDocFile("aadhaar_rahul_sharma.pdf", "application/pdf", pdf_bytes),
    "pan": MockDocFile("pan_rahul_sharma.png", "image/png", png_bytes),
    "salary_slip": MockDocFile("salary_slip_rahul_sharma.pdf", "application/pdf", pdf_bytes),
}

# 1. Update or Insert Rahul Sharma (Fully Verified)
rahul_existing = db.get_customer_by_name("Rahul Sharma")
if rahul_existing:
    print("🔄 Updating existing 'Rahul Sharma' with full KYC documents...")
    db.upload_customer_documents(str(rahul_existing["_id"]), docs_rahul)
    db.update_kyc_status(str(rahul_existing["_id"]), "verified", "All 3 required KYC documents verified.")
    print("✅ 'Rahul Sharma' updated to KYC VERIFIED with all 3 documents.")
else:
    rahul_data = {
        "name": "Rahul Sharma",
        "father_name": "Rajesh Sharma",
        "dob": datetime.datetime(1992, 5, 15),
        "age": 34,
        "gender": "Male",
        "marital_status": "Married",
        "employment_type": "Salaried - Private",
        "phone_number": "9876543210",
        "email": "rahul.sharma@example.com",
        "address": "42 Residency Road, Koramangala, Bangalore, Karnataka 560034",
        "monthly_income": 85000,
        "monthly_debt_payment": 12000,
        "credit_score": 750,
        "previous_loans": 2,
        "previous_defaults": 0,
        "aadhaar_number": "234567890123",
        "pan_number": "ABCPD1234E",
        "aadhaar_verified": True,
        "pan_verified": True,
        "phone_verified": True,
        "email_verified": True,
        "salary_slip_uploaded": True,
        "kyc_status": "verified",
    }
    inserted_id, error = db.add_customer(rahul_data, docs_rahul)
    if error:
        print(f"❌ Error inserting Rahul Sharma: {error}")
    else:
        print(f"✅ Mock customer 'Rahul Sharma' (VERIFIED) inserted with ID: {inserted_id}")

# 2. Update or Insert Amit Verma (Pending / Incomplete KYC)
amit_existing = db.get_customer_by_name("Amit Verma")
if not amit_existing:
    amit_data = {
        "name": "Amit Verma",
        "father_name": "Suresh Verma",
        "dob": datetime.datetime(1996, 8, 20),
        "age": 30,
        "gender": "Male",
        "marital_status": "Single",
        "employment_type": "Self-Employed",
        "phone_number": "9811223344",
        "email": "amit.verma@example.com",
        "address": "15 Park Avenue, Indiranagar, Bangalore, Karnataka 560038",
        "monthly_income": 45000,
        "monthly_debt_payment": 15000,
        "credit_score": 620,
        "previous_loans": 1,
        "previous_defaults": 0,
        "aadhaar_number": "345678901234",
        "pan_number": "XYZPD5678G",
        "aadhaar_verified": True,
        "pan_verified": True,
        "phone_verified": True,
        "email_verified": True,
        "salary_slip_uploaded": False,
        "kyc_status": "pending",
        "documents": {}  # Missing documents!
    }
    inserted_id_amit, error_amit = db.add_customer(amit_data)
    if error_amit:
        print(f"❌ Error inserting Amit Verma: {error_amit}")
    else:
        print(f"✅ Mock customer 'Amit Verma' (PENDING / LOCKED) inserted with ID: {inserted_id_amit}")
else:
    print("ℹ️  Mock customer 'Amit Verma' already exists.")

print("\n🚀 Ready for testing:")
print("  - Search 'Amit Verma'  → Demonstrates LOCKED Loan Risk Evaluation (KYC Incomplete)")
print("  - Search 'Rahul Sharma' → Demonstrates VERIFIED KYC and Unlocked Loan Risk Evaluation")
