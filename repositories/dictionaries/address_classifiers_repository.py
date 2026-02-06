# repositories/dictionaries/address_classifiers_repository.py

# =========================
# ADDRESS TYPES
# =========================

def upsert_address_types(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO address_types (id, code, title)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                title = excluded.title
            """,
            (it.get("id"), it.get("code"), it.get("title"))
        )


def get_address_type_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM address_types WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# COUNTRIES
# =========================

def upsert_countries(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO countries (id, code, title)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                title = excluded.title
            """,
            (it.get("id"), it.get("code"), it.get("title"))
        )


def get_country_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM countries WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# STREET TYPES
# =========================

def upsert_street_types(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO street_types (id, code, title)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                title = excluded.title
            """,
            (it.get("id"), it.get("code"), it.get("title"))
        )


def get_street_type_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM street_types WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# REGIONS
# =========================

def upsert_regions(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO regions (id, api_id, koatuu, title)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                api_id = excluded.api_id,
                koatuu = excluded.koatuu,
                title = excluded.title
            """,
            (it.get("id"), it.get("api_id"), it.get("koatuu"), it.get("title"))
        )


def get_region_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM regions WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# DISTRICTS
# =========================

def upsert_districts(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO districts (id, api_id, koatuu, title, region_id)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                api_id = excluded.api_id,
                koatuu = excluded.koatuu,
                title = excluded.title,
                region_id = excluded.region_id
            """,
            (
                it.get("id"),
                it.get("api_id"),
                it.get("koatuu"),
                it.get("title"),
                it.get("region_id"),
            )
        )


def get_district_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM districts WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# SETTLEMENT TYPES
# =========================

def upsert_settlement_types(conn, settlements):
    cur = conn.cursor()
    seen = {}
    for s in settlements:
        st = s.get("settlement_type") or {}
        sid = st.get("id")
        if not sid or sid in seen:
            continue
        seen[sid] = True
        cur.execute(
            """
            INSERT INTO settlement_types (id, code, title)
            VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                code = excluded.code,
                title = excluded.title
            """,
            (sid, st.get("code"), st.get("title"))
        )


def get_settlement_type_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM settlement_types WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# SETTLEMENTS
# =========================

def upsert_settlements(conn, items):
    cur = conn.cursor()
    for it in items:
        district = it.get("district") or {}
        region = it.get("region") or {}
        st = it.get("settlement_type") or {}

        cur.execute(
            """
            INSERT INTO settlements (
                id, api_id, koatuu, title,
                region_id, district_id, settlement_type_id, parent_settlement_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                api_id = excluded.api_id,
                koatuu = excluded.koatuu,
                title = excluded.title,
                region_id = excluded.region_id,
                district_id = excluded.district_id,
                settlement_type_id = excluded.settlement_type_id,
                parent_settlement_id = excluded.parent_settlement_id
            """,
            (
                it.get("id"),
                it.get("api_id"),
                it.get("koatuu"),
                it.get("title"),
                region.get("id"),
                district.get("id"),
                st.get("id"),
                it.get("parent_settlement_id"),
            )
        )


def get_settlement_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM settlements WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None


# =========================
# CITY DISTRICTS
# =========================

def upsert_city_districts(conn, items):
    cur = conn.cursor()
    for it in items:
        cur.execute(
            """
            INSERT INTO city_districts (id, koatuu, title, settlement_id)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                koatuu = excluded.koatuu,
                title = excluded.title,
                settlement_id = excluded.settlement_id
            """,
            (
                it.get("id"),
                it.get("koatuu"),
                it.get("title"),
                it.get("settlement_id"),
            )
        )


def get_city_district_title(conn, id_):
    cur = conn.cursor()
    cur.execute("SELECT title FROM city_districts WHERE id = ?", (id_,))
    row = cur.fetchone()
    return row[0] if row else None
