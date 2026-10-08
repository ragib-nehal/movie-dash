from pathlib import Path

import pandas as pd
import pytest

from analysis import (
    genre_distribution,
    genre_satisfaction,
    load_ratings,
    release_year_trend,
    top_movies,
)


@pytest.fixture
def ratings() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"user_id": 1, "movie_id": 10, "rating": 5, "title": "Double Bill", "year": 2000, "genres": "Drama|Comedy"},
            {"user_id": 2, "movie_id": 10, "rating": 1, "title": "Double Bill", "year": 2000, "genres": "Drama|Comedy"},
            {"user_id": 1, "movie_id": 20, "rating": 4, "title": "Straight Drama", "year": 2001, "genres": "Drama"},
            {"user_id": 3, "movie_id": 30, "rating": 2, "title": "Mystery Date", "year": None, "genres": "unknown"},
        ]
    )


def test_genre_distribution_counts_each_movie_once_per_genre(ratings: pd.DataFrame) -> None:
    result = genre_distribution(ratings)

    assert list(result.columns) == ["genre", "movie_count"]
    assert result.to_dict("records") == [
        {"genre": "Drama", "movie_count": 2},
        {"genre": "Comedy", "movie_count": 1},
        {"genre": "Unknown", "movie_count": 1},
    ]


def test_genre_satisfaction_is_weighted_by_rating_events(ratings: pd.DataFrame) -> None:
    result = genre_satisfaction(ratings).set_index("genre")

    assert list(result.columns) == ["mean_rating", "rating_count"]
    assert result.loc["Drama", "mean_rating"] == pytest.approx(10 / 3)
    assert result.loc["Drama", "rating_count"] == 3
    assert result.loc["Comedy", "mean_rating"] == pytest.approx(3.0)
    assert result.loc["Comedy", "rating_count"] == 2


def test_release_year_trend_excludes_missing_years(ratings: pd.DataFrame) -> None:
    result = release_year_trend(ratings)

    assert result.to_dict("records") == [
        {"year": 2000, "mean_rating": 3.0, "rating_count": 2},
        {"year": 2001, "mean_rating": 4.0, "rating_count": 1},
    ]


def test_release_year_trend_does_not_duplicate_multigenre_matches(ratings: pd.DataFrame) -> None:
    result = release_year_trend(ratings, genres=["Drama", "Comedy"])

    assert result.to_dict("records") == [
        {"year": 2000, "mean_rating": 3.0, "rating_count": 2},
        {"year": 2001, "mean_rating": 4.0, "rating_count": 1},
    ]


def test_release_year_trend_treats_empty_selection_as_all_data(ratings: pd.DataFrame) -> None:
    pd.testing.assert_frame_equal(
        release_year_trend(ratings, genres=[]),
        release_year_trend(ratings),
    )


def test_top_movies_uses_inclusive_floor_and_deterministic_ties() -> None:
    frame = pd.DataFrame(
        [
            {"movie_id": 1, "title": "Zulu", "rating": 4},
            {"movie_id": 1, "title": "Zulu", "rating": 4},
            {"movie_id": 2, "title": "Alpha", "rating": 4},
            {"movie_id": 2, "title": "Alpha", "rating": 4},
            {"movie_id": 3, "title": "Popular", "rating": 4},
            {"movie_id": 3, "title": "Popular", "rating": 4},
            {"movie_id": 3, "title": "Popular", "rating": 4},
            {"movie_id": 4, "title": "Tiny Perfect", "rating": 5},
        ]
    )

    result = top_movies(frame, min_ratings=2, limit=3)

    assert list(result.columns) == ["movie_id", "title", "mean_rating", "rating_count"]
    assert result["title"].tolist() == ["Popular", "Alpha", "Zulu"]
    assert result["rating_count"].tolist() == [3, 2, 2]


def test_load_ratings_validates_required_columns(tmp_path: Path) -> None:
    csv_path = tmp_path / "ratings.csv"
    pd.DataFrame({"movie_id": [1], "rating": [5]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="Missing required columns"):
        load_ratings(csv_path)


def test_load_ratings_rejects_unusable_rating_values(tmp_path: Path) -> None:
    csv_path = tmp_path / "ratings.csv"
    pd.DataFrame(
        {
            "user_id": [1],
            "movie_id": [1],
            "rating": ["not-a-number"],
            "title": ["Broken"],
            "year": [2000],
            "genres": ["Drama"],
        }
    ).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="no usable rating values"):
        load_ratings(csv_path)


def test_load_ratings_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Ratings file not found"):
        load_ratings(tmp_path / "missing.csv")
