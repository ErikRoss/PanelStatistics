from sqlalchemy import (
    ARRAY,
    Text,
    Column,
    Integer,
    Float,
    JSON,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    create_engine,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from config import SQLALCHEMY_DATABASE_URI


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base = declarative_base()


class Panel(Base):
    __tablename__ = "panels"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    service_tag = Column(String, index=True)
    domain = Column(String, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    statistics = relationship("Statistics", back_populates="panel")
    
    def __repr__(self):
        return f"<Panel(name={self.name}, service_tag={self.service_tag}, domain={self.domain})>"
    
    def __str__(self):
        return f"{self.name} ({self.service_tag}) - {self.domain}"
    
    def model_dump(self):
        return {
            "id": self.id,
            "name": self.name,
            "service_tag": self.service_tag,
            "domain": self.domain,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    total = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    panel_id = Column(Integer, ForeignKey("panels.id"))
    panel = relationship("Panel", back_populates="statistics")
    
    def __repr__(self):
        return f"<Statistics(total={self.total}, panel_id={self.panel_id})>"
    
    def __str__(self):
        return f"{self.total} - {self.panel_id}"
    
    def model_dump(self):
        return {
            "id": self.id,
            "panel_id": self.panel_id,
            "total": self.total,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
    

class PanelUser(Base):
    __tablename__ = "panel_users"

    id = Column(Integer, primary_key=True)
    service_tag = Column(String)
    unique_hash = Column(String, index=True)
    
    campaign_events = relationship("CampaignEvent", back_populates="user")
    app_events = relationship("AppEvent", back_populates="user")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    
    
    def __repr__(self):
        return f"<PanelUser(panel_service_tag={self.service_tag}, panel_hash={self.unique_hash})>"
    
    def __str__(self):
        return f"{self.service_tag} - {self.unique_hash}"
    
    def model_dump(self):
        return {
            "hash_code": self.unique_hash,
            "service_tag": self.service_tag,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


class CampaignEvent(Base):
    __tablename__ = "campaign_events"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer)
    campaign_name = Column(String)
    campaign_hash = Column(String, index=True)
    subuser_hash = Column(String, index=True)
    service_tag = Column(String)
    
    clid = Column(String)
    domain = Column(String, index=True)
    request_parameters = Column(JSON)
    user_ip = Column(String)
    country = Column(String, index=True)
    city = Column(String, index=True)
    device = Column(String)
    
    event_result = Column(String)
    app_id = Column(Integer)
    landing_id = Column(Integer)
    offer_url = Column(String)
    
    user_id = Column(Integer, ForeignKey("panel_users.id"))
    user = relationship("PanelUser", back_populates="campaign_events")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<CampaignEvent(campaign_name={self.campaign_name}, event_result={self.event_result})>"
    
    def __str__(self):
        return f"{self.campaign_name} - {self.event_result}"
    
    def model_dump(self):
        return {
            "id": self.id,
            "campaign_name": self.campaign_name,
            "subuser_hash": self.subuser_hash,
            "clid": self.clid,
            "domain": self.domain,
            "request_parameters": self.request_parameters,
            "user_ip": self.user_ip,
            "country": self.country,
            "city": self.city,
            "device": self.device,
            "event_result": self.event_result,
            "app_id": self.app_id,
            "landing_id": self.landing_id,
            "redirect_url": self.offer_url,
        }


class AppEvent(Base):
    __tablename__ = "app_events"

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer)
    app_name = Column(String)
    app_tags = Column(ARRAY(String))
    app_hash = Column(String, index=True)
    service_tag = Column(String)
    
    clid = Column(String)
    appclid = Column(String)
    request_parameters = Column(JSON)
    user_ip = Column(String)
    country = Column(String, index=True)
    city = Column(String, index=True)
    device = Column(String)
    
    event_result = Column(String)
    deposit_amount = Column(Float)
    
    user_id = Column(Integer, ForeignKey("panel_users.id"))
    user = relationship("PanelUser", back_populates="app_events")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AppEvent(name={self.app_name}, panel_id={self.event_result})>"
    
    def __str__(self):
        return f"{self.app_name} - {self.event_result}"
    
    def model_dump(self):
        return {
            "id": self.id,
            "app_id": self.app_id,
            "app_name": self.app_name,
            "app_tags": self.app_tags,
            "clid": self.clid,
            "appclid": self.appclid,
            "request_parameters": self.request_parameters,
            "user_ip": self.user_ip,
            "country": self.country,
            "city": self.city,
            "device": self.device,
            "event_result": self.event_result,
            "deposit_amount": self.deposit_amount,
        }


Base.metadata.create_all(bind=engine)
