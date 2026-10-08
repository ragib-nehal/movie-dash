import json
from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).parents[1] / "app.py"


def test_dashboard_renders_required_sections_and_controls() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=20).run()

    assert not app.exception
    assert app.title[0].value == "MovieDash, frame by frame"
    assert [metric.label for metric in app.metric] == ["Ratings", "Movies", "Viewers"]
    assert [heading.value for heading in app.subheader] == [
        "1. What genres were rated?",
        "2. Which genres satisfy viewers most?",
        "3. How did ratings change across release years?",
        "4. Which movies rise above the rating floor?",
    ]
    assert len(app.multiselect) == 1
    assert len(app.segmented_control) == 1
    assert len(app.toggle) == 1
    assert app.toggle[0].label == "Dark mode"
    assert app.segmented_control[0].options == ["50 ratings", "150 ratings"]
    assert len(app.get("plotly_chart")) == 4


def test_dashboard_controls_rerun_without_errors() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=20).run()

    app.multiselect[0].set_value(["Drama", "Comedy"]).run()
    app.segmented_control[0].set_value("150 ratings").run()

    assert not app.exception
    assert app.multiselect[0].value == ["Drama", "Comedy"]
    assert app.segmented_control[0].value == "150 ratings"


def test_dark_mode_updates_chart_palette_and_persists_across_reruns() -> None:
    app = AppTest.from_file(APP_PATH, default_timeout=20).run()
    light_chart = json.loads(app.get("plotly_chart")[0].proto.spec)

    app.toggle[0].set_value(True).run()
    dark_chart = json.loads(app.get("plotly_chart")[0].proto.spec)
    app.segmented_control[0].set_value("150 ratings").run()

    assert light_chart["layout"]["font"]["color"] == "#172033"
    assert dark_chart["layout"]["font"]["color"] == "#F4EFE6"
    assert dark_chart["data"][0]["marker"]["color"] == "#EF6A5B"
    assert app.toggle[0].value is True


def test_dashboard_reports_malformed_data_without_a_traceback(
    tmp_path: Path, monkeypatch
) -> None:
    csv_path = tmp_path / "malformed.csv"
    pd.DataFrame(
        {
            "user_id": [1],
            "movie_id": [1],
            "rating": [5],
            "title": ["Broken Year"],
            "year": [float("inf")],
            "genres": ["Drama"],
        }
    ).to_csv(csv_path, index=False)
    monkeypatch.setenv("MOVIEDASH_DATA_PATH", str(csv_path))

    app = AppTest.from_file(APP_PATH, default_timeout=20).run()

    assert not app.exception
    assert len(app.error) == 1
    assert "Release year values must be finite whole numbers or missing" in app.error[0].value
