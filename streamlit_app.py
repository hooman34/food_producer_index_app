import streamlit as st
from app.utils.fetch_data import *
from app.utils.streamlit_utils import *
from fredapi import Fred

# call fred class
fred = fred()

# select to create bar
food = st.multiselect(label="Select the ingredients you usually order",
                      options=fred.food_options.food_name, key='food_option')

analysis_start = st.button("Start analysis", key='analysis_button')
# click analysis button
if analysis_start:
    st.write('The food choices you have selected:', food)

    food_code_dict = fred.retrieve_code_from_food_name(food)
    st.write(food_code_dict)

    food_index_data = fred.collect_food_index(food_code_dict)
    st.write("Data collected:")

    st.write("Creating plots")
    fig = create_plots(food_index_data)
    st.plotly_chart(fig, use_container_width=True)

