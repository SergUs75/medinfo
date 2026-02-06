# api/health24/patient_client.py

import requests
from typing import List, Dict, Optional

from api.base_client import BaseApiClient
from lib.logger import setup_logger

logger = setup_logger("patient_client")

class PatientClient(BaseApiClient):
    PATIENTS_ENDPOINT = "api/v2/patients"
    PATIENT_BY_ID_ENDPOINT = "api/v2/patients/{patient_id}"
    DOCUMENT_TYPES_ENDPOINT = "api/v2/classifiers/document-types"

    def __init__(self):
        super().__init__()

    def get_patients(self, employee_id: str) -> List[Dict]:
        logger.info(f"Fetching patients for employee_id={employee_id}")

        all_patients: List[Dict] = []
        page = 1
        page_size = 100

        while True:
            params = {
                "declaration_employee_id": employee_id,
                "page": page,
                "page_size": page_size,
            }

            response = self._get(self.PATIENTS_ENDPOINT, params=params)
            
            items = response.get("patients", [])
            has_next = response.get("has_next_page", False)
            
            all_patients.extend(items)

            logger.debug(
                f"Patients page {page}: received {len(items)}"
            )

            if not items or not has_next:
                break

            page += 1

        logger.info(f"Total patients fetched: {len(all_patients)}")
        return all_patients

    def get_patient_by_id(self, patient_id: str) -> Optional[Dict]:
        logger.info(f"Fetching patient by id={patient_id}")

        endpoint = self.PATIENT_BY_ID_ENDPOINT.format(patient_id=patient_id)

        response = self._get(endpoint)
        return response

    def get_document_types(self) -> List[Dict]:
        logger.info("Fetching document types")

        response = self._get(self.DOCUMENT_TYPES_ENDPOINT)
        return response.get("items", [])

    def _get(self, endpoint: str, params: dict | None = None) -> Dict:
        url = f"{self.base_url}{endpoint}"

        try:
            resp = self.session.get(
                url,
                headers=self._headers(),
                params=params,
                timeout=self.timeout,
            )
            resp.raise_for_status()
            return resp.json()

        except requests.RequestException as e:
            logger.error(f"HTTP GET failed: {url} | {e}")
            raise
    
    def get_patient(self, health24_id: int):
        """
        Backward compatibility для PatientLoadService
        """
        return self.get_patient_by_id(health24_id)
