# api/health24/address_classifications_client.py

import requests
from typing import Optional


class AddressClassificationsClient:
    def __init__(self, base_url: str, access_token: str, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        })

    def _get(self, path: str, params: Optional[dict] = None):
        url = f"{self.base_url}{path}"
        response = self.session.get(url, params=params, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_address_types(self):
        return self._get("/api/v2/classifications/address/address_types")

    def get_countries(self):
        return self._get("/api/v2/classifications/address/countries")

    def get_regions(self):
        return self._get("/api/v2/classifications/address/regions")

    def get_districts(self):
        return self._get("/api/v2/classifications/address/districts")

    def get_settlements(self, region_id: Optional[int] = None):
        params = {"response_view": "full"}
        if region_id is not None:
            params["region_id"] = region_id
        return self._get("/api/v2/classifications/address/settlements", params=params)

    def get_city_districts(self, settlement_id: int):
        return self._get(
            "/api/v2/classifications/address/city_districts",
            params={"settlement_id": settlement_id}
        )

    def get_street_types(self):
        return self._get("/api/v2/classifications/address/street_types")
    
    def get_all_settlements(self, region_id: int) -> list[dict]:
        all_items = []
        page = 1
        page_size = 100

        while True:
            params = {
                "region_id": region_id,
                "response_view": "full",
                "page": page,
                "page_size": page_size,
            }

            data = self._get(
                "/api/v2/classifications/address/settlements",
                params=params,
            )

            items = data.get("items", [])
            total = data.get("total", 0)

            if not items:
                break

            all_items.extend(items)

            if len(all_items) >= total:
                break

            page += 1

        return all_items

