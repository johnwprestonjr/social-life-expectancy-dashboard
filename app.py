import pandas as pd
import streamlit as st
import altair as alt

alt.data_transformers.disable_max_rows()

st.set_page_config(
    page_title="Social Conditions & Life Expectancy Explorer",
    layout="wide"
)

@st.cache_data
def load_data():
    dashboard_df = pd.read_csv("dashboard_data.csv")
    race_df = pd.read_csv("race_life_expectancy_long.csv")
    return dashboard_df, race_df


dashboard_df, race_df = load_data()

st.title("Social Conditions & Life Expectancy Explorer")
st.caption(
    "An interactive dashboard exploring how social, economic, regional, and racial factors relate to health outcomes across U.S. counties."
)

# Sidebar filters
st.sidebar.header("Dashboard Filters")

regions = sorted(dashboard_df["Region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Select region(s)",
    options=regions,
    default=regions
)

states_available = sorted(
    dashboard_df.loc[dashboard_df["Region"].isin(selected_regions), "State"].dropna().unique()
)
selected_states = st.sidebar.multiselect(
    "Select state(s)",
    options=states_available,
    default=states_available
)

x_variable = st.sidebar.selectbox(
    "Choose a social determinant for the poor health chart",
    options=["% Some College", "% Uninsured"],
    index=0
)

show_trend = st.sidebar.checkbox("Show trend lines", value=True)
top_n = st.sidebar.slider("Top/Bottom counties to display", min_value=5, max_value=20, value=10, step=5)

filtered_df = dashboard_df[
    dashboard_df["Region"].isin(selected_regions) & dashboard_df["State"].isin(selected_states)
].copy()

filtered_race = race_df[
    race_df["Region"].isin(selected_regions) & race_df["State"].isin(selected_states)
].copy()

# KPI row
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Counties", f"{filtered_df['County'].nunique():,}")
kpi2.metric("Avg. Life Expectancy", f"{filtered_df['Life Expectancy'].mean():.1f} years")
kpi3.metric("Avg. Poor Health", f"{filtered_df['% Fair or Poor Health'].mean():.1f}%")
kpi4.metric("Avg. Food Insecurity", f"{filtered_df['% Food Insecure'].mean():.1f}%")

st.divider()

# Shared tooltip fields
tooltip_basic = [
    alt.Tooltip("County:N"),
    alt.Tooltip("State:N"),
    alt.Tooltip("Region:N"),
    alt.Tooltip("Life Expectancy:Q", format=".1f"),
    alt.Tooltip("% Fair or Poor Health:Q", format=".1f"),
    alt.Tooltip("% Children in Poverty:Q", format=".1f"),
    alt.Tooltip("% Food Insecure:Q", format=".1f"),
    alt.Tooltip("% Some College:Q", format=".1f"),
    alt.Tooltip("% Uninsured:Q", format=".1f"),
]

# Tab layout keeps the dashboard organized and avoids a top-to-bottom chart list.
tab1, tab2, tab3 = st.tabs([
    "Social Determinants",
    "State & Race Explorer",
    "County Extremes"
])

with tab1:
    st.subheader("Education, Insurance, Poverty, and Health Outcomes")
    left, right = st.columns(2)

    chart1_data = filtered_df.dropna(subset=[x_variable, "% Fair or Poor Health"])
    poor_health_scatter = alt.Chart(chart1_data).mark_circle(size=55, opacity=0.55).encode(
        x=alt.X(f"{x_variable}:Q", title=x_variable),
        y=alt.Y("% Fair or Poor Health:Q", title="Fair or Poor Health (%)"),
        color=alt.Color("Region:N", title="Region"),
        tooltip=tooltip_basic
    ).properties(
        title=f"{x_variable} vs Poor Health",
        height=390
    )

    if show_trend:
        poor_health_trend = poor_health_scatter.transform_regression(
            x_variable,
            "% Fair or Poor Health"
        ).mark_line()
        poor_health_scatter = poor_health_scatter + poor_health_trend

    with left:
        st.altair_chart(poor_health_scatter, use_container_width=True)
        st.caption(
            "UI interaction: the sidebar dropdown changes the x-axis between education and uninsured rates. Tooltips reveal county-level values."
        )

    chart3_data = filtered_df.dropna(subset=["% Children in Poverty", "Years of Potential Life Lost Rate"])
    poverty_brush = alt.selection_interval(name="PovertyBrush")

    poverty_scatter = alt.Chart(chart3_data).mark_circle(size=55, opacity=0.55).encode(
        x=alt.X("% Children in Poverty:Q", title="Children in Poverty (%)"),
        y=alt.Y("Years of Potential Life Lost Rate:Q", title="Premature Death Rate"),
        color=alt.condition(poverty_brush, "Region:N", alt.value("lightgray")),
        tooltip=tooltip_basic + [alt.Tooltip("Years of Potential Life Lost Rate:Q", format=".0f")]
    ).properties(
        title="Child Poverty vs Premature Death by Region",
        height=300
    ).add_params(poverty_brush)

    region_summary = alt.Chart(chart3_data).mark_bar().encode(
        x=alt.X("mean(Years of Potential Life Lost Rate):Q", title="Avg. Premature Death Rate"),
        y=alt.Y("Region:N", title="Region"),
        color=alt.Color("Region:N", legend=None),
        tooltip=[
            "Region:N",
            alt.Tooltip("mean(Years of Potential Life Lost Rate):Q", title="Avg. Premature Death", format=".0f")
        ]
    ).transform_filter(poverty_brush).properties(
        title="Selected Counties: Avg. Premature Death by Region",
        height=140
    )

    with right:
        st.altair_chart(poverty_scatter & region_summary, use_container_width=True)
        st.caption(
            "Within-visualization interaction: brush the scatterplot to update the regional summary chart below."
        )

with tab2:
    st.subheader("How Life Expectancy Varies by State and Racial Group")
    st.write(
        "Click on states in the map to update the racial group comparison below. This gives the dashboard a coordinated visualization feature."
    )

    # Data preparation for geochart
    state_fips = {
        "Alabama": 1, "Alaska": 2, "Arizona": 3, "Arkansas": 4, "California": 5,
        "Colorado": 6, "Connecticut": 7, "Delaware": 8, "District of Columbia": 9,
        "Florida": 10, "Georgia": 11, "Hawaii": 12, "Idaho": 13, "Illinois": 14,
        "Indiana": 15, "Iowa": 16, "Kansas": 17, "Kentucky": 18, "Louisiana": 19,
        "Maine": 20, "Maryland": 21, "Massachusetts": 22, "Michigan": 23,
        "Minnesota": 24, "Mississippi": 25, "Missouri": 26, "Montana": 27,
        "Nebraska": 28, "Nevada": 29, "New Hampshire": 30, "New Jersey": 31,
        "New Mexico": 32, "New York": 33, "North Carolina": 34, "North Dakota": 35,
        "Ohio": 36, "Oklahoma": 37, "Oregon": 38, "Pennsylvania": 39,
        "Rhode Island": 40, "South Carolina": 41, "South Dakota": 42,
        "Tennessee": 43, "Texas": 44, "Utah": 45, "Vermont": 46, "Virginia": 47,
        "Washington": 48, "West Virginia": 49, "Wisconsin": 50, "Wyoming": 51
    }

    geochart_data = filtered_race.dropna(subset=["Life Expectancy"]).copy()
    geochart_data["id"] = geochart_data["State"].map(state_fips)

    state_summary_for_geochart = (
        geochart_data
        .groupby(["State", "id"], as_index=False)["Life Expectancy"]
        .mean()
    )

    states_topo = alt.topo_feature(
        "https://cdn.jsdelivr.net/npm/us-atlas@3/states-10m.json",
        "states"
    )

    # Selection for the geochart
    state_selection = alt.selection_point(fields=['State'], name='state_selection', on='click')

    state_chart = alt.Chart(states_topo).mark_geoshape(
        stroke="white",
        strokeWidth=0.5
    ).encode(
        color=alt.Color(
            "Life Expectancy:Q",
            title="Avg. Life Expectancy",
            scale=alt.Scale(scheme="blues")
        ),
        tooltip=[
            alt.Tooltip("State:N", title="State"),
            alt.Tooltip("Life Expectancy:Q", title="Avg. Life Expectancy", format=".1f")
        ],
        # Add color condition for selection feedback
        strokeOpacity=alt.condition(state_selection, alt.value(1), alt.value(0.5)),
        strokeWidth=alt.condition(state_selection, alt.value(2), alt.value(0.5)),
    ).transform_lookup(
        lookup="id",
        from_=alt.LookupData(
            state_summary_for_geochart,
            key="id",
            fields=["State", "Life Expectancy"]
        )
    ).project(
        type="albersUsa"
    ).properties(
        title="Average Life Expectancy by State — Click to Select",
        height=400
    ).add_params(state_selection)

    # The race_chart uses filtered_race, which has 'State' column.
    race_chart_data_for_bar = filtered_race.dropna(subset=["Life Expectancy"])

    race_chart = alt.Chart(race_chart_data_for_bar).mark_bar().encode(
        x=alt.X("Race Group:N", title="Racial/Ethnic Group"),
        y=alt.Y("mean(Life Expectancy):Q", title="Average Life Expectancy"),
        color=alt.Color("Race Group:N", title="Race Group"),
        tooltip=[
            "Race Group:N",
            alt.Tooltip("mean(Life Expectancy):Q", title="Avg. Life Expectancy", format=".1f")
        ]
    ).transform_filter(
        state_selection
    ).properties(
        title="Average Life Expectancy by Race for Selected State(s)",
        height=300
    )

    st.altair_chart(state_chart & race_chart, use_container_width=True)
with tab3:
    st.subheader("Highest and Lowest Life Expectancy Counties")
    st.write(
        "This view compares counties with the highest and lowest life expectancy and shows how food insecurity differs across those counties."
    )

    county_data = filtered_df.dropna(subset=["Life Expectancy", "% Food Insecure"])
    top_counties = county_data.nlargest(top_n, "Life Expectancy")
    bottom_counties = county_data.nsmallest(top_n, "Life Expectancy")
    ranking = pd.concat([
        top_counties.assign(Life_Expectancy_Group="Highest"),
        bottom_counties.assign(Life_Expectancy_Group="Lowest")
    ])

    left, right = st.columns(2)

    county_scatter = alt.Chart(ranking).mark_circle(size=90, opacity=0.75).encode(
        x=alt.X("% Food Insecure:Q", title="Food Insecurity (%)"),
        y=alt.Y("Life Expectancy:Q", title="Life Expectancy (Years)"),
        color=alt.Color("Life_Expectancy_Group:N", title="Group"),
        tooltip=[
            "County:N", "State:N", "Region:N", "Life_Expectancy_Group:N",
            alt.Tooltip("Life Expectancy:Q", format=".1f"),
            alt.Tooltip("% Food Insecure:Q", format=".1f")
        ]
    ).properties(
        title="Food Insecurity vs Life Expectancy for Highest/Lowest Counties",
        height=420
    )

    ranked_bar = alt.Chart(ranking).mark_bar().encode(
        x=alt.X("Life Expectancy:Q", title="Life Expectancy (Years)", scale=alt.Scale(zero=False)),
        y=alt.Y("County:N", sort="-x", title="County"),
        color=alt.Color("Life_Expectancy_Group:N", title="Group"),
        tooltip=[
            "County:N", "State:N", "Region:N", "Life_Expectancy_Group:N",
            alt.Tooltip("Life Expectancy:Q", format=".1f"),
            alt.Tooltip("% Food Insecure:Q", format=".1f")
        ]
    ).properties(
        title="Ranked County Life Expectancy",
        height=420
    )

    with left:
        st.altair_chart(county_scatter, use_container_width=True)
    with right:
        st.altair_chart(ranked_bar, use_container_width=True)

st.divider()
st.caption(
    "Design note: the dashboard uses tabs, sidebar filters, and coordinated charts to support exploration without overwhelming users with a long vertical list of visuals."
)
