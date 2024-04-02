from datetime import datetime, timedelta
from hashlib import sha256

from sqlalchemy.orm import sessionmaker

from dataclass import CampaignEventData, AppEventData, FilterData
from models import PanelUser, CampaignEvent, AppEvent
from utils import logger


logs = logger.get_logger(__name__)


class Collector:
    def __init__(self, session: sessionmaker):
        self.session = session
    
    # def generate_user_hash(self, user_id: int, service_tag: str) -> str:
    #     return sha256(f"user{user_id}{service_tag}".encode()).hexdigest()[:12]
    
    def get_or_create_user(self, user_hash: str, service_tag: str):
        logs.info(f"User hash: {user_hash}")
        
        user = self.session.query(PanelUser).filter_by(unique_hash=user_hash).first()
        if user:
            logs.info(f"User found: {user}")
            return user
        else:
            logs.info("User not found, creating new user")
            user = PanelUser(
                service_tag=service_tag,
                unique_hash=user_hash
                )
            self.session.add(user)
            self.session.commit()
            return user
    
    def save_campaign_event(self, data: CampaignEventData):
        logs.info(f"Saving campaign event: {data}")
        
        user = self.get_or_create_user(data.user_hash, data.service_tag)
        logs.info(f"User: {user}")
        campaign_event = CampaignEvent(
            user_id=user.id,
            campaign_id=data.campaign_id,
            campaign_name=data.campaign_name,
            campaign_hash=data.campaign_hash,
            subuser_hash=data.subuser_hash,
            service_tag=data.service_tag,
            clid=data.clid,
            domain=data.domain,
            request_parameters=data.request_parameters,
            user_ip=data.user_ip,
            country=data.country,
            city=data.city,
            device=data.device,
            event_result=data.event_result,
            app_id=data.app_id,
            landing_id=data.landing_id,
            offer_url=data.redirect_url,
        )
        self.session.add(campaign_event)
        self.session.commit()
        
        logs.info(f"Campaign event saved: {campaign_event}")
    
    def save_app_event(self, data: AppEventData):
        logs.info(f"Saving app event: {data}")
        
        user = self.get_or_create_user(data.user_hash, data.service_tag)
        app_event = AppEvent(
            user_id=user.id,
            app_id=data.app_id,
            app_name=data.app_name,
            app_tags=data.app_tags,
            app_hash=data.app_hash,
            service_tag=data.service_tag,
            clid=data.clid,
            appclid=data.appclid,
            request_parameters=data.request_parameters,
            user_ip=data.user_ip,
            country=data.country,
            city=data.city,
            device=data.device,
            event_result=data.event_result
        )
        self.session.add(app_event)
        self.session.commit()
        
        logs.info(f"App event saved: {app_event}")
    
    def save_app_view_from_campaign(self, data: CampaignEventData):
        logs.info(f"Saving app view from campaign: {data}")
        
        user = self.get_or_create_user(data.user_hash, data.service_tag)
        app_event = AppEvent(
            user_id=user.id,
            app_id=data.app_id,
            app_name=data.app_name,
            app_tags=data.app_tags,
            app_hash=data.app_hash,
            service_tag=data.service_tag,
            clid=data.clid,
            appclid=data.appclid,
            request_parameters=data.request_parameters,
            user_ip=data.user_ip,
            country=data.country,
            city=data.city,
            device=data.device,
            event_result="view"
        )
        self.session.add(app_event)
        self.session.commit()
        
        logs.info(f"App view saved: {app_event}")
    
    def generate_user_statistics(self, data: FilterData):
        logs.info(f"Generating statistics for user: {data.user_hash}")
        
        user = (
            self.session.query(PanelUser).filter_by(unique_hash=data.user_hash).first()
        )
        if not user:
            logs.error(f"User not found: {data.user_hash}")
            return None
        
        # filter events by date, event type, result, etc.
        campaign_events = []
        app_events = []
        today = datetime.now()
        if data.period == "day":
            period_start = today - timedelta(days=1)
        elif data.period == "week":
            period_start = today - timedelta(weeks=1)
        elif data.period == "month":
            period_start = today - timedelta(weeks=4)
        elif data.period == "year":
            period_start = today - timedelta(weeks=52)
        else:
            period_start = user.created_at
        
        if data.campaign_hash:
            campaign_events = (
                self.session.query(CampaignEvent)
                .filter(CampaignEvent.service_tag == data.service_tag)
                .filter(CampaignEvent.user_id == user.id)
                .filter(CampaignEvent.campaign_hash == data.campaign_hash)
                .filter(CampaignEvent.created_at >= period_start)
                .all()
            )
        else:
            campaign_events = (
                self.session.query(CampaignEvent)
                .filter(CampaignEvent.service_tag == data.service_tag)
                .filter(CampaignEvent.user_id == user.id)
                .filter(CampaignEvent.created_at >= period_start)
                .all()
            )
            
        if data.app_hash:
            app_events = (
                self.session.query(AppEvent)
                .filter(AppEvent.service_tag == data.service_tag)
                .filter(AppEvent.user_id == user.id)
                .filter(AppEvent.app_hash == data.app_hash)
                .filter(AppEvent.created_at >= period_start)
                .all()
            )
        else:
            app_events = (
                self.session.query(AppEvent)
                .filter(CampaignEvent.service_tag == data.service_tag)
                .filter(AppEvent.user_id == user.id)
                .filter(AppEvent.created_at >= period_start)
                .all()
            )
        
        campaign_emergency = [
            event.model_dump()
            for event in campaign_events
            if event.event_result == "emergency"
        ]
        campaign_offer = [
            event.model_dump()
            for event in campaign_events
            if event.event_result == "offer"
        ]
        campaign_landing = [
            event.model_dump()
            for event in campaign_events
            if event.event_result == "landing"
        ]
        campaign_app = [
            event.model_dump()
            for event in campaign_events
            if event.event_result == "app"
        ]
        
        app_view = [
            event.model_dump() 
            for event in app_events 
            if event.event_result == "view"
        ]
        app_install = [
            event.model_dump()
            for event in app_events
            if event.event_result == "install"
        ]
        app_register = [
            event.model_dump()
            for event in app_events
            if event.event_result == "reg"
        ]
        app_deposit = [
            event.model_dump()
            for event in app_events
            if event.event_result == "dep"
        ]
        app_entry = [
            event.model_dump()
            for event in app_events
            if event.event_result == "entry"
        ]
        app_reregister = [
            event.model_dump()
            for event in app_events
            if event.event_result == "rereg"
        ]
        app_redep = [
            event.model_dump()
            for event in app_events
            if event.event_result == "redep"
        ]
        
        return {
            "campaign_events": {
                "total": len(campaign_events),
                "emergency": {"total": len(campaign_emergency), "events": campaign_emergency},
                "offer": {"total": len(campaign_offer), "events": campaign_offer},
                "landing": {"total": len(campaign_landing), "events": campaign_landing},
                "app": {"total": len(campaign_app), "events": campaign_app}
            },
            "app_events": {
                "total": len(app_events),
                "view": {"total": len(app_view), "events": app_view},
                "install": {"total": len(app_install), "events": app_install},
                "register": {"total": len(app_register), "events": app_register},
                "deposit": {"total": len(app_deposit), "events": app_deposit},
                "entry": {"total": len(app_entry), "events": app_entry},
                "reregister": {"total": len(app_reregister), "events": app_reregister},
                "redeposit": {"total": len(app_redep), "events": app_redep}
            }
        }
        
    def show_campaign_events(self):
        campaign_events = self.session.query(CampaignEvent).all()
        return campaign_events