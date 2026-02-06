# services/patient/patient_header_service.py
from typing import Dict, Any

from lib.utils import (
    format_date,
    calculate_age,
    format_gender,
)


class PatientHeaderService:
    @staticmethod
    def build_header(json_data: Dict[str, Any]) -> Dict[str, Any]:
        birth_date_iso = json_data.get("birth_date")

        years, months, days = calculate_age(birth_date_iso)

        verification = json_data.get("verification_status") or {}

        last_name = json_data.get("last_name", "")
        first_name = json_data.get("first_name", "")
        second_name = json_data.get("second_name")

        full_name = " ".join(
            part for part in (last_name, first_name, second_name) if part
        )

        return {
            "health24_id": json_data.get("id") or json_data.get("health24_id"),

            "personality_id": json_data.get("personality_id"),

            "last_name": last_name,
            "first_name": first_name,
            "second_name": second_name,
            "full_name": full_name,

            "gender": format_gender(json_data.get("gender")),

            "birth_date": format_date(birth_date_iso) or "—",

            "age_years": years,
            "age_months": months,
            "age_days": days,

            "confirmed": bool(json_data.get("confirmed")),

            "verification_status_code": verification.get("code"),
            "verification_status_title": verification.get("title", "—"),
        }
