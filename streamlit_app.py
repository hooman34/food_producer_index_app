import streamlit as st
from app.utils.fetch_data import *
from app.utils.streamlit_utils import *
from fredapi import Fred

# call fred class
fred = fred_processor()

# select to create bar
food = st.multiselect(label="Select the ingredients you usually order",
                      options=fred.food_options.food_name, key='food_option')

view_price_index = st.button("See price changes", key='view_price_index_button')
# click analysis button
if view_price_index:
    st.info('The food you have selected: {}'.format(food))

    food_code_dict = fred.retrieve_code_from_food_name(food)
    # st.write(food_code_dict)

    food_index_data = fred.collect_food_index(food_code_dict)
    # st.write("Data collected")

    # st.write("Creating plots")
    fig = create_plots(food_index_data)
    st.plotly_chart(fig, use_container_width=True)

    st.write('start forecasting')
    forecast_results = fred.forecast(food_index_data)

    # write insight report
    fred.forecast_report(food_index_data, forecast_results)






