from pydantic import BaseModel


class MovieBasic(BaseModel):
    title : str
    poster : str
    release_date : str
    overview : str 
    url : str

class MovieDetails(BaseModel):
    director : str | None
    cast : list
    genres : list[str]
    runtime : str
    certificate : str
    language : str
    watch_link : list
    backdrops : list[str]
    overview : str

class YoutubeTrailerResponse(BaseModel):
    trailer_url: str | None
    title: str | None