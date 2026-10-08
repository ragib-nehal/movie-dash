"""Testable data transformations for the MovieLens dashboard."""

from collections.abc import Sequence
import math
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "user_id",
    "movie_id",
    "rating",
    "title",
    "year",
    "genres",
}


def load_ratings(path: str | Path) -> pd.DataFrame:
    """Load ratings data and validate the fields used by the dashboard."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise FileNotFoundError(f"Ratings file not found: {csv_path}")

    ratings = pd.read_csv(csv_path)
    missing = sorted(REQUIRED_COLUMNS.difference(ratings.columns))
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    ratings = ratings.copy()
    numeric_ratings = pd.to_numeric(ratings["rating"], errors="coerce")
    if (~numeric_ratings.between(1, 5)).any():
        raise ValueError("Rating values must be finite numbers from 1 to 5")

    raw_years = ratings["year"]
    numeric_years = pd.to_numeric(raw_years, errors="coerce")
    missing_years = raw_years.isna()
    provided_years = numeric_years.loc[~missing_years]
    years_are_valid = (
        provided_years.notna()
        & provided_years.map(math.isfinite)
        & provided_years.mod(1).eq(0)
    )
    if not years_are_valid.all():
        raise ValueError("Release year values must be finite whole numbers or missing")

    ratings["rating"] = numeric_ratings
    ratings["year"] = numeric_years
    return ratings


def _split_genres(value: object) -> list[str]:
    if pd.isna(value) or not str(value).strip():
        return ["Unknown"]
    return [
        "Unknown" if genre.strip().lower() == "unknown" else genre.strip()
        for genre in str(value).split("|")
    ]


def genre_distribution(ratings: pd.DataFrame) -> pd.DataFrame:
    """Count unique rated movies once in each of their listed genres."""
    movie_genres = ratings.loc[:, ["movie_id", "genres"]].drop_duplicates()
    exploded = movie_genres.assign(genre=movie_genres["genres"].map(_split_genres)).explode("genre")
    counts = (
        exploded.loc[:, ["movie_id", "genre"]]
        .drop_duplicates()
        .groupby("genre", as_index=False)
        .agg(movie_count=("movie_id", "nunique"))
    )
    return counts.sort_values(
        ["movie_count", "genre"], ascending=[False, True], ignore_index=True
    )


def genre_satisfaction(ratings: pd.DataFrame) -> pd.DataFrame:
    """Average rating events across every genre assigned to each movie."""
    exploded = ratings.assign(genre=ratings["genres"].map(_split_genres)).explode("genre")
    summary = (
        exploded.groupby("genre", as_index=False)
        .agg(mean_rating=("rating", "mean"), rating_count=("rating", "count"))
    )
    return summary.sort_values(
        ["mean_rating", "rating_count", "genre"],
        ascending=[False, False, True],
        ignore_index=True,
    )


def release_year_trend(
    ratings: pd.DataFrame, genres: Sequence[str] | None = None
) -> pd.DataFrame:
    """Calculate rating-event means by movie release year."""
    selected = {genre.strip() for genre in genres or [] if genre.strip()}
    filtered = ratings
    if selected:
        matches = ratings["genres"].map(
            lambda value: bool(selected.intersection(_split_genres(value)))
        )
        filtered = ratings.loc[matches]

    valid = filtered.assign(year=pd.to_numeric(filtered["year"], errors="coerce")).dropna(
        subset=["year", "rating"]
    )
    if valid.empty:
        return pd.DataFrame(columns=["year", "mean_rating", "rating_count"])

    valid = valid.assign(year=valid["year"].astype(int))
    trend = (
        valid.groupby("year", as_index=False)
        .agg(mean_rating=("rating", "mean"), rating_count=("rating", "count"))
        .sort_values("year", ignore_index=True)
    )
    return trend.loc[:, ["year", "mean_rating", "rating_count"]]


def top_movies(
    ratings: pd.DataFrame, min_ratings: int, limit: int = 5
) -> pd.DataFrame:
    """Rank movies meeting an inclusive minimum number of ratings."""
    if min_ratings < 1:
        raise ValueError("min_ratings must be at least 1")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    summary = (
        ratings.groupby(["movie_id", "title"], as_index=False, dropna=False)
        .agg(mean_rating=("rating", "mean"), rating_count=("rating", "count"))
    )
    eligible = summary.loc[summary["rating_count"] >= min_ratings]
    ranked = eligible.sort_values(
        ["mean_rating", "rating_count", "title"],
        ascending=[False, False, True],
        ignore_index=True,
    ).head(limit)
    return ranked.loc[:, ["movie_id", "title", "mean_rating", "rating_count"]]
