from pathlib import Path

import altair as alt
import pandas as pd
import streamlit as st

alt.data_transformers.disable_max_rows()

# -----------------------------------------------------------------------------
# Page setup and visual theme
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Social Conditions & Life Expectancy Explorer",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PURPLE = "#5B3F8C"
PURPLE_2 = "#7A5BB5"
LAVENDER = "#B8A8E3"
PALE_LAVENDER = "#F4F0FA"
DEEP_TEXT = "#2F234A"
MUTED_TEXT = "#6D6280"
SAGE = "#7FA97A"
ROSE = "#C06C84"
LIGHT_GRAY = "#D9D5E2"

st.markdown(
    f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, {PALE_LAVENDER} 0%, #FFFFFF 28%, #FFFFFF 100%);
            color: {DEEP_TEXT};
        }}
        [data-testid="stHeader"] {{
            background: rgba(244, 240, 250, 0.88);
        }}
        [data-testid="stMetric"] {{
            background: #FFFFFF;
            border: 1px solid #DED6EF;
            border-radius: 14px;
            padding: 14px 16px;
            box-shadow: 0 2px 10px rgba(67, 43, 105, 0.06);
        }}
        [data-testid="stMetricLabel"] {{
            color: {MUTED_TEXT};
        }}
        [data-testid="stMetricValue"] {{
            color: {PURPLE};
        }}
        .hero-title {{
            color: {PURPLE};
            font-size: clamp(2rem, 4vw, 3.5rem);
            line-height: 1.05;
            font-weight: 750;
            margin: 0 0 .5rem 0;
        }}
        .hero-subtitle {{
            color: {MUTED_TEXT};
            font-size: 1.08rem;
            line-height: 1.55;
            margin-bottom: 1rem;
            max-width: 820px;
        }}
        .purple-callout {{
            background: #EEE8F8;
            border-left: 6px solid {PURPLE};
            border-radius: 12px;
            padding: 14px 18px;
            margin: 8px 0 18px 0;
            color: {DEEP_TEXT};
        }}
        .section-kicker {{
            color: {PURPLE_2};
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: .08em;
            font-size: .78rem;
            margin-bottom: .2rem;
        }}
        .section-title {{
            color: {DEEP_TEXT};
            font-size: 1.7rem;
            font-weight: 720;
            margin-bottom: .25rem;
        }}
        .section-copy {{
            color: {MUTED_TEXT};
            margin-bottom: 1rem;
        }}
        .small-note {{
            color: {MUTED_TEXT};
            font-size: .9rem;
        }}
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        .stTabs [data-baseweb="tab"] {{
            background: #EEE8F8;
            color: {DEEP_TEXT};
            border-radius: 10px 10px 0 0;
            padding: 10px 18px;
        }}
        .stTabs [aria-selected="true"] {{
            background: {PURPLE} !important;
            color: #FFFFFF !important;
        }}
        div[data-testid="stExpander"] {{
            border: 1px solid #DED6EF;
            border-radius: 12px;
            background: #FBFAFD;
        }}
        .stButton > button {{
            border-color: {PURPLE};
            color: {PURPLE};
        }}
        footer {{visibility: hidden;}}
    </style>
    """,
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    dashboard = pd.read_csv("dashboard_data.csv")
    race = pd.read_csv("race_life_expectancy_long.csv")

    for frame in (dashboard, race):
        if "Region" in frame.columns:
            frame["Region"] = frame["Region"].replace(
                {"undefined": pd.NA, "Undefined": pd.NA, "": pd.NA}
            )

    numeric_dashboard_cols = [
        "Life Expectancy",
        "Years of Potential Life Lost Rate",
        "% Children in Poverty",
        "% Food Insecure",
        "% Some College",
        "% Fair or Poor Health",
        "% Uninsured",
    ]
    for col in numeric_dashboard_cols:
        if col in dashboard.columns:
            dashboard[col] = pd.to_numeric(dashboard[col], errors="coerce")

    if "Life Expectancy" in race.columns:
        race["Life Expectancy"] = pd.to_numeric(race["Life Expectancy"], errors="coerce")

    return dashboard, race


dashboard_df, race_df = load_data()

# -----------------------------------------------------------------------------
# Hero / homepage
# -----------------------------------------------------------------------------
hero_col, text_col = st.columns([1.0, 1.45], gap="large")

with hero_col:
    image_candidates = [
        Path("community_hero.jpg"),
        Path("assets/community_hero.jpg"),
    ]
    hero_path = next((path for path in image_candidates if path.exists()), None)
    if hero_path:
        st.image(str(hero_path), use_container_width=True)
    else:
        st.markdown(
            f"""
            <div style="background:#E9E1F5;border:1px dashed {LAVENDER};border-radius:18px;
                        min-height:260px;display:flex;align-items:center;justify-content:center;
                        color:{MUTED_TEXT};padding:24px;text-align:center;">
                Add <b>community_hero.jpg</b> to the repository to display the homepage illustration.
            </div>
            """,
            unsafe_allow_html=True,
        )

with text_col:
    st.markdown('<div class="section-kicker">Interactive county health dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-title">Social Conditions &amp; Life Expectancy Explorer</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="hero-subtitle">
            Explore how education, poverty, food insecurity, insurance coverage, geography,
            and race relate to health outcomes across U.S. counties.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="purple-callout">
            <b>Start here:</b> Use the State &amp; Race Explorer to view the national pattern.
            Hover for details, click a state to compare racial groups, and then move into the
            social and county-level explanations.
        </div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# Meaningful default findings
# -----------------------------------------------------------------------------
valid_life = dashboard_df.dropna(subset=["Life Expectancy", "County", "State"]).copy()
valid_premature = dashboard_df.dropna(
    subset=["Years of Potential Life Lost Rate", "Region"]
).copy()

if not valid_life.empty:
    highest_county = valid_life.loc[valid_life["Life Expectancy"].idxmax()]
    lowest_county = valid_life.loc[valid_life["Life Expectancy"].idxmin()]
else:
    highest_county = lowest_county = None

region_premature = (
    valid_premature.groupby("Region")["Years of Potential Life Lost Rate"]
    .mean()
    .sort_values(ascending=False)
)
highest_premature_region = region_premature.index[0] if not region_premature.empty else "N/A"

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Counties", f"{dashboard_df['County'].nunique():,}")
kpi2.metric(
    "Highest life expectancy",
    f"{highest_county['Life Expectancy']:.1f} years" if highest_county is not None else "N/A",
    f"{highest_county['County']}, {highest_county['State']}" if highest_county is not None else None,
)
kpi3.metric(
    "Lowest life expectancy",
    f"{lowest_county['Life Expectancy']:.1f} years" if lowest_county is not None else "N/A",
    f"{lowest_county['County']}, {lowest_county['State']}" if lowest_county is not None else None,
)
kpi4.metric("Highest avg. premature death", highest_premature_region)

st.divider()

# Shared Altair configuration and tooltips
region_scale = alt.Scale(
    domain=["Northeast", "Midwest", "South", "West"],
    range=[PURPLE, PURPLE_2, LAVENDER, SAGE],
)

tooltip_basic = [
    alt.Tooltip("County:N", title="County"),
    alt.Tooltip("State:N", title="State"),
    alt.Tooltip("Region:N", title="Region"),
    alt.Tooltip("Life Expectancy:Q", title="Life Expectancy", format=".1f"),
    alt.Tooltip("% Fair or Poor Health:Q", title="Fair/Poor Health", format=".1f"),
    alt.Tooltip("% Children in Poverty:Q", title="Children in Poverty", format=".1f"),
    alt.Tooltip("% Food Insecure:Q", title="Food Insecure", format=".1f"),
    alt.Tooltip("% Some College:Q", title="Some College", format=".1f"),
    alt.Tooltip("% Uninsured:Q", title="Uninsured", format=".1f"),
]

# Revised story order: overview -> explanation -> county detail
state_tab, social_tab, county_tab, about_tab = st.tabs(
    [
        "State & Race Explorer",
        "Social Determinants",
        "County Extremes",
        "About",
    ]
)

# -----------------------------------------------------------------------------
# TAB 1: State & Race Explorer
# -----------------------------------------------------------------------------
with state_tab:
    st.markdown('<div class="section-kicker">National overview</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Where does life expectancy differ by state and racial group?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">Select the geographic area first, then click a state on the map to update the linked racial-group comparison.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Filters for this section", expanded=True):
        c1, c2 = st.columns(2)
        race_regions = sorted(race_df["Region"].dropna().unique())
        selected_race_regions = c1.multiselect(
            "Region(s)", race_regions, default=race_regions, key="race_regions"
        )
        race_states_available = sorted(
            race_df.loc[race_df["Region"].isin(selected_race_regions), "State"]
            .dropna()
            .unique()
        )
        selected_race_states = c2.multiselect(
            "State(s)", race_states_available, default=race_states_available, key="race_states"
        )

    filtered_race = race_df[
        race_df["Region"].isin(selected_race_regions)
        & race_df["State"].isin(selected_race_states)
    ].copy()

    st.markdown(
        """
        <div class="purple-callout">
            <b>How to interact:</b> Hover over a state for its average life expectancy. Click a state
            to highlight it and update the racial-group chart below. Click another state to change the selection.
        </div>
        """,
        unsafe_allow_html=True,
    )

    state_fips = {
        "Alabama": "01", "Alaska": "02", "Arizona": "04", "Arkansas": "05",
        "California": "06", "Colorado": "08", "Connecticut": "09",
        "Delaware": "10", "District of Columbia": "11", "Florida": "12",
        "Georgia": "13", "Hawaii": "15", "Idaho": "16", "Illinois": "17",
        "Indiana": "18", "Iowa": "19", "Kansas": "20", "Kentucky": "21",
        "Louisiana": "22", "Maine": "23", "Maryland": "24",
        "Massachusetts": "25", "Michigan": "26", "Minnesota": "27",
        "Mississippi": "28", "Missouri": "29", "Montana": "30",
        "Nebraska": "31", "Nevada": "32", "New Hampshire": "33",
        "New Jersey": "34", "New Mexico": "35", "New York": "36",
        "North Carolina": "37", "North Dakota": "38", "Ohio": "39",
        "Oklahoma": "40", "Oregon": "41", "Pennsylvania": "42",
        "Rhode Island": "44", "South Carolina": "45", "South Dakota": "46",
        "Tennessee": "47", "Texas": "48", "Utah": "49", "Vermont": "50",
        "Virginia": "51", "Washington": "53", "West Virginia": "54",
        "Wisconsin": "55", "Wyoming": "56",
    }

    geo = filtered_race.dropna(subset=["Life Expectancy", "State"]).copy()
    geo["id"] = geo["State"].map(state_fips)
    state_summary = geo.groupby(["State", "id"], as_index=False)["Life Expectancy"].mean()

    states_topo = alt.topo_feature(
        "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json", "states"
    )
    state_selection = alt.selection_point(
        fields=["State"], name="state_selection", on="click", empty="all"
    )

    state_chart = (
        alt.Chart(states_topo)
        .mark_geoshape(stroke="white", strokeWidth=0.7)
        .encode(
            color=alt.Color(
                "Life Expectancy:Q",
                title="Avg. life expectancy",
                scale=alt.Scale(scheme="purples"),
            ),
            tooltip=[
                alt.Tooltip("State:N", title="State"),
                alt.Tooltip("Life Expectancy:Q", title="Average", format=".1f"),
            ],
            strokeOpacity=alt.condition(state_selection, alt.value(1), alt.value(0.45)),
            strokeWidth=alt.condition(state_selection, alt.value(2.8), alt.value(0.7)),
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(state_summary, key="id", fields=["State", "Life Expectancy"]),
        )
        .project(type="albersUsa")
        .properties(title="Average Life Expectancy by State — Click to Select", height=410)
        .add_params(state_selection)
    )

    race_chart = (
        alt.Chart(filtered_race.dropna(subset=["Life Expectancy"]))
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("Race Group:N", title="Racial/Ethnic Group", sort="-y"),
            y=alt.Y(
                "mean(Life Expectancy):Q",
                title="Average Life Expectancy",
                scale=alt.Scale(zero=False),
            ),
            color=alt.Color("Race Group:N", title="Race Group", scale=alt.Scale(scheme="purples")),
            tooltip=[
                alt.Tooltip("Race Group:N", title="Race Group"),
                alt.Tooltip("mean(Life Expectancy):Q", title="Average", format=".1f"),
            ],
        )
        .transform_filter(state_selection)
        .properties(title="Life Expectancy by Race for Selected State(s)", height=290)
    )

    st.altair_chart((state_chart & race_chart).configure_view(stroke=None), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 2: Social Determinants
# -----------------------------------------------------------------------------
with social_tab:
    st.markdown('<div class="section-kicker">Possible explanations</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">How do education, insurance, and poverty relate to health?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">Use the controls beside these charts to focus the analysis without changing unrelated sections.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Filters for this section", expanded=True):
        c1, c2, c3 = st.columns([2, 2, 1.2])
        social_regions = sorted(dashboard_df["Region"].dropna().unique())
        selected_social_regions = c1.multiselect(
            "Region(s)", social_regions, default=social_regions, key="social_regions"
        )
        social_states_available = sorted(
            dashboard_df.loc[
                dashboard_df["Region"].isin(selected_social_regions), "State"
            ].dropna().unique()
        )
        selected_social_states = c2.multiselect(
            "State(s)", social_states_available, default=social_states_available, key="social_states"
        )
        x_variable = c3.selectbox(
            "Poor-health predictor", ["% Some College", "% Uninsured"], key="social_x"
        )
        show_trend = c3.checkbox("Show trend line", value=True, key="social_trend")

    filtered_social = dashboard_df[
        dashboard_df["Region"].isin(selected_social_regions)
        & dashboard_df["State"].isin(selected_social_states)
    ].copy()

    left, right = st.columns(2, gap="large")

    chart1_data = filtered_social.dropna(subset=[x_variable, "% Fair or Poor Health"])
    poor_scatter = (
        alt.Chart(chart1_data)
        .mark_circle(size=62, opacity=0.58)
        .encode(
            x=alt.X(f"{x_variable}:Q", title=x_variable),
            y=alt.Y("% Fair or Poor Health:Q", title="Fair or Poor Health (%)"),
            color=alt.Color("Region:N", title="Region", scale=region_scale),
            tooltip=tooltip_basic,
        )
        .properties(title=f"{x_variable} vs Poor Health", height=390)
    )
    if show_trend:
        trend = (
            alt.Chart(chart1_data)
            .transform_regression(x_variable, "% Fair or Poor Health")
            .mark_line(color=PURPLE, strokeWidth=3)
            .encode(x=f"{x_variable}:Q", y="% Fair or Poor Health:Q")
        )
        poor_scatter = poor_scatter + trend

    with left:
        st.altair_chart(poor_scatter.configure_view(stroke=None), use_container_width=True)
        st.caption("Switch between education and uninsured rates. Hover for county-level details.")

    chart3_data = filtered_social.dropna(
        subset=["% Children in Poverty", "Years of Potential Life Lost Rate", "Region"]
    )
    poverty_brush = alt.selection_interval(name="PovertyBrush")

    poverty_scatter = (
        alt.Chart(chart3_data)
        .mark_circle(size=62, opacity=0.62)
        .encode(
            x=alt.X("% Children in Poverty:Q", title="Children in Poverty (%)"),
            y=alt.Y("Years of Potential Life Lost Rate:Q", title="Premature Death Rate"),
            color=alt.condition(
                poverty_brush,
                alt.Color("Region:N", title="Region", scale=region_scale),
                alt.value(LIGHT_GRAY),
            ),
            tooltip=tooltip_basic
            + [alt.Tooltip("Years of Potential Life Lost Rate:Q", title="Premature Death", format=".0f")],
        )
        .properties(title="Child Poverty vs Premature Death", height=285)
        .add_params(poverty_brush)
    )

    region_summary = (
        alt.Chart(chart3_data)
        .mark_bar(cornerRadiusEnd=4)
        .encode(
            x=alt.X("mean(Years of Potential Life Lost Rate):Q", title="Average Premature Death Rate"),
            y=alt.Y("Region:N", title=None),
            color=alt.Color("Region:N", legend=None, scale=region_scale),
            tooltip=[
                alt.Tooltip("Region:N", title="Region"),
                alt.Tooltip(
                    "mean(Years of Potential Life Lost Rate):Q",
                    title="Average Premature Death",
                    format=".0f",
                ),
            ],
        )
        .transform_filter(poverty_brush)
        .properties(title="Selected Counties by Region", height=140)
    )

    with right:
        st.markdown(
            """
            <div class="purple-callout">
                <b>Brush interaction:</b> Drag a box over points in the scatterplot. The bar chart
                will recalculate using only the selected counties.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.altair_chart((poverty_scatter & region_summary).configure_view(stroke=None), use_container_width=True)

# -----------------------------------------------------------------------------
# TAB 3: County Extremes
# -----------------------------------------------------------------------------
with county_tab:
    st.markdown('<div class="section-kicker">From overview to detail</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-title">Which counties stand out, and how does food insecurity compare?</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-copy">The section now identifies the counties first, then explains their contrast through food insecurity.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Filters for this section", expanded=True):
        c1, c2, c3 = st.columns([2, 2, 1])
        county_regions = sorted(dashboard_df["Region"].dropna().unique())
        selected_county_regions = c1.multiselect(
            "Region(s)", county_regions, default=county_regions, key="county_regions"
        )
        county_states_available = sorted(
            dashboard_df.loc[
                dashboard_df["Region"].isin(selected_county_regions), "State"
            ].dropna().unique()
        )
        selected_county_states = c2.multiselect(
            "State(s)", county_states_available, default=county_states_available, key="county_states"
        )
        top_n = c3.slider("Top/bottom counties", 5, 20, 10, 5, key="county_top_n")

    filtered_county = dashboard_df[
        dashboard_df["Region"].isin(selected_county_regions)
        & dashboard_df["State"].isin(selected_county_states)
    ].copy()
    county_data = filtered_county.dropna(subset=["Life Expectancy", "% Food Insecure"])

    if county_data.empty:
        st.warning("No counties match the selected filters. Expand the region or state selection.")
    else:
        top = county_data.nlargest(top_n, "Life Expectancy")
        bottom = county_data.nsmallest(top_n, "Life Expectancy")
        ranking = pd.concat(
            [
                top.assign(Life_Expectancy_Group="Highest"),
                bottom.assign(Life_Expectancy_Group="Lowest"),
            ]
        )
        group_scale = alt.Scale(
            domain=["Highest", "Lowest"], range=[PURPLE, ROSE]
        )

        st.markdown("#### 1. Identify the highest- and lowest-life-expectancy counties")
        ranked_bar = (
            alt.Chart(ranking)
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                x=alt.X(
                    "Life Expectancy:Q",
                    title="Life Expectancy (Years)",
                    scale=alt.Scale(zero=False),
                ),
                y=alt.Y("County:N", sort="-x", title="County"),
                color=alt.Color(
                    "Life_Expectancy_Group:N", title="Group", scale=group_scale
                ),
                tooltip=[
                    alt.Tooltip("County:N", title="County"),
                    alt.Tooltip("State:N", title="State"),
                    alt.Tooltip("Region:N", title="Region"),
                    alt.Tooltip("Life_Expectancy_Group:N", title="Group"),
                    alt.Tooltip("Life Expectancy:Q", title="Life Expectancy", format=".1f"),
                    alt.Tooltip("% Food Insecure:Q", title="Food Insecure", format=".1f"),
                ],
            )
            .properties(title="Ranked County Life Expectancy", height=470)
        )
        st.altair_chart(ranked_bar.configure_view(stroke=None), use_container_width=True)

        st.markdown("#### 2. Compare food insecurity between those groups")
        county_scatter = (
            alt.Chart(ranking)
            .mark_circle(size=105, opacity=0.82)
            .encode(
                x=alt.X("% Food Insecure:Q", title="Food Insecurity (%)"),
                y=alt.Y(
                    "Life Expectancy:Q",
                    title="Life Expectancy (Years)",
                    scale=alt.Scale(zero=False),
                ),
                color=alt.Color(
                    "Life_Expectancy_Group:N", title="Group", scale=group_scale
                ),
                tooltip=[
                    alt.Tooltip("County:N", title="County"),
                    alt.Tooltip("State:N", title="State"),
                    alt.Tooltip("Region:N", title="Region"),
                    alt.Tooltip("Life_Expectancy_Group:N", title="Group"),
                    alt.Tooltip("Life Expectancy:Q", title="Life Expectancy", format=".1f"),
                    alt.Tooltip("% Food Insecure:Q", title="Food Insecure", format=".1f"),
                ],
            )
            .properties(title="Food Insecurity vs Life Expectancy", height=410)
        )
        st.altair_chart(county_scatter.configure_view(stroke=None), use_container_width=True)
        st.caption(
            "Displaying only the selected highest and lowest counties reduces clutter. Very narrow filters can create a small comparison group."
        )

# -----------------------------------------------------------------------------
# TAB 4: About / limitations
# -----------------------------------------------------------------------------
with about_tab:
    st.markdown('<div class="section-kicker">Project context</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">About this dashboard</div>', unsafe_allow_html=True)
    a, b = st.columns(2, gap="large")
    with a:
        st.markdown("#### What users can do")
        st.markdown(
            """
            - Filter by region and state within each section.
            - Hover over charts for detailed county values.
            - Click a state to update a linked racial-group chart.
            - Brush counties to update a coordinated regional summary.
            - Compare the highest and lowest life-expectancy counties.
            """
        )
    with b:
        st.markdown("#### Design trade-offs and limitations")
        st.markdown(
            """
            - County-level relationships do not establish causation or represent every individual.
            - Race-specific estimates contain missing values in some counties.
            - Filters are placed near the charts they control, which improves clarity but repeats some controls.
            - The top/bottom view intentionally limits the number of counties to reduce clutter.
            - Brushing is most useful when users select a focused subset of points.
            """
        )

st.divider()
st.markdown(
    f'<div class="small-note">Built with Streamlit, Pandas, and Altair.</div>',
    unsafe_allow_html=True,
)
