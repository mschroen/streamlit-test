import streamlit as st
import pandas as pd
import math
from pathlib import Path
import sklearn
from figurex import Figure

# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='CRNS Data Dashboard',
    page_icon=':earth_americas:', # This is an emoji shortcode. Could be a URL too.
)

# -----------------------------------------------------------------------------
# Declare some useful functions.

@st.cache_data
def get_gdp_data():
    """Grab GDP data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent/'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    # The data above has columns like:
    # - Country Name
    # - Country Code
    # - [Stuff I don't care about]
    # - GDP for 1960
    # - GDP for 1961
    # - GDP for 1962
    # - ...
    # - GDP for 2022
    #
    # ...but I want this instead:
    # - Country Name
    # - Country Code
    # - Year
    # - GDP
    #
    # So let's pivot all those year-columns into two: Year and GDP
    gdp_df = raw_gdp_df.melt(
        ['Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    # Convert years from string to integers
    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])

    return gdp_df

gdp_df = get_gdp_data()

# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# :earth_americas: CRNS Data dashboard 2

So the preview is stupid.
Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

# Add some spacing
''
''

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

spectra = st.file_uploader("upload file", type={"csv", "txt"})
if spectra is not None:
    spectra_df = pd.read_csv(spectra)
    st.write(spectra_df)

    csv = convert_df(spectra_df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name="large_df.csv",
        mime="text/csv",
    )

with Figure() as ax:
    ax.plot([1,2,3], [4,5,6])
st.pyplot(Figure.get())

from magazine import Magazine, Publish
Magazine.report("topic1", "hallo")
st.write("gemacht!")
st.write(Magazine.post("topic1"))
Magazine.report("topic1", "heee")
Magazine.report("topic1", Figure.get())
with Publish("report.pdf", "huhu") as M:
    M.add_topic("topic1")
    M.add_figure("topic1")

with open("report.pdf", "rb") as file:
    btn = st.download_button(
        label="Download Report",
        data=file,
        file_name="report.pdf",
        mime="application/pdf",
    )


path = Path(__file__).parent/'data/test.csv'
data = pd.read_csv(path)

beta = st.slider(
    'Beta',
    min_value=120,
    max_value=160,
    value=133)

import numpy as np
data["N_p"] = data["N"]*np.exp((1013-data["P"])/beta)
#st.line_chart(
#    data,
#    x="time",
#    y="N_p",
#)
import plotly.express as px
st.plotly_chart(px.line(data, x="time" ,y=["N","N_p"]), use_container_width=True)

"""
# import pandas as pd
from pathlib import Path
from neptoon.workflow.process_with_yaml import ProcessWithYaml
from neptoon.config import ConfigurationManager
from neptoon.data_audit import DataAuditLog


config = ConfigurationManager()

station_config_path = Path(__file__).parent/'data/A101_station.yaml'
processing_config_path = Path(__file__).parent/'data/v1_processing_method.yaml'

config.load_and_validate_configuration(
    name="station",
    file_path=station_config_path,
)
config.load_and_validate_configuration(
    name="processing",
    file_path=processing_config_path,
)

DataAuditLog.create()
yaml_processor = ProcessWithYaml(configuration_object=config)

## OPTION 1:
# data_hub = yaml_processor.create_data_hub()

## OPTION 2:
yaml_processor.run_full_process()
"""

# Add some spacing
''
''


min_value = gdp_df['Year'].min()
max_value = gdp_df['Year'].max()

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value])

countries = gdp_df['Country Code'].unique()

if not len(countries):
    st.warning("Select at least one country")

selected_countries = st.multiselect(
    'Which countries would you like to view?',
    countries,
    ['DEU', 'FRA', 'GBR', 'BRA', 'MEX', 'JPN'])

''
''
''

# Filter the data
filtered_gdp_df = gdp_df[
    (gdp_df['Country Code'].isin(selected_countries))
    & (gdp_df['Year'] <= to_year)
    & (from_year <= gdp_df['Year'])
]

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y='GDP',
    color='Country Code',
)

''
''


first_year = gdp_df[gdp_df['Year'] == from_year]
last_year = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, country in enumerate(selected_countries):
    col = cols[i % len(cols)]

    with col:
        first_gdp = first_year[first_year['Country Code'] == country]['GDP'].iat[0] / 1000000000
        last_gdp = last_year[last_year['Country Code'] == country]['GDP'].iat[0] / 1000000000

        if math.isnan(first_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{country} GDP',
            value=f'{last_gdp:,.0f}B',
            delta=growth,
            delta_color=delta_color
        )
