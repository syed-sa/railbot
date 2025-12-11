# app/services/irctc_client.py
from typing import Any, Dict, Optional
import httpx

from app.core.config import get_settings

settings = get_settings()


class IRCTCClientError(Exception):
    """Raised when IRCTC RapidAPI returns non-2xx or network error occurs."""


class IRCTCClient:
    """
    Async wrapper for the IRCTC RapidAPI endpoints.
    No retries are performed here by design (per user instruction).
    """
    def __init__(self, api_key: str, host: str, timeout: float = 20.0):
        self.base_url = "https://irctc1.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": host,
        }
        self.timeout = timeout


    async def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        
        url = f"{self.base_url}{path}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=self.headers, params=params)
                resp.raise_for_status()
                return resp.json()
            
            except httpx.HTTPStatusError as exc:
                msg = f"IRCTC API error [{exc.response.status_code}] {exc.request.url}: {exc.response.text}"
                raise IRCTCClientError(msg)
                
            except httpx.RequestError as exc:
                raise IRCTCClientError(f"Network error while calling IRCTC API: {exc}") from exc

    
    
    async def search_station(self, query: str) -> Dict[str, Any]:
       
        """GET /api/v1/SearchStation or /searchStation"""
        
        return await self._get("/api/v1/SearchStation", params={"query": query})

    async def search_train(self, query: str) -> Dict[str, Any]:
        
        """GET /api/v1/SearchTrain"""
        return await self._get("/api/v1/SearchTrain", params={"query": query})

    async def trains_between_stations_v3(self, from_station_code: str, to_station_code: str, date_of_journey: str) -> Dict[str, Any]:
        
        """GET /api/v/trainBetweenStations"""
        return await self._get("/api/v3/trainBetweenStations", params={
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
            "dateOfJourney": date_of_journey
        })

    async def get_train_live_status(self, train_no: str) -> Dict[str, Any]:
        
        """GET /api/v1/liveTrainStatus"""
        return await self._get("/api/v1/liveTrainStatus", params={"trainNo": train_no})

    async def get_train_schedule(self, train_no: str) -> Dict[str, Any]:
        
        """GET /api/v1/getTrainSchedule"""
        return await self._get("/api/v1/getTrainSchedule", params={"trainNo": train_no})

    async def get_pnr_status_v3(self, pnr: str) -> Dict[str, Any]:
        
        """GET /api/v3/getPNRStatus"""
        return await self._get("/api/v3/getPNRStatus", params={"pnrNumber": pnr})


    async def check_seat_availability_v2(self, train_no: str, from_station_code: str, to_station_code: str, date_of_journey: str, class_type: str, quota: str) -> Dict[str, Any]:
        
        """GET /api/v2/CheckSeatAvailability - pass whatever the v2 expects in kwargs"""
        params = {
            "trainNo": train_no,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
            "date": date_of_journey,
            "classType": class_type,
            "quota": quota
        }
        return await self._get("/api/v2/checkSeatAvailability", params=params)

    async def get_train_classes(self) -> Dict[str, Any]:
        
        """GET /api/v1/getTrainClasses"""
        return await self._get("/api/v1/getTrainClasses")

    async def get_fare(self, train_no: str, from_station_code: str, to_station_code: str) -> Dict[str, Any]:
        
        """GET /api/v1/getFare"""
        params = {
            "trainNo": train_no,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
        }
        return await self._get("/api/v1/getFare", params=params)

    async def get_trains_by_station(self, station_code: str) -> Dict[str, Any]:
        
        """GET /api/v1/getTrainsByStation"""
        return await self._get("/api/v1/getTrainsByStation", params={"stationCode": station_code})

