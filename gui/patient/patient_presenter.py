#services/patient_service.py
from lib.utils import format_date, format_gender, calculate_age

class PatientPresenter:
    @staticmethod
    def prepare_for_viem(patient: dict) -> dict:
        birth_date = patient.get("birth_date")
        years, months, days = calculate_age(birth_date)
        return {
            **patient,
            "birth_date_view": format_date(birth_date),
            "gender_view": format_gender(patient.get("gender")),
            "age_years": years,
            "age_months": months,
            "age_days": days,
        }
    