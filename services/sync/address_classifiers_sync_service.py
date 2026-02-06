# services/sync/address_classifiers_sync_service.py

from datetime import datetime, timedelta
from lib.logger import setup_logger

from repositories.meta_repository import get_meta_value, set_meta_value
from repositories.dictionaries.address_classifiers_repository import (
    upsert_address_types,
    upsert_countries,
    upsert_street_types,
    upsert_settlement_types,
    upsert_regions,
    upsert_districts,
    upsert_settlements,
    upsert_city_districts,
)

logger = setup_logger("address_classifiers_sync_service")


class AddressClassifiersSyncService:
    def __init__(self, db_conn, api_client):
        self.conn = db_conn
        self.api = api_client
        self._settlements_cache = None

    def run(self):
        self._sync_if_due("countries_last_sync", 30, self._sync_countries)
        self._sync_if_due("address_types_last_sync", 30, self._sync_address_types)
        self._sync_if_due("street_types_last_sync", 30, self._sync_street_types)
        self._sync_if_due("settlement_types_last_sync", 30, self._sync_settlement_types)
        self._sync_if_due("regions_last_sync", 7, self._sync_regions)
        self._sync_if_due("districts_last_sync", 7, self._sync_districts)
        self._sync_if_due("settlements_last_sync", 5, self._sync_settlements)
        self._sync_if_due("city_districts_last_sync", 2, self._sync_city_districts)


    def _sync_if_due(self, key, ttl_days, fn):
        last = get_meta_value(self.conn, key)
        if last:
            try:
                last_dt = datetime.fromisoformat(last)
                if datetime.utcnow() - last_dt < timedelta(days=ttl_days):
                    return
            except ValueError:
                pass

        logger.info("Початок синхронізації: %s", key)

        try:
            self.conn.execute("BEGIN IMMEDIATE")
            fn()
            set_meta_value(self.conn, key, datetime.utcnow().isoformat())
            self.conn.commit()
            logger.info("Синхронізація завершена: %s", key)
        except Exception as e:
            self.conn.rollback()
            logger.error("Помилка синхронізації: %s", key, exc_info=e)

    def _get_settlements_cached(self):
        if self._settlements_cache is None:
            logger.info("Завантаження ВСІХ settlements з API (pagination)")
            self._settlements_cache = []

            data = self.api.get_regions()
            regions = data.get("items", [])

            if not regions:
                logger.warning("API повернув порожній список regions")
                return []

            for r in regions:
                region_id = r.get("id")
                if not region_id:
                    continue


                # ⬇⬇⬇ ОЦЕ МІСЦЕ ⬇⬇⬇
                items = self.api.get_all_settlements(region_id)
                self._settlements_cache.extend(items)
                # ⬆⬆⬆ САМЕ ТУТ ⬆⬆⬆

            if not self._settlements_cache:
                logger.warning("API повернув порожній список settlements")

        return self._settlements_cache



    def _sync_countries(self):
        data = self.api.get_countries()
        if not data:
            logger.warning("API повернув порожній список countries")
            return
        upsert_countries(self.conn, data)

    def _sync_address_types(self):
        data = self.api.get_address_types()
        if not data:
            logger.warning("API повернув порожній список address_types")
            return
        upsert_address_types(self.conn, data)

    def _sync_street_types(self):
        data = self.api.get_street_types()
        if not data:
            logger.warning("API повернув порожній список street_types")
            return
        upsert_street_types(self.conn, data)

    def _sync_settlement_types(self):
        settlements = self._get_settlements_cached()
        if not settlements:
            return
        upsert_settlement_types(self.conn, settlements)

    def _sync_regions(self):
        data = self.api.get_regions()
        if not data:
            logger.warning("API повернув порожній список regions")
            return
        upsert_regions(self.conn, data)

    def _sync_districts(self):
        try:
            data = self.api.get_districts()
        except Exception:
            logger.warning("Endpoint districts недоступний")
            return
        if not data:
            logger.warning("API повернув порожній список districts")
            return
        upsert_districts(self.conn, data)

    def _sync_settlements(self):
        settlements = self._get_settlements_cached()
        if not settlements:
            return
        upsert_settlements(self.conn, settlements)

    def _sync_city_districts(self):
        settlements = self._get_settlements_cached()
        if not settlements:
            return

        for s in settlements:
            settlement_id = s.get("id")
            if not settlement_id:
                continue
            data = self.api.get_city_districts(settlement_id)
            if not data:
                logger.warning(
                    "API повернув порожній список city_districts (settlement_id=%s)",
                    settlement_id,
                )
                continue
            upsert_city_districts(self.conn, data)
