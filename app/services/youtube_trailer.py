from ..utilities.config import settings
from ..middlewares.logger import get_logger
import httpx
from fastapi import HTTPException

logger = get_logger(__name__)

async def get_trailer_from_youtube(movie_name:str):
    logger.info(f"Fetching YouTube trailer for movie: {movie_name}")
    search_query = f"{movie_name} official trailer"
    params = {
        "q": search_query,
        "part": "snippet",
        "type": "video",
        "key": settings.YOUTUBE_API_KEY,
        "maxResults": 1
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.YOUTUBE_API_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('items'):
                video_id = data['items'][0]['id']['videoId']
                trailer_url = f"https://www.youtube.com/watch?v={video_id}"
                logger.info(f"Found YouTube trailer for {movie_name}: {trailer_url}")
                return {"trailer_url": trailer_url, "title": data['items'][0]['snippet']['title']}
            else:
                logger.warning(f"No YouTube trailer found for movie: {movie_name}")
                return {"trailer_url": None, "title": None}
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching YouTube trailer for {movie_name}: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Error fetching trailer: {e}")
    except httpx.RequestError as e:
        logger.error(f"Request error fetching YouTube trailer for {movie_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching trailer: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error fetching YouTube trailer for {movie_name}: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching trailer")
        
   