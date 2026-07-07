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
        "Brush across states in the top chart to update the racial group comparison below. This gives the dashboard a coordinated visualization feature."
    )

    race_chart_data = filtered_race.dropna(subset=["Life Expectancy"])
    state_brush = alt.selection_interval(encodings=["x"], name="StateBrush")

    state_chart = alt.Chart(race_chart_data).mark_bar().encode(
        x=alt.X("State:N", sort="-y", title="State"),
        y=alt.Y("mean(Life Expectancy):Q", title="Average Life Expectancy"),
        color=alt.condition(state_brush, alt.value("steelblue"), alt.value("lightgray")),
        tooltip=[
            "State:N",
            alt.Tooltip("mean(Life Expectancy):Q", title="Avg. Life Expectancy", format=".1f")
        ]
    ).properties(
        title="Average Life Expectancy by State — Brush to Select",
        height=260
    ).add_params(state_brush)

    race_chart = alt.Chart(race_chart_data).mark_bar().encode(
        x=alt.X("Race Group:N", title="Racial/Ethnic Group"),
        y=alt.Y("mean(Life Expectancy):Q", title="Average Life Expectancy"),
        color=alt.Color("Race Group:N", title="Race Group"),
        tooltip=[
            "Race Group:N",
            alt.Tooltip("mean(Life Expectancy):Q", title="Avg. Life Expectancy", format=".1f")
        ]
    ).transform_filter(state_brush).properties(
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
