#services/patient_json_service.py
import json
import requests
from typing import Optional

from repositories.json.patient_json_repository import (
    get_patient_json_by_health24_id,
    upsert_patient_json
)

API_BASE_URL = "https://ehr.h24.ua/api/patients"

def fetch_patient_json_from_api(
    health24_id: int,
    token: str
) -> dict:
    url = f"{API_BASE_URL}/{health24_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    return response.json()

def get_patient_json(
    health24_id: int,
    token: str,
    force_refresh: bool = False
) -> dict:
    if not force_refresh:
        cached_json = get_patient_json_by_health24_id(health24_id)
        if cached_json is not None:
            return json.loads(cached_json)

    patient_data = fetch_patient_json_from_api(health24_id, token)

    api_id = patient_data.get("api_id")
    personality_id = patient_data.get("personality_id")

    upsert_patient_json(
        health24_id=health24_id,
        api_id=api_id,
        personality_id=personality_id,
        json_data=json.dumps(patient_data, ensure_ascii=False),
        source="api"
    )

    return patient_data
