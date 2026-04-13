from bs4 import BeautifulSoup
from fastapi import HTTPException,Response
import requests
import re
import urllib.parse
from ..middlewares.logger import get_logger

logger = get_logger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-GB,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

async def fetch_movie_list(movie_name: str,response:Response): 
    logger.info(f"Fetching movie list for: {movie_name}")
    url = f"https://www.themoviedb.org/search/movie?query={movie_name}&language=en-GB"
    try:
        tmdb_response = requests.get(url,headers=HEADERS, timeout=10)
        tmdb_response.raise_for_status()
    except requests.Timeout:
        logger.error(f"Request to TMDB timed out for movie: {movie_name}")
        raise HTTPException(status_code=504, detail="Request to TMDB timed out")
    except requests.RequestException as e:
        logger.error(f"Error fetching movie list for {movie_name}: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Error fetching movie list: {str(e)}")

    soup = BeautifulSoup(tmdb_response.text, 'html.parser')
    movies=[]
    for card in soup.select('div[class*="media-card"]'):
        movie_link = card.select_one('a[data-media-type="movie"]')

        if not movie_link:
            continue

        href = movie_link.get('href')
        movie_url = f"https://www.themoviedb.org{href}"

        movies.append({
            "title": card.select_one('h2').get_text(strip=True) if card.select_one('h2') else "Unknown",
            "poster": card.select_one('img')['src'] if card.select_one('img') else "No poster available",
            "release_date": card.select_one('span.release_date').get_text(strip=True) if card.select_one('span.release_date') else "Unknown",
            "overview": card.select_one('div.overview p').get_text(strip=True) if card.select_one('div.overview p') else "Overview not available",
            "url": movie_url,
        })

    return movies  


async def get_movie_details(movie_url):
    logger.info(f"Fetching movie details for URL: {movie_url}")
    try:
        response = requests.get(movie_url, timeout=10)
        response.raise_for_status()
    except requests.Timeout:
        logger.error(f"Request to TMDB timed out for movie URL: {movie_url}")
        return {"error": "Request to TMDB timed out"}
    except requests.RequestException as e:
        logger.error(f"Error fetching movie details for {movie_url}: {str(e)}")
        return {"error": f"Error fetching movie details: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    director = next(
        (profile.select_one('a').get_text(strip=True)
         for profile in soup.select('li.profile')
         if profile.select_one('p.character') and 'Director' in profile.select_one('p.character').text),
        None
    )

    if not director:
        return {
            "director": None, "cast": [], "genres": [],
            "runtime": "Unknown", "certificate": "Unknown",
            "language": "Unknown", "watch_link": "No watch link available",
            "backdrops": []
        }

    cast = [
        (card.select_one('p').get_text(strip=True), card.select_one('img')['src'] if card.select_one('img') else "No Image")
        for card in soup.select('li.card')
    ]

    genres = [genre.get_text(strip=True) for genre in soup.select('span.genres a')]

    facts_section = soup.select_one('div.facts')
    runtime = facts_section.select_one('span.runtime').get_text(strip=True) if facts_section and facts_section.select_one('span.runtime') else "Unknown"
    certificate = facts_section.select_one('span.certification').get_text(strip=True) if facts_section and facts_section.select_one('span.certification') else "Unknown"

    language = next(
        (tag.find_parent().get_text(strip=True).replace("Original Language", "").strip()
         for tag in soup.find_all('strong', string=re.compile(r'Original Language', re.IGNORECASE))),
        "Unknown"
    )

    watch_link_element = soup.select_one('a[href*="/watch"]')
    streaming_url = f"https://www.themoviedb.org{watch_link_element['href']}" if watch_link_element else "No watch link available"
    watch_links = await fetch_watch_links(streaming_url) if watch_link_element else ["No watch links available"]

    backdrops = await fetch_backdrop_images(movie_url)
    overview_element = soup.select_one('div.overview p')
    overview = overview_element.get_text(strip=True) if overview_element else "No overview available"

    return {
        "director": director,
        "cast": cast,
        "genres": genres,
        "runtime": runtime,
        "certificate": certificate,
        "language": language,
        "watch_link": watch_links,
        "backdrops": backdrops,
        "overview": overview 
    }


async def fetch_backdrop_images(movie_url):
    logger.info(f"Fetching backdrop images for movie URL: {movie_url}")
    backdrop_url = movie_url.replace("?language=en-GB", "") + "/images/backdrops?language=en-GB"

    try:
        response = requests.get(backdrop_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        images = set(a['href'] for a in soup.select('a[title="View Original"]'))

        return list(images) if images else ["No backdrop images available"]

    except requests.RequestException as e:
        logger.error(f"Error fetching backdrop images for {movie_url}: {e}")
        return {"error": "Failed to fetch backdrop images"}


async def fetch_watch_links(streaming_url):
    logger.info(f"Fetching watch links for streaming URL: {streaming_url}")
    try:
        response = requests.get(streaming_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        stream_section = soup.find('h3', string=re.compile(r'Stream', re.IGNORECASE))
        if not stream_section:
            return ["No watch links available"]

        watch_links = []
        for link in stream_section.find_next('ul', class_='providers').find_all('a', href=True):
            match = re.search(r'r=(https%3A%2F%2F[^\&]+)', link['href'])
            icon = link.find('img')['src'] if link.find('img') else None
            if match and icon:
                clean_url = urllib.parse.unquote(match.group(1))
                if not any(item['url'] == clean_url for item in watch_links):
                    watch_links.append({'icon': icon, 'url': clean_url})

        return watch_links if watch_links else ["No watch links available"]

    except requests.RequestException as e:
        logger.error(f"Error fetching watch links for {streaming_url}: {e}")
        return {"error": "Failed to fetch watch links"}




async def fetch_all_movies_by_category(category: str, base_url: str, response: Response = None):
    logger.info(f"Fetching {category} movie list")
    url = base_url
    try:
        tmdb_response = requests.get(url, headers=HEADERS, timeout=10)
        tmdb_response.raise_for_status()
    except requests.Timeout:
        logger.error(f"Request to TMDB timed out for {category} movies")
        raise HTTPException(status_code=504, detail="Request to TMDB timed out")
    except requests.RequestException as e:
        logger.error(f"Error fetching {category} movie list: {str(e)}")
        raise HTTPException(status_code=502, detail=f"Error fetching movie list: {str(e)}")

    soup = BeautifulSoup(tmdb_response.text, 'html.parser')
    movies = []
    for card in soup.select('div[class*="poster-card"]'):
        movie_link = card.select_one('a[data-media-type="movie"]')
        if not movie_link:
            continue
        href = movie_link.get('href')
        movie_url = f"https://www.themoviedb.org{href}"
        img_tag = card.select_one('img.poster')
        title = img_tag.get('alt') if img_tag else "Unknown"
        poster = img_tag.get('src') if img_tag else "No poster available"
        release_date_tag = card.select_one('span.subheader') or card.select_one('span.release_date')
        overview_tag = card.select_one('div.overview p')

        movies.append({
            "title": title,
            "poster": poster,
            "release_date": release_date_tag.get_text(strip=True) if release_date_tag else "Unknown",
            "overview": overview_tag.get_text(strip=True) if overview_tag else "Overview not available",
            "url": movie_url,
        })

    return movies