"""Streamlit entrypoint for the MovieDash dashboard."""

import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    genre_distribution,
    genre_satisfaction,
    load_ratings,
    release_year_trend,
    top_movies,
)


DATA_PATH = Path(
    os.environ.get(
        "MOVIEDASH_DATA_PATH",
        Path(__file__).parent / "data" / "movie_ratings.csv",
    )
)
LIGHT_THEME = {
    "background": "#F7F4EC",
    "surface": "#EEE9DE",
    "text": "#172033",
    "muted": "#526071",
    "accent": "#C84A3A",
    "gold": "#D8A43B",
    "grid": "rgba(82,96,113,0.16)",
    "hover_text": "#FFFFFF",
}
DARK_THEME = {
    "background": "#0E1420",
    "surface": "#171F2D",
    "text": "#F4EFE6",
    "muted": "#B8C1CE",
    "accent": "#EF6A5B",
    "gold": "#E2B95E",
    "grid": "rgba(184,193,206,0.18)",
    "hover_text": "#0E1420",
}


st.set_page_config(
    page_title="MovieDash, frame by frame",
    page_icon="🎞️",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def get_ratings(path: str) -> pd.DataFrame:
    """Load and cache the dashboard's source file."""
    return load_ratings(path)


def style_figure(
    figure: go.Figure, palette: dict[str, str], *, height: int = 480
) -> go.Figure:
    """Apply the shared film-catalog chart treatment."""
    figure.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Arial, sans-serif", "color": palette["text"], "size": 13},
        margin={"l": 12, "r": 18, "t": 24, "b": 48},
        hoverlabel={
            "bgcolor": palette["text"],
            "font_color": palette["hover_text"],
        },
        showlegend=False,
    )
    figure.update_xaxes(showgrid=True, gridcolor=palette["grid"], zeroline=False)
    figure.update_yaxes(showgrid=False, zeroline=False)
    return figure


def render_dashboard() -> None:
    mode_column, toggle_column = st.columns([4, 1])
    with toggle_column:
        dark_mode = st.toggle("Dark mode", key="dark_mode")
    palette = DARK_THEME if dark_mode else LIGHT_THEME

    st.markdown(
        f"""
        <style>
        :root {{ color-scheme: {'dark' if dark_mode else 'light'}; }}
        .stApp, [data-testid="stAppViewContainer"] {{ background: {palette['background']}; color: {palette['text']}; }}
        [data-testid="stHeader"] {{ background: {palette['background']}; }}
        .block-container {{ max-width: 1120px; padding-top: 3.25rem; padding-bottom: 5rem; }}
        h1, h2, h3 {{ font-family: Georgia, 'Times New Roman', serif !important; color: {palette['text']} !important; }}
        h1 {{ max-width: 760px; font-size: clamp(2.7rem, 7vw, 5.6rem) !important; line-height: .94 !important; letter-spacing: -.04em !important; }}
        h3 {{ font-size: clamp(1.55rem, 3vw, 2.2rem) !important; margin-top: 2.8rem !important; }}
        p, label, [data-testid="stCaptionContainer"] {{ color: {palette['muted']}; }}
        [data-testid="stWidgetLabel"] p {{ color: {palette['text']}; }}
        [data-baseweb="select"] > div {{ background: {palette['surface']}; border-color: {palette['muted']}; }}
        [data-testid="stMetric"] {{ border-top: 2px solid {palette['text']}; padding-top: .8rem; }}
        [data-testid="stMetricLabel"] {{ font-size: .86rem; }}
        [data-testid="stMetricValue"] {{ font-family: Georgia, 'Times New Roman', serif; color: {palette['text']}; }}
        [data-testid="stPlotlyChart"] {{ border-bottom: 1px solid {palette['grid']}; padding-bottom: 1.1rem; }}
        .catalog-intro {{ max-width: 720px; font-size: 1.08rem; line-height: 1.65; margin-bottom: 2rem; }}
        .method-note {{ border-left: 1px solid {palette['gold']}; padding-left: .9rem; margin: .3rem 0 1rem; color: {palette['muted']}; }}
        hr {{ border-color: {palette['grid']} !important; margin: 2.8rem 0 !important; }}
        ::selection {{ background: {palette['accent']}; color: {palette['hover_text']}; }}
        :focus-visible {{ outline: 3px solid {palette['gold']} !important; outline-offset: 2px; }}
        ::-webkit-scrollbar {{ width: 10px; }}
        ::-webkit-scrollbar-track {{ background: {palette['background']}; }}
        ::-webkit-scrollbar-thumb {{ background: {palette['muted']}; border: 3px solid {palette['background']}; border-radius: 8px; }}
        @media (max-width: 640px) {{
          .block-container {{ padding-top: 4rem; }}
          h1 {{ font-size: 3rem !important; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    try:
        ratings = get_ratings(str(DATA_PATH))
    except (FileNotFoundError, ValueError) as error:
        st.error(f"The MovieDash data could not be loaded. {error}")
        st.stop()

    st.title("MovieDash, frame by frame")
    st.markdown(
        '<p class="catalog-intro">A guided look at what viewers rated, which genres earned their confidence, how reception shifted across release years, and which films still lead when popularity matters.</p>',
        unsafe_allow_html=True,
    )

    metric_columns = st.columns(3)
    metric_columns[0].metric("Ratings", f"{len(ratings):,}")
    metric_columns[1].metric("Movies", f"{ratings['movie_id'].nunique():,}")
    metric_columns[2].metric("Viewers", f"{ratings['user_id'].nunique():,}")

    st.subheader("1. What genres were rated?")
    st.markdown(
        '<p class="method-note"><strong>How this is counted:</strong> Each movie counts once in every listed genre. Multi-genre films therefore appear in more than one bar.</p>',
        unsafe_allow_html=True,
    )
    distribution = genre_distribution(ratings)
    distribution_chart = px.bar(
        distribution,
        x="movie_count",
        y="genre",
        orientation="h",
        text="movie_count",
        labels={"movie_count": "Rated movies", "genre": "Genre"},
        color_discrete_sequence=[palette["accent"]],
    )
    distribution_chart.update_traces(
        texttemplate="%{text:,}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>%{x:,} rated movies<extra></extra>",
    )
    distribution_chart.update_yaxes(categoryorder="total ascending")
    st.plotly_chart(style_figure(distribution_chart, palette, height=570), width="stretch", config={"displayModeBar": False})

    st.subheader("2. Which genres satisfy viewers most?")
    st.markdown(
        '<p class="method-note"><strong>How this is counted:</strong> Every rating contributes to each genre assigned to its movie. Bars are sorted by the unrounded mean on the 1–5 scale.</p>',
        unsafe_allow_html=True,
    )
    satisfaction = genre_satisfaction(ratings)
    satisfaction_chart = px.bar(
        satisfaction,
        x="mean_rating",
        y="genre",
        orientation="h",
        text="mean_rating",
        custom_data=["rating_count"],
        labels={"mean_rating": "Average rating", "genre": "Genre"},
        color="mean_rating",
        color_continuous_scale=[(0, palette["muted"]), (0.58, palette["gold"]), (1, palette["accent"])],
        range_color=(1, 5),
    )
    satisfaction_chart.update_traces(
        texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False,
        hovertemplate="<b>%{y}</b><br>Average %{x:.2f}<br>%{customdata[0]:,} ratings<extra></extra>",
    )
    satisfaction_chart.update_yaxes(categoryorder="total ascending")
    satisfaction_chart.update_xaxes(range=[0, 5])
    st.plotly_chart(style_figure(satisfaction_chart, palette, height=570), width="stretch", config={"displayModeBar": False})

    st.subheader("3. How did ratings change across release years?")
    st.markdown(
        '<p class="method-note"><strong>How this is counted:</strong> Ratings are averaged by the movie\'s release year—not the year the viewer submitted the rating.</p>',
        unsafe_allow_html=True,
    )
    genre_options = sorted(genre_distribution(ratings)["genre"].tolist())
    selected_genres = st.multiselect(
        "Focus the timeline on genres",
        options=genre_options,
        default=[],
        placeholder="All genres",
        help="Selecting more than one genre uses OR matching; each rating is counted once.",
    )
    trend = release_year_trend(ratings, genres=selected_genres)
    if trend.empty:
        st.info("No release-year ratings match this genre selection.")
    else:
        trend_chart = px.line(
            trend,
            x="year",
            y="mean_rating",
            markers=True,
            custom_data=["rating_count"],
            labels={"year": "Movie release year", "mean_rating": "Average rating"},
            color_discrete_sequence=[palette["accent"]],
        )
        trend_chart.update_traces(
            line={"width": 2.5}, marker={"size": 6, "color": palette["background"], "line": {"color": palette["accent"], "width": 2}},
            hovertemplate="<b>%{x}</b><br>Average %{y:.2f}<br>%{customdata[0]:,} ratings<extra></extra>",
        )
        trend_chart.update_yaxes(range=[1, 5])
        st.plotly_chart(style_figure(trend_chart, palette, height=470), width="stretch", config={"displayModeBar": False})
    missing_years = int(ratings["year"].isna().sum())
    st.caption(f"{missing_years:,} rating records with no movie release year are excluded from this timeline.")

    st.subheader("4. Which movies rise above the rating floor?")
    st.markdown(
        '<p class="method-note"><strong>How this is counted:</strong> A movie qualifies when its rating count is greater than or equal to the selected floor. Ties favor more ratings, then title.</p>',
        unsafe_allow_html=True,
    )
    floor_label = st.segmented_control(
        "Minimum audience size",
        options=["50 ratings", "150 ratings"],
        default="50 ratings",
        selection_mode="single",
    )
    floor = 150 if floor_label == "150 ratings" else 50
    ranking = top_movies(ratings, min_ratings=floor)
    if ranking.empty:
        st.info(f"No movies have at least {floor:,} ratings.")
    else:
        ranking_chart = px.bar(
            ranking,
            x="mean_rating",
            y="title",
            orientation="h",
            text="mean_rating",
            custom_data=["rating_count"],
            labels={"mean_rating": "Average rating", "title": "Movie"},
            color_discrete_sequence=[palette["text"]],
        )
        ranking_chart.update_traces(
            texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False,
            hovertemplate="<b>%{y}</b><br>Average %{x:.3f}<br>%{customdata[0]:,} ratings<extra></extra>",
        )
        ranking_chart.update_yaxes(categoryorder="array", categoryarray=ranking["title"].tolist()[::-1])
        ranking_chart.update_xaxes(range=[0, 5])
        st.plotly_chart(style_figure(ranking_chart, palette, height=430), width="stretch", config={"displayModeBar": False})

    fifty_titles = set(top_movies(ratings, min_ratings=50)["title"])
    one_fifty_titles = set(top_movies(ratings, min_ratings=150)["title"])
    entered = sorted(one_fifty_titles - fifty_titles)
    dropped = sorted(fifty_titles - one_fifty_titles)
    if floor == 50:
        st.caption(
            "Raise the floor to 150 and "
            + ", ".join(dropped)
            + " leave the top five; "
            + ", ".join(entered)
            + " enter."
        )
    else:
        st.caption(
            "Compared with the 50-rating floor, "
            + ", ".join(entered)
            + " enter the top five while "
            + ", ".join(dropped)
            + " leave."
        )

    st.divider()
    st.caption("Source: GroupLens 100K dataset · 100,000 ratings from 943 viewers across 1,682 movies")


render_dashboard()
