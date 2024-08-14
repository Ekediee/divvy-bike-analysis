from datetime import timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as sl

import pandas as pd
import sqlite3 as db

# conn = sl.experimental_connection("divvydb", type="sql")
# conns = sl.experimental_connection("divvydb22", type="sql")

@sl.cache_data
def fetch_data(year, month=None, prev_month=None, quarter=None, prev_quarter=None):
    con = db.connect("divvy.sqlite")
    
    if quarter is None:
        if prev_month is None:
            if(year == 2022):
                
                data = pd.read_sql_query(f"select * from divvy_bike22 where month = '{month}'", con)
                
                return data
            elif(year == 2023):
                # data = conn.query(f"select * from divvy_bike_share where month = '{month}'", ttl=timedelta(minutes=30))
                
                data = pd.read_sql_query(f"select * from divvy_bike23 where month = '{month}'", con)

                return data
        else:
            if(year == 2022):
                
                data = pd.read_sql_query(f"select * from divvy_bike22 where month_num = '{prev_month}'", con)
                
                return data
            elif(year == 2023):
                # data = conn.query(f"select * from divvy_bike_share where month = '{month}'", ttl=timedelta(minutes=30))
                
                data = pd.read_sql_query(f"select * from divvy_bike23 where month_num = '{prev_month}'", con)

                return data
    else:
        if prev_quarter is None:
            if(year == 2022):
                
                data = pd.read_sql_query(f"select * from divvy_bike22 where quarter = '{quarter}'", con)
                
                return data
            elif(year == 2023):
                # data = conn.query(f"select * from divvy_bike_share where month = '{month}'", ttl=timedelta(minutes=30))
                
                data = pd.read_sql_query(f"select * from divvy_bike23 where quarter = '{quarter}'", con)

                return data
        else:
            if(year == 2022):
                
                data = pd.read_sql_query(f"select * from divvy_bike22 where quarter = '{prev_quarter}'", con)
                
                return data
            elif(year == 2023):
                # data = conn.query(f"select * from divvy_bike_share where month = '{month}'", ttl=timedelta(minutes=30))
                
                data = pd.read_sql_query(f"select * from divvy_bike23 where quarter = '{prev_quarter}'", con)

                return data
            

def clean_data(df):

    # Remove records with missing route information
    trip_data = df.dropna(subset=["start_station_id", "end_station_id", "end_lat", "end_lng"])
    trip_data = trip_data.rename(columns={"ride_id": "trip_id", "rideable_type": "bike_type"})
    # print(trip_data)
    trip_data["started_at"] = pd.to_datetime(trip_data["started_at"])

    trip_data["ended_at"] = pd.to_datetime(trip_data["ended_at"])
    trip_data['trip_duration'] = round((trip_data["ended_at"] - trip_data["started_at"]).dt.total_seconds()/60,1)

    trip_data['quarter'] = trip_data['quarter'].str.capitalize()
    trip_data['quarter_num'] = trip_data['quarter'].str.split(" ").str[1]
    trip_data['week_day'] = trip_data["started_at"].dt.strftime('%a')
    trip_data['day_num'] = trip_data['started_at'].dt.dayofweek
    trip_data['day_num'] = trip_data['day_num'].replace([6,0,1,2,3,4,5],[1,2,3,4,5,6,7])

    trip_data['route'] = trip_data['start_station_name']+'_to_'+trip_data['end_station_name']

    return trip_data


@sl.cache_data
def indicator(value, title, suffix=None, reference=None):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value=value,
            number={
                "font.size": 30,
                "font.color": "black",
                # "prefix":"$", 
                "suffix":suffix
            },
            title={
                "text": title,
                "font": {"size": 15, 'color':'black'},
            },
        )
    )

    # fig.update_xaxes(visible=False, fixedrange=True)
    # fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        height=100,
        # width=250,
        paper_bgcolor='white',
        plot_bgcolor='white',
        template={
            "data": {
                "indicator": [
                    {
                        "mode": "number+delta",
                        "delta": {"reference": reference},
                    }
                ]
            }
        },
    )

    sl.plotly_chart(fig, use_container_width=True)

@sl.cache_data
def trip_duration(dataset):
    
    trip_duration = str(int(round(dataset['trip_duration'].mean(),2)//1))+':'+str(int(round((round(dataset['trip_duration'].mean(),2)%1)*60,1)))

    return trip_duration

@sl.cache_data
def donut_chart(df, title):
    fig = px.pie(
        df, values='count', 
        names='member_casual',
        hole=0.5,
        color='member_casual',
        labels={'count':'Total Trips',
                'member_casual':'Membership Type'},
        color_discrete_map={
            'member':'#8BC7F7',
            'casual': '#D5EA67'
        }
    )
    fig.update_traces(textposition='outside', textinfo='percent')
    fig.update_layout(
        legend=dict(orientation="v", yanchor="top", xanchor="right", y=2, x=0.95),
        height=300,
        # width=300,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=True,
        title=title,
        title_x=0.1,
    )
    sl.plotly_chart(fig, use_container_width=True)

@sl.cache_data
def rider_prop(df):
    riders = df.groupby('member_casual', as_index=False)["member_casual"].value_counts()

    return riders

@sl.cache_data
def most_bikes(df, metric=None):
    
    member_by_bike = df.groupby(['member_casual','bike_type'], as_index=False)["member_casual"].value_counts()
    
    if metric:
        member_by_bike['tot_trip'] = member_by_bike['count'].apply(lambda x: '{0:1.2f}k'.format(x/metric))
    else:
        member_by_bike['tot_trip'] = member_by_bike['count']

    member_by_bike = member_by_bike.sort_values(by='count')

    return member_by_bike

@sl.cache_data
def trip_duration_users(df):
    
    member_by_dur = df.groupby(['member_casual','bike_type'], as_index=False)["trip_duration"].mean()

    member_by_dur = member_by_dur.sort_values(by='trip_duration')
    member_by_dur['trip_dur'] = (member_by_dur['trip_duration']//1).astype(int).astype(str)+':'+(round((member_by_dur['trip_duration']%1)*60,1)//1).astype(int).astype(str)

    return member_by_dur

@sl.cache_data
def plot(df, x, y, orientation=None, title=None, color=None, text=None, labels=None, color_discrete_map=None, hover_data=None, hover_name=None, height=None):
    
    fig = px.bar(
        df,
        x=y,
        y=x,
        orientation=orientation,
        title=title,
        color=color,
        text=text,
        barmode='group',
        labels=labels,
        color_discrete_map=color_discrete_map,
        hover_data=hover_data,
        hover_name=hover_name
        
    )
    
    fig.update_xaxes(visible=True, title="", fixedrange=True)
    fig.update_yaxes(visible=True, title="", fixedrange=True, showticklabels=True)
    fig.update_layout(
        # title=title,
        showlegend=False,
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=height,
        # width=450,
    )

    sl.plotly_chart(fig, use_container_width=True)

@sl.cache_data
def trips_per_day(df):
    member_by_trip = df.groupby(['member_casual','week_day','day_num'], as_index=False)["member_casual"].value_counts()

    member_by_trip = member_by_trip.sort_values(by=['member_casual','day_num'])

    return member_by_trip

@sl.cache_data
def lineplot(df, x, y, title, color=None, text=None, line=True, duration=None, height=None):

    if line:
        fig = px.line(
            df,
            x=x,
            y=y,
            title=title,
            color=color,
            # text=text,
            category_orders={'week_day': ['Sunday','Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']},
            color_discrete_map={
                'member':'#8BC7F7',
                'casual': '#D5EA67'
            },
            labels={'count':'Total Trips',
                'member_casual':'Membership Type',
                'week_day': 'Week Day',
                text: 'Trip Duration'
            },
            hover_data={text: True,
                duration: False  
            }
        )
        fig.update_traces(textposition="top center", fill="tozeroy")
    else: 
        fig = px.bar(
            df,
            x=x,
            y=y,
            orientation="h",
            title=title,
            color=color,
            text=x,
            barmode='group',
            
        )
    
    fig.update_xaxes(visible=True, title="", fixedrange=True)
    fig.update_yaxes(visible=True, title="", fixedrange=True, showticklabels=True)
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=height,
        title=title,
        showlegend=False,
        # height=350,
        # width=450,
    )

    sl.plotly_chart(fig, use_container_width=True)

@sl.cache_data
def daily_trip_duration(df):
    member_by_duration = df.groupby(['member_casual','week_day','day_num'], as_index=False)["trip_duration"].mean()

    member_by_duration = member_by_duration.sort_values(by=['member_casual','day_num'])

    member_by_duration['trip_dur'] = (member_by_duration['trip_duration']//1).astype(int).astype(str)+':'+(round((member_by_duration['trip_duration']%1)*60,1)//1).astype(int).astype(str)

    return member_by_duration

@sl.cache_data
def get_casual_route(df):
    casual = df.loc[df['member_casual'] == 'casual',]

    casual = casual.groupby('route', as_index=False)['route'].value_counts()
    casual = casual.sort_values(by='count', ascending=False)
    casual = casual.head()

    casual = casual.sort_values(by='count')

    return  casual

@sl.cache_data
def get_member_route(df):
    member = df.loc[df['member_casual'] == 'member',]

    member = member.groupby('route', as_index=False)['route'].value_counts()
    member = member.sort_values(by='count', ascending=False)
    member = member.head()

    member = member.sort_values(by='count')

    return  member

@sl.cache_data
def casual_chart(x, y, marker_color=None, orientation=None, text=None, title=None, height=None):
    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=x,
            y=y,
            marker_color=marker_color,
            orientation=orientation,
            text=text
            # text=text.apply(lambda x: '{0:1.1f}k'.format(x/1000))

        )
    )
    fig.update_layout(
        title_text=title,
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=height,
        # width=450,
    )
    sl.plotly_chart(fig, use_container_width=True)

def get_reference(year, month=None, quarter=None, isTotTrip=False):
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
       'August', 'September', 'October', 'November', 'December']
    
    quarters = ['Qtr 1', 'Qtr 2', 'Qtr 3', 'Qtr 4']
    
    if quarter:
        quarter_nums = {i:quarters.index(i)+1 for i in quarters}
        selected_quarter_num = quarter_nums[quarter]
        # print(selected_quarter_num)

        if selected_quarter_num > 1:
            previous_quarter = "qtr "+str(selected_quarter_num-1)
            previous_quarter_data = clean_data(fetch_data(year, quarter=quarter.lower(), prev_quarter=previous_quarter))
            
            if isTotTrip:
                
                return previous_quarter_data.shape[0]
            else:
                return previous_quarter_data['trip_duration'].mean()
        else:
            refs = None
            return refs
    else:
        month_nums = {i:months.index(i)+1 for i in months}
        selected_month_num = month_nums[month]


        if selected_month_num > 1:
            previous_month_data = clean_data(fetch_data(year, prev_month=selected_month_num-1))
            if isTotTrip:
                
                return previous_month_data.shape[0]
            else:
                return previous_month_data['trip_duration'].mean()
        else:
            refs = None
            return refs