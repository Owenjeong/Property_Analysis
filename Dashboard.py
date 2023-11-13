import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
import numpy as np
import pydeck as pdk
import requests
from io import StringIO


st.set_page_config(page_title="Property Analysis",
                  page_icon=None, 
                  layout="wide", 
                  initial_sidebar_state="auto", 
                  menu_items=None)


@st.cache_data
def allhome_toptier():  
    url = "https://www.dropbox.com/scl/fi/2akzxhadsxbam2maf6jgr/all_home_toptier_0923.csv?rlkey=wphpn8w4hsnwdae5a17jtpq75&dl=1"
    download = requests.get(url).content
    data = StringIO(download.decode('utf-8'))
    df = pd.read_csv(data)
    df = df.loc[df['State'].str.contains('IL')]
    return df


def a_year(df):
    df['Rate'] = (df[df.columns[-1]] - df[df.columns[-13]]) / df[df.columns[-13]]
    df['1yrDiff'] = df[df.columns[-2]] - df[df.columns[-14]]
    il_result = df[['RegionName', 'State', df.columns[-15], df.columns[-3], 'Rate', '1yrDiff']]
    sorted_il_result = il_result.sort_values(by='Rate', ascending=False)
    return sorted_il_result

def th_year(df):
    df['Rate'] = (df[df.columns[-1]] - df[df.columns[-37]]) / df[df.columns[-37]]
    df['3yrDiff'] = df[df.columns[-2]] - df[df.columns[-38]]
    il_result = df[['RegionName', 'State', df.columns[-39], df.columns[-3], 'Rate', '3yrDiff']]
    sorted_il_result = il_result.sort_values(by='Rate', ascending=False)
    return sorted_il_result

def fi_year(df):
    df['Rate'] = (df[df.columns[-1]] - df[df.columns[-61]]) / df[df.columns[-61]]
    df['5yrDiff'] = df[df.columns[-2]] - df[df.columns[-62]]
    il_result = df[['RegionName', 'State', df.columns[-63], df.columns[-3], 'Rate', '5yrDiff']]
    sorted_il_result = il_result.sort_values(by='Rate', ascending=False)
    return sorted_il_result

def ten_years(df):
    df['Rate'] = (df[df.columns[-1]] - df[df.columns[-121]]) / df[df.columns[-121]]
    df['10yrDiff'] = df[df.columns[-2]] - df[df.columns[-122]]
    il_result = df[['RegionName', 'State', df.columns[-123], df.columns[-3], 'Rate', '10yrDiff']]
    sorted_il_result = il_result.sort_values(by='Rate', ascending=False)    
    return sorted_il_result

def tw_year(df):
    df['Rate'] = (df[df.columns[-1]] - df[df.columns[-241]]) / df[df.columns[-241]]
    df['20yrDiff'] = df[df.columns[-2]] - df[df.columns[-242]]
    il_result = df[['RegionName', 'State', df.columns[-243], df.columns[-3], 'Rate', '20yrDiff']]
    sorted_il_result = il_result.sort_values(by='Rate', ascending=False)
    return sorted_il_result


@st.cache_data
def lat_long(sorted_il_result):
    geolocator = Nominatim(user_agent="Property Analysis")
    lat = []
    lon = []
    top30 = sorted_il_result.head(100)
    for i, q in top30[['RegionName', 'State']].values:
        location = geolocator.geocode(f"{i} {q}")
        if location is not None:
            lat.append(location.latitude)
            lon.append(location.longitude)
        else:
            lat.append(np.nan)
            lon.append(np.nan)
    top30['lat'] = lat
    top30['lon'] = lon
    return top30

# Create the app object

col1,col2,col3 = st.columns([1,1,1])
##############################################################################################

st.header('Illinois Property')
st.subheader('Data up to 09-2023')

option = st.selectbox(
    'Select an option',
        ('All Home Toptier', 'All Home Midtier', 'All Home Lowtier'))


if option =='All Home Toptier': 
    df = allhome_toptier()
elif option == 'All Home Midtier':
    df = midtier()
elif option == 'All Home Lowtier':
    df = lowtier()
    


option_yr = st.selectbox(
    'Choose Year'
    , ('1 Year','3 Years','5 Years','10 Years','20 Years'))



if option_yr =='10 Years':
    sorted_il_result = ten_years(df)
elif option_yr =='1 Year':
    sorted_il_result = a_year(df)
elif option_yr == '3 Years':
    sorted_il_result = th_year(df)
elif option_yr == '5 Years':
    sorted_il_result = fi_year(df)
elif option_yr == '20 Years':
    sorted_il_result = tw_year(df)

st.dataframe(sorted_il_result)

top30 = lat_long(sorted_il_result)

sorted_top30 = top30[['RegionName','lat', 'lon', 'Rate']]

sorted_top30['Rate_str'] = (sorted_top30['Rate']*100).astype(str)

st.dataframe(sorted_top30)
st.write(len(soted_top30))


view = pdk.ViewState(latitude=top30['lat'].mean(),
longitude=top30['lon'].mean(),
pitch = 50,
zoom= 7,
bearing = 0)

column_layer = pdk.Layer(
    "ColumnLayer",
    data=sorted_top30,
    get_position=["lon", "lat"],
    get_elevation="Rate_str",
    elevation_scale=1000,
    radius=700,
    get_fill_color=['Rate*200', '255-Rate*200', '255-Rate*200', 140],
    pickable=True,
    auto_highlight=True,
)

tooltip = {
    "html": "The area: <b>{RegionName}</b>, Increasing of rate: <b>{Rate_str}%</b>",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

# pdk.Deck 호출 시 'layers' 인자로 레이어를 전달합니다.
r = pdk.Deck(
    layers=[column_layer],
    initial_view_state=view,
    tooltip=tooltip,
    map_provider="mapbox",
    map_style=None,  #pdk.map_styles.SATELLITE
)

# Streamlit의 st.pydeck_chart 함수를 사용하여 차트를 표시합니다.
st.pydeck_chart(r)


# # python
# layers = []

# for index, row in top30.iterrows():
#     layers.append(
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=pd.DataFrame({'lon': [row['lon']], 'lat': [row['lat']], 'Rate': [row['Rate']]}),
#             get_position='[lon, lat]',
#             get_color="[200, 30, 0, 160 + row['Rate'] * 100]",
#             get_radius='Rate * 2000',
#         )
#     )

# st.pydeck_chart(pdk.Deck(
#     map_style=None,
#     initial_view_state=pdk.ViewState(
#         latitude=top30['lat'].mean(),
#         longitude=top30['lon'].mean(), # Chicago
#         zoom=9,
#         pitch=50,
#     ),
#     layers=layers,
# ))

