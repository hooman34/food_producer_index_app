import streamlit as st
from app.utils.fetch_data import *
from app.utils.streamlit_utils import *
from fredapi import Fred

# call fred class
fred = fred()

# select to create bar
food = st.multiselect(label="Select the ingredients you usually order",
                    options=fred.food_options.food_name, key='food_option')

analysis_start = st.button("Start analysis")

if analysis_start:
    st.write('Type in the food you would like to see:', food)
    food_codes = fred.retrieve_code_from_food_name(food)
    st.write(food_codes)

