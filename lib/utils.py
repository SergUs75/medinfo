# lib/utils.py
from datetime import datetime
import calendar
from typing import Optional



def format_date(date_iso: Optional[str]) -> str:
    if not date_iso:
        return ''
    try:
        date_obj = datetime.strptime(date_iso, '%Y-%m-%d')
        return date_obj.strftime('%d.%m.%Y')
    except ValueError:
        return 'Помилка формату'
    
def calculate_age(birth_date_str, reference_date = None):
    if not birth_date_str:
        return 0, 0, 0
    try:
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        ref_date = reference_date if reference_date else datetime.today()
        if isinstance(ref_date, str):
            ref_date = datetime.strptime(ref_date, "%Y-%m-%d") 
        years = ref_date.year - birth_date.year
        months = ref_date.month - birth_date.month
        days = ref_date.day - birth_date.day
        if days < 0:
            months -= 1
            prev_month = ref_date.month - 1 if ref_date.month > 1 else 12
            prev_year = ref_date.year if ref_date.month > 1 else ref_date.year - 1
            days += calendar.monthrange(prev_year, prev_month)[1]
        if months < 0:
            years -= 1
            months += 12
        return years, months, days
    except (ValueError, TypeError) as e:
        return 0, 0, 0

def format_gender(gender_code: Optional[str]):
    if isinstance(gender_code, str):
        gender_code = gender_code.lower()
        if gender_code in ('male', 'm'):
            return 'чоловіча'
        if gender_code in ('female', 'f'):
            return 'жіноча'
        return 'невідома'

def lower_first(s: str | None) -> str | None:
    if not s:
        return s
    return s[0].lower() + s[1:]

def format_address(address: dict | None) -> str:
    if not address:
        return "Адреса відсутня"

    parts = []

    # Вулиця
    street_parts = []
    if address.get("street_type"):
        street_parts.append(address["street_type"])
    if address.get("street"):
        street_parts.append(address["street"])

    if street_parts:
        parts.append(" ".join(street_parts))

    # Будинок
    if address.get("building"):
        parts.append(f"буд. {address['building']}")

    # Квартира
    if address.get("apartment"):
        parts.append(f"кв. {address['apartment']}")

    # Населений пункт
    if address.get("settlement"):
        parts.append(address["settlement"])

    # Регіон
    if address.get("region"):
        parts.append(address["region"])

    # Індекс
    if address.get("zip"):
        parts.append(address["zip"])

    return ", ".join(parts)
