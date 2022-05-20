import streamlit as st
from app.utils.fetch_data import *
from app.utils.streamlit_utils import *
from PIL import Image
from fredapi import Fred
import requests
from io import BytesIO

response = requests.get("https://github.com/hooman34/tridge_demo/blob/main/app/other/tridge_image.png?raw=true")
image = Image.open(BytesIO(response.content))

_, col2, _ = st.columns([1, 2, 1])
with col2:
    st.title("Tridge demo")
_, _, col3 = st.columns([1, 2, 1])
with col3:
    st.text("Gieun Kwak")

st.markdown("")
st.markdown("")

# image = Image.open("./app/other/tridge_image.PNG")
st.image(image)
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")
st.markdown("")

# call fred class
fred = fred_processor()

# select to create bar
food = st.multiselect(label="Select the ingredients you usually order. \nYou can click, or type in the text.",
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

    _, col2, _ = st.columns([1, 2, 1])
    # with col2:
    st.subheader('Expected price change')

    forecast_results = fred.forecast(food_index_data)

    # write insight report
    fred.forecast_report(food_index_data, forecast_results)






