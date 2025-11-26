from enum import Enum
from pydantic import BaseModel
from typing import Optional, Dict


class Intent(str, Enum):
    SEARCH_TRAINS = "search_trains"
    LIVE_STATUS = "live_status"
    TRAIN_SCHEDULE = "train_schedule"
    SEAT_AVAILABILITY = "seat_availability"
    PNR_STATUS = "pnr_status"
    LIVE_STATION = "live_station"
    STATION_SEARCH = "station_search"
    TRAIN_SEARCH = "train_search"
    UNKNOWN = "unknown"


class IntentResult(BaseModel):
    intent: Intent
    params: Dict[str, Optional[str]] = {}
    missing: list[str] = []
