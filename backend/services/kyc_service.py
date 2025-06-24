"""
KYC Service - Handles Know Your Customer verification for card issuance
Simulates KYC workflow for demo purposes - in production would integrate with real KYC providers
"""
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from ..models.virtual_card import (
    UserKYC, KYCRequest, KYCStatus, KYCDocument
)
from ..services.database import get_collection

logger = logging.getLogger(__name__)

class KYCService:
    """Service for managing KYC verification process"""
    
    # Demo KYC configuration
    VALID_DOCUMENT_TYPES = {
        "aadhar": {"pattern": r"^\d{12}$", "name": "Aadhar Card"},
        "pan": {"pattern": r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", "name": "PAN Card"},
        "passport": {"pattern": r"^[A-Z][0-9]{7}$", "name": "Passport"},
        "driving_license": {"pattern": r"^[A-Z]{2}[0-9]{13}$", "name": "Driving License"}
    }
    
    @staticmethod
    async def initiate_kyc(request: KYCRequest) -> UserKYC:
        """Initiate KYC process for a user"""
        try:
            kyc_collection = await get_collection("user_kyc")
            
            # Check if KYC already exists
            existing_kyc = await kyc_collection.find_one({"user_id": request.user_id})
            if existing_kyc:
                existing_kyc_obj = UserKYC(**existing_kyc)
                if existing_kyc_obj.kyc_status in [KYCStatus.APPROVED, KYCStatus.IN_PROGRESS]:
                    raise ValueError(f"KYC already exists with status: {existing_kyc_obj.kyc_status}")
            
            # Validate documents
            validated_documents = []
            for doc in request.documents:
                if await KYCService._validate_document(doc):
                    validated_documents.append(doc)
                else:
                    raise ValueError(f"Invalid document: {doc.document_type}")
            
            # Create KYC record
            kyc_record = UserKYC(
                user_id=request.user_id,
                kyc_status=KYCStatus.IN_PROGRESS,
                full_name=request.full_name,
                date_of_birth=request.date_of_birth,
                address=request.address,
                phone_verified=True,  # Assume verified for demo
                email_verified=True,  # Assume verified for demo
                documents=validated_documents,
                risk_score=await KYCService._calculate_risk_score(request)
            )
            
            # Save to database
            if existing_kyc:
                await kyc_collection.replace_one(
                    {"user_id": request.user_id},
                    kyc_record.dict()
                )
            else:
                await kyc_collection.insert_one(kyc_record.dict())
            
            # Auto-process for demo (in production this would be manual review)
            await KYCService._auto_process_kyc(kyc_record.id)
            
            logger.info(f"KYC initiated for user {request.user_id}")
            return kyc_record
            
        except Exception as e:
            logger.error(f"Error initiating KYC: {e}")
            raise
    
    @staticmethod
    async def get_kyc_status(user_id: str) -> Optional[UserKYC]:
        """Get KYC status for a user"""
        try:
            kyc_collection = await get_collection("user_kyc")
            kyc_doc = await kyc_collection.find_one({"user_id": user_id})
            
            if kyc_doc:
                return UserKYC(**kyc_doc)
            return None
            
        except Exception as e:
            logger.error(f"Error getting KYC status: {e}")
            return None
    
    @staticmethod
    async def update_kyc_status(kyc_id: str, status: KYCStatus, reviewer_id: str = "system", 
                               rejection_reason: Optional[str] = None) -> bool:
        """Update KYC status (approve/reject)"""
        try:
            kyc_collection = await get_collection("user_kyc")
            
            update_data = {
                "kyc_status": status,
                "updated_at": datetime.utcnow(),
                "reviewed_at": datetime.utcnow(),
                "reviewer_id": reviewer_id
            }
            
            if status == KYCStatus.APPROVED:
                update_data["approved_for_card_issuance"] = True
            elif status == KYCStatus.REJECTED:
                update_data["rejection_reason"] = rejection_reason
                update_data["approved_for_card_issuance"] = False
            
            result = await kyc_collection.update_one(
                {"id": kyc_id},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating KYC status: {e}")
            return False
    
    @staticmethod
    async def _validate_document(document: KYCDocument) -> bool:
        """Validate document format and details"""
        try:
            import re
            
            doc_type = document.document_type.lower()
            if doc_type not in KYCService.VALID_DOCUMENT_TYPES:
                return False
            
            # Check document number format
            pattern = KYCService.VALID_DOCUMENT_TYPES[doc_type]["pattern"]
            if not re.match(pattern, document.document_number):
                return False
            
            # In production, this would verify with actual document verification APIs
            # For demo, we'll mark as verified
            document.verified = True
            document.verified_at = datetime.utcnow()
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating document: {e}")
            return False
    
    @staticmethod
    async def _calculate_risk_score(request: KYCRequest) -> int:
        """Calculate risk score for KYC (0-100, lower is better)"""
        try:
            risk_score = 10  # Base score
            
            # Age factor
            try:
                from datetime import datetime
                birth_date = datetime.strptime(request.date_of_birth, "%Y-%m-%d")
                age = (datetime.utcnow() - birth_date).days / 365.25
                
                if age < 18:
                    risk_score += 50  # Underage
                elif age > 65:
                    risk_score += 10  # Senior citizen - slightly higher risk
                elif age < 25:
                    risk_score += 15  # Young adult
            except:
                risk_score += 20  # Invalid date format
            
            # Document completeness
            required_docs = ["aadhar", "pan"]
            provided_docs = [doc.document_type.lower() for doc in request.documents]
            missing_docs = set(required_docs) - set(provided_docs)
            risk_score += len(missing_docs) * 15
            
            # Phone/email verification
            if not hasattr(request, 'phone_verified') or not request.phone_number:
                risk_score += 15
            if not hasattr(request, 'email_verified') or not request.email:
                risk_score += 10
            
            return min(risk_score, 100)  # Cap at 100
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {e}")
            return 50  # Default medium risk
    
    @staticmethod
    async def _auto_process_kyc(kyc_id: str) -> None:
        """Auto-process KYC for demo purposes"""
        try:
            # In production, this would be a manual review process
            # For demo, we'll auto-approve low risk applications
            
            kyc_collection = await get_collection("user_kyc")
            kyc_doc = await kyc_collection.find_one({"id": kyc_id})
            
            if not kyc_doc:
                return
            
            kyc_record = UserKYC(**kyc_doc)
            
            # Auto-approve if risk score is low
            if kyc_record.risk_score <= 30:
                await KYCService.update_kyc_status(
                    kyc_id, 
                    KYCStatus.APPROVED, 
                    "auto_system"
                )
                logger.info(f"KYC auto-approved for user {kyc_record.user_id}")
            else:
                # Set to under review for manual processing
                await KYCService.update_kyc_status(
                    kyc_id, 
                    KYCStatus.UNDER_REVIEW, 
                    "auto_system"
                )
                logger.info(f"KYC set to manual review for user {kyc_record.user_id}")
                
        except Exception as e:
            logger.error(f"Error auto-processing KYC: {e}")
    
    @staticmethod
    async def get_kyc_requirements() -> Dict[str, Any]:
        """Get KYC requirements and document types"""
        return {
            "required_documents": [
                {
                    "type": "aadhar",
                    "name": "Aadhar Card",
                    "description": "12-digit Aadhar number",
                    "required": True
                },
                {
                    "type": "pan",
                    "name": "PAN Card", 
                    "description": "PAN card for tax identification",
                    "required": True
                }
            ],
            "optional_documents": [
                {
                    "type": "passport",
                    "name": "Passport",
                    "description": "Valid Indian passport",
                    "required": False
                },
                {
                    "type": "driving_license",
                    "name": "Driving License",
                    "description": "Valid driving license",
                    "required": False
                }
            ],
            "required_information": [
                "Full legal name",
                "Date of birth", 
                "Complete address",
                "Phone number (verified)",
                "Email address (verified)"
            ]
        }
    
    @staticmethod
    async def simulate_document_verification(document_type: str, document_number: str) -> Dict[str, Any]:
        """Simulate document verification with external APIs"""
        try:
            # In production, this would call actual verification APIs like:
            # - Aadhar verification via UIDAI
            # - PAN verification via Income Tax Department
            # - Passport verification via Passport Seva
            
            # For demo, simulate based on document format
            import re
            
            if document_type.lower() not in KYCService.VALID_DOCUMENT_TYPES:
                return {
                    "verified": False,
                    "error": "Invalid document type"
                }
            
            pattern = KYCService.VALID_DOCUMENT_TYPES[document_type.lower()]["pattern"]
            if not re.match(pattern, document_number):
                return {
                    "verified": False,
                    "error": "Invalid document number format"
                }
            
            # Simulate successful verification
            return {
                "verified": True,
                "verification_id": f"VER_{secrets.token_hex(6).upper()}",
                "verified_at": datetime.utcnow().isoformat(),
                "verification_source": f"demo_{document_type}_api"
            }
            
        except Exception as e:
            logger.error(f"Error simulating document verification: {e}")
            return {
                "verified": False,
                "error": "Verification service unavailable"
            }
    
    @staticmethod
    async def create_demo_kyc_for_user(user_id: str, full_name: str) -> UserKYC:
        """Create a demo KYC record for testing purposes"""
        try:
            demo_request = KYCRequest(
                user_id=user_id,
                full_name=full_name,
                date_of_birth="1990-01-01",
                address="123 Demo Street, Demo City, Demo State 400001",
                phone_number="9876543210",
                email="demo@axzora.com",
                documents=[
                    KYCDocument(
                        document_type="aadhar",
                        document_number="123456789012",
                        verified=True,
                        verified_at=datetime.utcnow()
                    ),
                    KYCDocument(
                        document_type="pan",
                        document_number="ABCDE1234F",
                        verified=True,
                        verified_at=datetime.utcnow()
                    )
                ]
            )
            
            return await KYCService.initiate_kyc(demo_request)
            
        except Exception as e:
            logger.error(f"Error creating demo KYC: {e}")
            raise