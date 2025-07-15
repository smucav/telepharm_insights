from fastapi import FastAPI, Depends, HTTPException
from typing import List
from .schemas import ChannelActivity, TopProduct, MessageSearch
from .crud import get_top_products, get_channel_activity, search_messages
from .database import get_db
import logging

# Set up logging
logging.basicConfig(
    filename='api/logs/api.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = FastAPI(title="TelePharm Insights API", version="1.0.0")

@app.get("/api/reports/top-products", response_model=List[TopProduct])
async def top_products(limit: int = 10, db=Depends(get_db)):
    """Get the most frequently mentioned products."""
    try:
        results = get_top_products(db, limit)
        logger.info(f"Fetched top {limit} products")
        return results
    except Exception as e:
        logger.error(f"Error fetching top products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/channels/{channel_name}/activity", response_model=List[ChannelActivity])
async def channel_activity(channel_name: str, db=Depends(get_db)):
    """Get posting activity for a specific channel"""
    try:
        results = get_channel_activity(db, channel_name)
        logger.info(f"Fetched activity for channel={channel_name}")
        return results
    except Exception as e:
        logger.error(f"Error fetching activity for channel={channel_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search/messages", response_model=List[MessageSearch])
async def search_messages_endpoint(query: str, db=Depends(get_db)):
    """Search message containing a specific keyword."""
    try:
        results = search_messages(db, query)
        logger.info(f"Searched messages for query={query}")
        return results
    except Exception as e:
        logger.error(f"Error searching messages for query={query}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
