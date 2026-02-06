# services/patient/patient_profile_service.py
from typing import Any, Dict
from repositories.patient.patient_profile_repository import upsert_patient_profile
from lib.logger import setup_logger

logger = setup_logger("patient_profile_service")


def extract_patient_profile(json_data: Dict[str, Any]) -> Dict[str, Any]:
    declaration = json_data.get("declaration") or {}
    employee = declaration.get("employee") or {}
    person = json_data.get("person") or {}
    verification = person.get("verification_status") or {}

    last_name = json_data.get("last_name", "")
    first_name = json_data.get("first_name", "")
    second_name = json_data.get("second_name")

    full_name = " ".join(
        part for part in [last_name, first_name, second_name] if part
    )

    phones = json_data.get("phones") or []
    phone = json_data.get("phone") or (phones[0]["number"] if phones else None)

    return {
        "health24_id": json_data["id"],
        "personality_id": json_data["personality_id"],
        "api_id": json_data["api_id"],

        "last_name": last_name,
        "first_name": first_name,
        "second_name": second_name,

        "full_name": full_name,
        "initials_name": json_data.get("initials_name"),

        "gender": json_data.get("gender"),
        "birth_date": json_data.get("birth_date"),
        "age": json_data.get("age"),

        "phone": phone,
        "email": json_data.get("email"),

        "declaration_number": declaration.get("number"),
        "doctor_employee_id": employee.get("id"),
        "doctor_name": employee.get("name"),

        "verification_code": verification.get("code"),
        "confirmed": int(bool(json_data.get("confirmed"))),
        "has_full_profile": int(bool(json_data.get("has_full_profile")))
    }


def sync_patient_profile(conn, json_data: Dict[str, Any]) -> None:
    profile = extract_patient_profile(json_data)
    upsert_patient_profile(conn, profile)
