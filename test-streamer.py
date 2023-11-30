# test-streamer.py
import time  # to simulate a real time data, time loop

import numpy as np  # np mean, np random
import pandas as pd
import plotly.express as px  # interactive charts
import streamlit as st  # web development

from poc_streamlit.streamer import Stream

df_buy = pd.DataFrame(columns=['Price', 'Quantity', 'USD Value'])
df_sell = pd.DataFrame(columns=['Price', 'Quantity', 'USD Value'])

st.set_page_config(
    page_title='Real-Time Data Science Dashboard', page_icon='✅', layout='wide'
)

# dashboard title

st.title("Real-Time / Live Data Science Dashboard")

placeholder = st.empty()

Stream(df_buy, df_sell, placeholder).connect()
