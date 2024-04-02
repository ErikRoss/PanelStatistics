from typing import Optional

from pydantic import BaseModel


class PanelData(BaseModel):
    name: str
    service_tag: str
    domain: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class CampaignEventData(BaseModel):
    user_hash: str
    campaign_id: int
    campaign_name: str
    campaign_hash: str
    subuser_hash: Optional[str] = None
    service_tag: str

    clid: str
    domain: str
    request_parameters: dict
    user_ip: str
    country: str
    city: str
    device: str

    event_result: str
    app_id: Optional[int] = None
    landing_id: Optional[int] = None
    redirect_url: Optional[str] = None
    
    app_name: Optional[str] = None
    app_tags: Optional[list] = None
    app_hash: Optional[str] = None
    appclid: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_hash": 1,
                    "campaign_id": 1,
                    "campaign_name": "Campaign 1",
                    "campaign_hash": "campaign_hash",
                    "subuser_hash": "subuser_hash",
                    "service_tag": "service_tag",
                    "clid": "clid",
                    "domain": "domain",
                    "request_parameters": {"key": "value"},
                    "user_ip": "user_ip",
                    "country": "country",
                    "city": "city",
                    "device": "device",
                    "event_result": "event_result",
                    "app_id": 1,
                    "landing_id": 1,
                    "redirect_url": "redirect_url",
                }
            ]
        }
    }


class AppEventData(BaseModel):
    user_hash: str
    app_id: int
    app_name: str
    app_tags: list
    app_hash: str
    service_tag: str

    clid: str
    appclid: Optional[str] = None
    request_parameters: dict
    user_ip: str
    country: str
    city: str
    device: str

    event_result: str
    deposit_amount: Optional[float] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_hash": "user_hash",
                    "app_id": 1,
                    "app_name": "App 1",
                    "app_tags": ["tag1", "tag2"],
                    "app_hash": "app_hash",
                    "service_tag": "service_tag",
                    "clid": "clid",
                    "appclid": "appclid",
                    "request_parameters": {"key": "value"},
                    "user_ip": "user_ip",
                    "country": "country",
                    "city": "city",
                    "device": "device",
                    "event_result": "event_result",
                    "deposit_amount": 100.0,
                }
            ]
        }
    }


class FilterData(BaseModel):
    user_hash: str
    service_tag: str
    app_hash: Optional[str] = None
    campaign_hash: Optional[str] = None
    period: Optional[str] = "month"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_hash": "user_hash",
                    "service_tag": "service_tag",
                    "app_hash": None,
                    "campaign_hash": None,
                    "period": "month",
                }
            ]
        }
    }
