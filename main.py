from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import SQLALCHEMY_DATABASE_URI
from dataclass import AppEventData, CampaignEventData, FilterData
from models import Panel, Statistics
from utils import logger
from utils.collector import Collector


engine = create_engine(SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logs = logger.get_logger(__name__)
app = FastAPI()


@app.get("/")
@app.post("/")
async def get_root():
    return JSONResponse(content={"success": True, "msg": "Server is running"})

@app.get("/panels")
async def get_panels():
    with SessionLocal() as session:
        panels = session.query(Panel).all()
        return JSONResponse(content={
            "success": True, 
            "data": [panel.model_dump() for panel in panels]
            })

@app.post("/panels")
async def create_panel(request: Request):
    data = await request.json()
    panel = Panel(**data)

    with SessionLocal() as session:
        session.add(panel)
        session.commit()

    return JSONResponse(content={"success": True, "msg": "Panel created"})

@app.get("/panels/{panel_id}")
async def get_panel(panel_id: int):
    with SessionLocal() as session:
        panel = session.query(Panel).filter(Panel.id == panel_id).first()
        if panel:
            return JSONResponse(content={
                "success": True, 
                "data": panel.model_dump()
                })
        
        return JSONResponse(content={
            "success": False, 
            "msg": "Panel not found"
            }, status_code=404)

@app.get("/panels/{panel_id}/statistics")
async def get_panel_statistics(panel_id: int):
    with SessionLocal() as session:
        panel = session.query(Panel).filter(Panel.id == panel_id).first()
        if panel:
            statistics = panel.statistics.order_by(Statistics.created_at.desc()).first()
            return JSONResponse(
                content={"success": True, "data": statistics.model_dump() or None}
            )
        
        return JSONResponse(content={
            "success": False, 
            "msg": "Panel not found"
            }, status_code=404)

@app.post("/campaign_event")
async def save_campaign_event(data: CampaignEventData):
    logs.info("Received campaign event.")
    session = SessionLocal()
    try:
        collector = Collector(session)
        collector.save_campaign_event(data)
        
        if data.event_result == "app":
            collector.save_app_view_from_campaign(data)
        
        session.close()
        logs.info("Campaign event saved.")
        return JSONResponse(content={
            "success": True, 
            "msg": "Campaign event saved"
            })
    except Exception as e:
        session.close()
        logs.error(f"Error saving campaign event: \n{e}")
        return JSONResponse(content={
            "success": False, 
            "msg": "Error saving campaign event. Check logs for more details"
            })

@app.post("/app_event")
async def save_app_event(data: AppEventData):
    logs.info("Received app event.")
    session = SessionLocal()
    try:
        Collector(session).save_app_event(data)
        session.close()
        logs.info("App event saved.")
        return JSONResponse(
            content={
                "success": True, 
                "msg": "App event saved"
            },
            status_code=200
            )
    except Exception as e:
        session.close()
        logs.error(f"Error saving app event: \n{e}")
        return JSONResponse(
            content={
                "success": False, 
                "msg": "Error saving app event. Check logs for more details"
            },
            status_code=500
            )

@app.post("/user_statistics")
async def generate_user_statistics(data: FilterData):
    logs.info("Generating user statistics.")
    session = SessionLocal()
    try:
        statistics = Collector(session).generate_user_statistics(data)
        session.close()
        logs.info(f"User statistics generated. \n\t{statistics}")
        return JSONResponse(content={
            "success": True, 
            "data": statistics
            })
    except Exception as e:
        session.close()
        logs.error(f"Error generating user statistics: \n{e}")
        return JSONResponse(content={
            "success": False, 
            "msg": "Error generating user statistics. Check logs for more details"
            })

@app.get("/ui/campaign_statistics")
def show_campaign_statistics():
    """
    Show campaign statistics table useing FastUI
    """
    logs.info("Showing campaign statistics.")
    session = SessionLocal()
    try:
        statistics = Collector(session).show_campaign_events()
        session.close()
        logs.info(f"Campaign statistics generated. \n\t{statistics}")
        return [
            c.Page(
                c.Table(
                    data=statistics,
                    columns=[
                        DisplayLookup.CAMPAIGN_STATISTICS["columns"][col] for col in DisplayLookup.CAMPAIGN_STATISTICS["columns"]
                    ]
                    # display_mode=DisplayMode.TABLE,
                    # display_lookup=DisplayLookup.CAMPAIGN_STATISTICS
                )
            )
        ]
    except Exception as e:
        session.close()
        logs.error(f"Error showing campaign statistics: \n{e}")
        return JSONResponse(content={
            "success": False, 
            "msg": "Error showing campaign statistics. Check logs for more details"
            })