import streamlit as sl
from streamlit_option_menu import option_menu

from components.metric import (
    fetch_data, clean_data,
    indicator, trip_duration,
    donut_chart, rider_prop,
    most_bikes, plot,
    trip_duration_users,
    trips_per_day, lineplot,
    daily_trip_duration, get_casual_route,
    casual_chart, get_member_route,
    get_reference
)


# ========= Page setup ======================
sl.set_page_config(page_title="Bikeshare Analytics", page_icon=":bar_chart:", layout="wide")

from components.css import css

# go to webfx.com/tools/emoji-cheat-sheet/ for emoji's

# ========= CSS ===============
sl.markdown(css, unsafe_allow_html=True)

sl.header("Divvy Bike-Share Analytic :bar_chart:")

with sl.sidebar:
    selected = option_menu(
        menu_title="Dashboard",
        options=["Trips", "Routes"],
        icons=["bicycle", "compass"],
        default_index=0,
        orientation="vertical",
    )
    "---"

if selected == "Trips":
    with sl.sidebar:
        years = [2022, 2023]

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December']

        quarters = ['Qtr 1', 'Qtr 2', 'Qtr 3', 'Qtr 4']

        checked = sl.checkbox("View Quarterly Report")

        year = sl.selectbox("Filter by Year", options=years, index=1)

        if checked:
            quarter = sl.selectbox("Filter by Quarter", options=quarters, index=0)
            quarter = quarter.lower()
        else:
            month = sl.selectbox("Filter by Month", options=months, index=0)


    if checked:
        filtered_data = clean_data(fetch_data(year, quarter=quarter))
    else:
        filtered_data = clean_data(fetch_data(year, month=month))


    left_col, right_col = sl.columns([1, 2])

    with right_col:
        total_trips, avg_duration = sl.columns(2)

        with total_trips:
            if checked:
                reference = get_reference(year, quarter=quarter.capitalize(), isTotTrip=True)
            else:
                reference = get_reference(year, month=month, isTotTrip=True)

            indicator(filtered_data.shape[0], "Total Trips", reference=reference)

        with avg_duration:
            indicator(0, 'Avg Duration', ":"+trip_duration(filtered_data))
        "---"

        # riders by bike type
        color_discrete_map = {
            'member':'#8BC7F7',
            'casual': '#D5EA67'
        }

        hover_data={
            'tot_trip': False,
            # 'count': False
        }

        labels={
            'count':'Total Trips',
            'member_casual':'Membership Type',
            'bike_type': 'Bike Type',
            # text: 'Total Trips'
        }

        plot(most_bikes(filtered_data, metric=1000), 'count', 'bike_type', title='Total trips by members per bike', orientation='v', color='member_casual', text='tot_trip', color_discrete_map=color_discrete_map, hover_data=hover_data, labels=labels, height=420, width=540)

    with left_col:
        donut_chart(rider_prop(filtered_data), "Proportion of Membership")

        # members by trip duration
        labels={
            'member_casual':'Membership Type',
            'bike_type': 'Bike Type',
            'trip_dur': 'Trip Duration'
        }

        hover_data={
            'trip_duration': False
        }

        plot(trip_duration_users(filtered_data), 'trip_duration', 'bike_type', title='Trip Duration by User type per Bike', color='member_casual', text='trip_dur', color_discrete_map=color_discrete_map, labels=labels, hover_data=hover_data, orientation='v', height=255, width=270)

if selected == "Routes":
    with sl.sidebar:
        years = [2022, 2023]

        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
        'August', 'September', 'October', 'November', 'December']

        quarters = ['Qtr 1', 'Qtr 2', 'Qtr 3', 'Qtr 4']

        checked = sl.checkbox("View Quarterly Report")

        year = sl.selectbox("Filter by Year", options=years, index=1)

        if checked:
            quarter = sl.selectbox("Filter by Quarter", options=quarters, index=0)
            quarter = quarter.lower()
        else:
            month = sl.selectbox("Filter by Month", options=months, index=0)


    if checked:
        filtered_data = clean_data(fetch_data(year, quarter=quarter))
    else:
        filtered_data = clean_data(fetch_data(year, month=month))


    left_col, right_col = sl.columns([1, 2])

    with right_col:

        # routes by casuals
        labels={
            'member_casual':'Membership Type',
            'bike_type': 'Bike Type',
            'trip_dur': 'Trip Duration'
        }

        hover_data={
            'trip_duration': False
        }

        colors = ['rgba(213,234,103,0.1)',]*5
        colors[4] = 'rgba(213,234,103,1)'
        colors[3] = 'rgba(213,234,103,0.5)'
        colors[2] = 'rgba(213,234,103,0.3)'
        colors[1] = 'rgba(213,234,103,0.2)'

        casual = get_casual_route(filtered_data)

        casual_routes = casual_chart(casual['count'], casual['route'], marker_color=colors, orientation='h', text=casual['count'], title='Top 5 Routes of Casual riders Number trips', height=350, width=540)

        # routes by members
        colors = ['rgba(139,199,247,0.1)',]*5
        colors[4] = 'rgba(139,199,247,1)'
        colors[3] = 'rgba(139,199,247,1)'
        colors[2] = 'rgba(139,199,247,0.4)'
        colors[1] = 'rgba(139,199,247,0.3)'

        member = get_member_route(filtered_data)

        member_routes = casual_chart(member['count'], member['route'], marker_color=colors, orientation='h', text=member['count'], title='Top 5 Routes of Annual Members Number trips', height=350, width=540)

    with left_col:
        lineplot(trips_per_day(filtered_data), 'week_day', 'count', 'Total trips per day per members', 'member_casual', height=350, width=270)

        # daily trip duration
        lineplot(daily_trip_duration(filtered_data), 'week_day', 'trip_duration', 'Avg. Trip duration per day', 'member_casual', text='trip_dur', duration='trip_duration', height=350, width=270)

        
