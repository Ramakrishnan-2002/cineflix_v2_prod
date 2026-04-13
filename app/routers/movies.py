from fastapi import APIRouter, Depends, HTTPException,status,Request,Response
from ..configs.security import get_current_user
from ..services.scraper import  fetch_movie_list, get_movie_details,fetch_all_movies_by_category
from ..middlewares.logger import get_logger
from fastapi.responses import JSONResponse
from ..schemas.movie_schemas import MovieBasic,MovieDetails,YoutubeTrailerResponse
from ..services.youtube_trailer import get_trailer_from_youtube
import requests


router= APIRouter(prefix="/movies", tags=["movies"])
logger = get_logger(__name__)

@router.get("/search/{movie_name}",status_code=status.HTTP_200_OK,response_model=list[MovieBasic])
async def search_movies(request : Request,movie_name:str,response:Response,current_user: str = Depends(get_current_user)):
    movies= await fetch_movie_list(movie_name,response)
    if not movies:
        logger.info(f"No movies found for search term: {movie_name}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No movies found")
    logger.info(f"Found {len(movies)} movies for search term: {movie_name}")
    return movies


@router.get("/details",status_code=status.HTTP_200_OK,response_model=list[MovieDetails])
async def get_full_movie_details(movie_url:str,current_user: str = Depends(get_current_user)):
    if not movie_url.startswith("https://www.themoviedb.org/movie/"):
        logger.warning(f"Invalid movie URL provided: {movie_url}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid movie URL")
    try:
        details=await get_movie_details(movie_url)
        movies=MovieDetails(**details)
        return JSONResponse(content=movies.model_dump(), status_code=status.HTTP_200_OK)
    except requests.Timeout:
        logger.error(f"Request to fetch movie details timed out for URL: {movie_url}")
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail="Request timed out while fetching movie details")
    except requests.RequestException as e:
        logger.error(f"Error fetching movie details for URL {movie_url}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Error fetching movie details: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching movie details for URL {movie_url}: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")
    

@router.get("/trailer/{movie_name}",status_code=status.HTTP_200_OK,response_model=YoutubeTrailerResponse)
async def get_movie_trailer(movie_name:str,current_user: str = Depends(get_current_user)):
   
    trailer_url = await get_trailer_from_youtube(movie_name)
    if "Error" in trailer_url or "No trailer found" in trailer_url:
        logger.warning(f"Trailer not found for movie: {movie_name}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=trailer_url)
    logger.info(f"Trailer found for movie: {movie_name}, URL: {trailer_url}")
    return trailer_url


@router.get("/popular",status_code=status.HTTP_200_OK,response_model=list[MovieBasic])
async def get_popular_movies(current_user: str = Depends(get_current_user)):
    movies= await fetch_all_movies_by_category("popular", "https://www.themoviedb.org/movie")
    if not movies:
        logger.info("No popular movies found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No popular movies found")
    logger.info(f"Found {len(movies)} popular movies")
    return movies


@router.get("/upcoming",status_code=status.HTTP_200_OK,response_model=list[MovieBasic])
async def get_upcoming_movies(current_user: str = Depends(get_current_user)):
    movies= await fetch_all_movies_by_category("upcoming", "https://www.themoviedb.org/movie/upcoming")
    if not movies:
        logger.info("No upcoming movies found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No upcoming movies found")
    logger.info(f"Found {len(movies)} upcoming movies")
    return movies



@router.get("/toprated",status_code=status.HTTP_200_OK,response_model=list[MovieBasic])
async def get_top_rated_movies(current_user: str = Depends(get_current_user)):
    movies= await fetch_all_movies_by_category("top_rated", "https://www.themoviedb.org/movie/top-rated")
    if not movies:
        logger.info("No top-rated movies found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No top-rated movies found")
    logger.info(f"Found {len(movies)} top-rated movies")
    return movies