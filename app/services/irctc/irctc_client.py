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

    def __init__(self, timeout: float = 20.0):
        self.base_url = "https://irctc1.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": settings.IRCTC_API_KEY,
            "x-rapidapi-host": settings.RAPIDAPI_HOST,
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

    async def get_train_live_status(self, train_no: str, start_day: str) -> Dict[str, Any]:
        
        """GET /api/v1/Get Train Live Status"""
        return await self._get("/api/v1/GetTrainLiveStatus", params={"trainNo": train_no, "startDay": start_day})

    async def get_train_schedule(self, train_no: str) -> Dict[str, Any]:
        
        """GET /api/v1/Get Train Schedule"""
        return await self._get("/api/v1/GetTrainSchedule", params={"trainNo": train_no})

    async def get_pnr_status_v3(self, pnr: str) -> Dict[str, Any]:
        
        """GET /api/v3/GetPNRStatus"""
        return await self._get("/api/v3/GetPNRStatus", params={"pnr": pnr})

    async def check_seat_availability(self, train_no: str, from_station_code: str, to_station_code: str, date_of_journey: str, travel_class: Optional[str] = None) -> Dict[str, Any]:
        
        """GET /api/v1/CheckSeatAvailability (or v2 variant)"""
        params = {
            "trainNo": train_no,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
            "dateOfJourney": date_of_journey
        }
        if travel_class:
            params["class"] = travel_class
        return await self._get("/api/v1/CheckSeatAvailability", params=params)

    async def check_seat_availability_v2(self, **kwargs) -> Dict[str, Any]:
        
        """GET /api/v2/CheckSeatAvailability - pass whatever the v2 expects in kwargs"""
        return await self._get("/api/v2/CheckSeatAvailability", params=kwargs)

    async def get_train_classes(self) -> Dict[str, Any]:
        
        """GET /api/v1/GetTrainClasses"""
        return await self._get("/api/v1/GetTrainClasses")

    async def get_fare(self, train_no: str, from_station_code: str, to_station_code: str, age: Optional[int] = None, travel_class: Optional[str] = None) -> Dict[str, Any]:
        
        """GET /api/v1/GetFare"""
        params = {
            "trainNo": train_no,
            "fromStationCode": from_station_code,
            "toStationCode": to_station_code,
        }
        if age is not None:
            params["age"] = age
        if travel_class:
            params["class"] = travel_class
        return await self._get("/api/v1/GetFare", params=params)

    async def get_trains_by_station(self, station_code: str) -> Dict[str, Any]:
        
        """GET /api/v1/GetTrainsByStation"""
        return await self._get("/api/v1/GetTrainsByStation", params={"stationCode": station_code})

    async def get_live_station(self, hours: int = 1) -> Dict[str, Any]:
        
        """GET /api/v3/getLiveStation?hours=1"""
        return await self._get("/api/v3/getLiveStation", params={"hours": hours})
