import streamlit as st
from app.utils.fetch_data import *
from app.utils.streamlit_utils import *
from fredapi import Fred

# call fred class
fred = fred()

# st.write(fred.food_options)

food = st.selectbox(label="Select food", options=fred.food_options.food_name, key='food_option')
st.write('Type in the food you would like to see:', food)

