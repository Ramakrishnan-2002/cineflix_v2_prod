from fastapi import APIRouter, Depends, HTTPException,status,Request
from ..databases.models import Review, User, ReviewItem
from ..configs.security import get_current_user
from ..middlewares.logger import get_logger
from ..middlewares.rate_limiter import limiter
from ..schemas.review_schemas import ReviewCreateModel,ReviewEditModel,ReviewResponseModel,ReviewItemResposnseModel
from ..schemas.user_schemas import UserResponse

router= APIRouter(prefix="/reviews", tags=["reviews"])
logger = get_logger(__name__)


@router.post("/create",status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_review(request : Request,review: ReviewCreateModel, current_user: User = Depends(get_current_user)):
    try:
        existing_movie = await Review.find_one(Review.movie_name == review.movie_name)
        new_review = ReviewItem(review_content=review.review_content,rating=review.rating,created_by=current_user)
        if existing_movie:
            for review_ in existing_movie.reviews:
                if review_.created_by.id == current_user.id:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You have already reviewed this movie")
            existing_movie.reviews.append(new_review)
            total_ratings= sum(r.rating for r in existing_movie.reviews)
            existing_movie.overall_rating = total_ratings/len(existing_movie.reviews)
            await existing_movie.save() 
            logger.info(f"Review added for movie: {review.movie_name} by user: {current_user.email}")
            return {"message": "Review added successfully"}
        else:
            new_review = Review(movie_name=review.movie_name,release_date=review.release_date,overall_rating=review.rating,reviews=[new_review])
            await new_review.insert()
            logger.info(f"Review created for movie: {review.movie_name} by user: {current_user.email}")
            return {"message": "Review created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error creating review: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/edit/{movie_name}/{release_date}",status_code=status.HTTP_200_OK) 
@limiter.limit("10/minute")
async def edit_review(request : Request,movie_name:str,release_date:str,review_update: ReviewEditModel, current_user: User = Depends(get_current_user)):
    try:
        existing_movie = await Review.find_one(Review.movie_name == movie_name, Review.release_date == release_date)
        if not existing_movie:
            logger.warning(f"Review edit failed - movie not found: {movie_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie review not found")
        review_to_edit = None
        for review in existing_movie.reviews:
            if review.created_by.id == current_user.id:
                review_to_edit = review
                break
        if not review_to_edit:
            logger.warning(f"Review edit failed - user {current_user.email} has no review for movie: {movie_name}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own reviews")
        review_to_edit.review_content = review_update.review_content
        review_to_edit.rating = review_update.rating
        total_ratings= sum(r.rating for r in existing_movie.reviews)
        existing_movie.overall_rating = total_ratings/len(existing_movie.reviews)
        await existing_movie.save()
        logger.info(f"Review edited for movie: {movie_name} by user: {current_user.email}")
        return {"message": "Review updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error editing review: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/delete/{movie_name}/{release_date}",status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def delete_review(request : Request,movie_name:str,release_date:str, current_user: User = Depends(get_current_user)):
    try:
        existing_movie = await Review.find_one(Review.movie_name == movie_name, Review.release_date == release_date)
        if not existing_movie:
            logger.warning(f"Review delete failed - movie not found: {movie_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie review not found")
        review_to_delete = None
        for review in existing_movie.reviews:
            if review.created_by.id == current_user.id:
                review_to_delete = review
                break
        if not review_to_delete:
            logger.warning(f"Review delete failed - user {current_user.email} has no review for movie: {movie_name}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own reviews")
        existing_movie.reviews.remove(review_to_delete)
        if existing_movie.reviews:
            total_ratings= sum(r.rating for r in existing_movie.reviews)
            existing_movie.overall_rating = total_ratings/len(existing_movie.reviews)
        else:
            existing_movie.overall_rating = 0
        await existing_movie.save()
        logger.info(f"Review deleted for movie: {movie_name} by user: {current_user.email}")
        return {"message": "Review deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error deleting review: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@router.get("/movie/{movie_name}/{release_date}",status_code=status.HTTP_200_OK,response_model=ReviewResponseModel)
@limiter.limit("20/minute")
async def get_review(request : Request,movie_name:str,release_date:str):
    try:
        existing_movie = await Review.find_one(Review.movie_name == movie_name, Review.release_date == release_date)
        if not existing_movie:
            logger.warning(f"Review fetch failed - movie not found: {movie_name}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie review not found")
        overall_rating = round(sum(r.rating for r in existing_movie.reviews) / len(existing_movie.reviews), 2) if existing_movie.reviews else 0.0
        reviews_of_cur_user= []
        for review in existing_movie.reviews:
            user_model = await User.find_one(User.id == review.created_by.id)
            if not user_model:
                logger.warning(f"User not found for review: {review.created_by.id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for review")
            reviews_of_cur_user.append(
                ReviewItemResposnseModel(
                    review_content=review.review_content,
                    rating=review.rating,
                    created_by=UserResponse(
                        id=user_model.id,
                        name=user_model.name,
                        email=user_model.email,
                        created_at=user_model.created_at
                    ),
                    created_at=review.created_at
                )
            )
        logger.info(f"Review fetched for movie: {movie_name}")
        return ReviewResponseModel(
            movie_name=existing_movie.movie_name,
            release_date=existing_movie.release_date,
            overall_rating=overall_rating,
            reviews=reviews_of_cur_user
        )
    except HTTPException:
        raise 
    except Exception as e:
        logger.exception(f"Unexpected error fetching review: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))