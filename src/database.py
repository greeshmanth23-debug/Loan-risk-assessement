"""
MongoDB Database Manager for Loan Risk Assessment System.
Handles customer registration, document storage, and loan application tracking.
"""

import base64
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from bson import ObjectId

from src.validators import sanitize_filename


DEFAULT_MONGO_URI = "mongodb+srv://ravurivenkatesh279_db_user:Greesh123@loanriskassessment.f7e036t.mongodb.net/loanriskmodel?retryWrites=true&w=majority"


class DatabaseManager:
    """Manages all MongoDB operations for the Loan Risk Assessment System."""

    def __init__(self, uri=None):
        self.uri = uri or DEFAULT_MONGO_URI
        self.client = None
        self.db = None
        self.connected = False
        self._connect()

    def _connect(self):
        """Establish MongoDB connection with error handling."""
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client.get_database()
            self.connected = True
            self._ensure_indexes()
        except (ConnectionFailure, Exception):
            self.connected = False

    def _ensure_indexes(self):
        """Create necessary indexes for performance."""
        if not self.connected:
            return
        try:
            self.db.customers.create_index("name")
            self.db.customers.create_index("aadhaar_number", unique=True, sparse=True)
            self.db.customers.create_index("pan_number", unique=True, sparse=True)
            self.db.customers.create_index("phone_number", unique=True, sparse=True)
            self.db.customers.create_index("email", unique=True, sparse=True)
            self.db.loan_applications.create_index("customer_name")
            self.db.loan_applications.create_index("created_at")
        except Exception:
            pass

    # ── Customer Operations ──────────────────────────────────────────────

    def add_customer(self, customer_data, documents=None):
        """
        Register a new customer with optional document uploads.
        Documents are stored as base64-encoded data in the document.
        Filenames are sanitized before storage.

        Returns: (inserted_id_str or None, error_message or None)
        """
        if not self.connected:
            return None, "MongoDB is not connected. Please check your database server."

        customer_data.pop("_id", None)
        customer_data["created_at"] = datetime.utcnow()
        customer_data["updated_at"] = datetime.utcnow()
        customer_data["status"] = "active"

        # Set default KYC status based on document verification
        if "kyc_status" not in customer_data:
            customer_data["kyc_status"] = "pending"

        if documents:
            doc_storage = {}
            for doc_name, doc_file in documents.items():
                if doc_file is not None:
                    content = doc_file.read()
                    doc_file.seek(0)
                    doc_storage[doc_name] = {
                        "filename": sanitize_filename(doc_file.name),
                        "content_type": doc_file.type,
                        "data": base64.b64encode(content).decode('utf-8'),
                        "size_bytes": len(content),
                        "uploaded_at": datetime.utcnow()
                    }
            customer_data["documents"] = doc_storage

        try:
            result = self.db.customers.insert_one(customer_data)
            return str(result.inserted_id), None
        except DuplicateKeyError as e:
            err_str = str(e)
            if "aadhaar_number" in err_str:
                return None, "A customer with this Aadhaar number is already registered."
            elif "pan_number" in err_str:
                return None, "A customer with this PAN number is already registered."
            elif "phone_number" in err_str:
                return None, "A customer with this phone number is already registered."
            elif "email" in err_str:
                return None, "A customer with this email address is already registered."
            return None, f"Duplicate entry detected: {err_str}"
        except Exception as e:
            return None, f"Database error: {str(e)}"

    def search_customers(self, name_query):
        """Search customers by name (case-insensitive partial match)."""
        if not self.connected:
            return []
        try:
            return list(self.db.customers.find(
                {"name": {"$regex": name_query, "$options": "i"}},
                {"documents.aadhaar.data": 0, "documents.pan.data": 0,
                 "documents.salary_slip.data": 0}
            ))
        except Exception:
            return []

    def get_customer_by_name(self, name):
        """Get customer record by exact name (without large binary data)."""
        if not self.connected:
            return None
        try:
            return self.db.customers.find_one(
                {"name": name},
                {"documents.aadhaar.data": 0, "documents.pan.data": 0,
                 "documents.salary_slip.data": 0}
            )
        except Exception:
            return None

    def get_customer_by_id(self, customer_id):
        """Get full customer record by ObjectId."""
        if not self.connected:
            return None
        try:
            return self.db.customers.find_one({"_id": ObjectId(customer_id)})
        except Exception:
            return None

    def get_all_customers(self):
        """Retrieve all customers (excluding large binary document data)."""
        if not self.connected:
            return []
        try:
            return list(self.db.customers.find(
                {},
                {"documents.aadhaar.data": 0, "documents.pan.data": 0,
                 "documents.salary_slip.data": 0}
            ).sort("created_at", -1))
        except Exception:
            return []

    def get_customer_count(self):
        """Get total registered customer count."""
        if not self.connected:
            return 0
        try:
            return self.db.customers.count_documents({})
        except Exception:
            return 0

    def get_customer_document(self, customer_id, doc_type):
        """
        Retrieve a specific document's binary data for a customer.
        doc_type: 'aadhaar', 'pan', or 'salary_slip'

        Returns: dict with 'filename', 'content_type', 'data' (base64), 'size_bytes'
                 or None if not found.
        """
        if not self.connected:
            return None
        try:
            customer = self.db.customers.find_one(
                {"_id": ObjectId(customer_id)},
                {f"documents.{doc_type}": 1}
            )
            if customer and "documents" in customer and doc_type in customer["documents"]:
                return customer["documents"][doc_type]
            return None
        except Exception:
            return None

    def update_kyc_status(self, customer_id, status, notes=""):
        """
        Update the KYC verification status for a customer.
        status: 'pending', 'verified', 'rejected'
        """
        if not self.connected:
            return False
        try:
            result = self.db.customers.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {
                    "kyc_status": status,
                    "kyc_notes": notes,
                    "kyc_updated_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                }}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def upload_customer_documents(self, customer_id, documents):
        """
        Upload or update documents for an existing customer.
        documents: dict mapping doc_type ('aadhaar', 'pan', 'salary_slip') to uploaded file objects.
        Automatically updates kyc_status to 'verified' if all 3 required documents are present,
        or 'pending' if any are missing.
        """
        if not self.connected:
            return False, "Database not connected"
        try:
            doc_storage = {}
            for doc_name, doc_file in documents.items():
                if doc_file is not None:
                    content = doc_file.read()
                    doc_file.seek(0)
                    doc_storage[f"documents.{doc_name}"] = {
                        "filename": sanitize_filename(doc_file.name),
                        "content_type": doc_file.type,
                        "data": base64.b64encode(content).decode('utf-8'),
                        "size_bytes": len(content),
                        "uploaded_at": datetime.utcnow()
                    }
            if not doc_storage:
                return False, "No valid documents provided"

            doc_storage["updated_at"] = datetime.utcnow()
            self.db.customers.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": doc_storage}
            )

            # Re-check completeness of all 3 required docs
            updated_cust = self.db.customers.find_one({"_id": ObjectId(customer_id)})
            existing_docs = updated_cust.get("documents", {}) if updated_cust else {}
            has_all = ("aadhaar" in existing_docs and "pan" in existing_docs and "salary_slip" in existing_docs)
            new_kyc_status = "verified" if has_all else "pending"

            self.db.customers.update_one(
                {"_id": ObjectId(customer_id)},
                {"$set": {
                    "kyc_status": new_kyc_status,
                    "salary_slip_uploaded": "salary_slip" in existing_docs,
                    "kyc_updated_at": datetime.utcnow()
                }}
            )
            return True, f"Documents successfully uploaded. KYC Status is now: {new_kyc_status.upper()}."
        except Exception as e:
            return False, str(e)

    # ── Application Operations ───────────────────────────────────────────

    def save_application(self, application_data):
        """
        Save a loan risk assessment result.
        Returns the generated application reference ID.
        """
        if not self.connected:
            return None

        try:
            application_data["created_at"] = datetime.utcnow()
            application_data["application_id"] = self._generate_application_id()
            self.db.loan_applications.insert_one(application_data)
            return application_data["application_id"]
        except Exception:
            return None

    def get_customer_applications(self, customer_name):
        """Get all loan applications for a specific customer, newest first."""
        if not self.connected:
            return []
        try:
            return list(self.db.loan_applications.find(
                {"customer_name": customer_name}
            ).sort("created_at", -1))
        except Exception:
            return []

    def get_all_applications(self):
        """Get all loan applications, newest first."""
        if not self.connected:
            return []
        try:
            return list(self.db.loan_applications.find().sort("created_at", -1))
        except Exception:
            return []

    def get_application_count(self):
        """Get total application count."""
        if not self.connected:
            return 0
        try:
            return self.db.loan_applications.count_documents({})
        except Exception:
            return 0

    # ── Utility ──────────────────────────────────────────────────────────

    def _generate_application_id(self):
        """Generate a unique application reference number like LRA-2026-00001."""
        try:
            count = self.db.loan_applications.count_documents({}) + 1
            now = datetime.utcnow()
            return f"LRA-{now.year}-{count:05d}"
        except Exception:
            import random
            return f"LRA-{datetime.utcnow().year}-{random.randint(10000, 99999)}"

    def check_duplicate(self, field, value):
        """Check if a value already exists for a given field in customers collection."""
        if not self.connected:
            return False
        try:
            return self.db.customers.find_one({field: value}) is not None
        except Exception:
            return False
