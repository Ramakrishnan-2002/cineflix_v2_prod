from fastapi import APIRouter, Depends, HTTPException,status,Request,Response
from ..configs.security import get_current_user
from ..services.scraper import fetch_movie_list, get_movie_details, fetch_watch_links, fetch_backdrop_images
from ..middlewares.logger import get_logger
from fastapi.responses import JSONResponse

router= APIRouter(prefix="/movies", tags=["movies"])
logger = get_logger(__name__)

@router.get("/search/{movie_name}",status_code=status.HTTP_200_OK)
async def search_movies(request : Request,movie_name:str,response:Response):
    movies=  fetch_movie_list(movie_name,response)
    if not movies:
        logger.info(f"No movies found for search term: {movie_name}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found")
    logger.info(f"Found {len(movies)} movies for search term: {movie_name}")
    return JSONResponse(movies)


