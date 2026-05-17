"""
Клієнт для Art Institute of Chicago API.
Документація: https://api.artic.edu/docs/#collections
"""

import httpx
from fastapi import HTTPException, status

AIC_BASE_URL = "https://api.artic.edu/api/v1"
AIC_FIELDS = "id,title"


def validate_artwork_exists(external_id: int) -> dict:
    """
    Перевіряє що експонат існує в AIC API.
    Повертає дані експоната або кидає 422 якщо не знайдено.
    """
    url = f"{AIC_BASE_URL}/artworks/{external_id}"
    params = {"fields": AIC_FIELDS}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url, params=params)

        if response.status_code == 404:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Artwork with id={external_id} not found in Art Institute of Chicago API"
            )

        response.raise_for_status()
        return response.json().get("data")

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Art Institute of Chicago API is not responding. Try again later."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Art Institute of Chicago API error: {e.response.status_code}"
        )