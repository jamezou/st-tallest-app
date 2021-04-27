
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import math
import pydeck as pdk
import seaborn as sns
sns.set_style("whitegrid")

# retrieving the data
df = pd.read_excel("skyscrapers.xlsx")
def home():
    st.header("Home")
    st.markdown("This application was made for users to learn more about the "
                "tallest freestanding structures (over 350 metres)")
    st.markdown("Here is a preview of the first five records from the data set:")
    st.dataframe(df.head())
    st.markdown(f"The pages of this application includes :"
                "\n* a map feature to visually locate the tallest structures"
                "\n* general facts and statistics to learn more about the data set"
                "\n* search function to view specific information regarding structures")
    st.markdown("_Created by Jame Zou_")


def maps(measureChoice):
    mapChoice = st.sidebar.selectbox("Select Map", ["All Structures", "Filter By Location", "Structures Near Me"])
    st.markdown(f"**Viewing {mapChoice}**")
    if mapChoice == "All Structures":
        columns = ["Name", measureChoice, "Lat", "Lon"]
        dfMap = df[columns]
        viewState = pdk.ViewState(
            latitude=round(dfMap["Lat"].mean(), 4),
            longitude=round(dfMap["Lon"].mean(), 4),
            zoom=2,
            pitch=0)
        scatter_layer = pdk.Layer("ScatterplotLayer",
                                  data=dfMap,
                                  get_position=["Lon", "Lat"],
                                  opacity=0.2,
                                  filled=True,
                                  get_radius=100000,
                                  get_radius_scale=1000,
                                  radius_min_pixels=3,
                                  radius_max_pixels=10,
                                  get_fill_color=[255, 0, 0],
                                  pickable=True)

        tool_tip = {"html": "{Name}", "style": {"color": "white"}}
        map1 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                        initial_view_state=viewState,
                        layers=scatter_layer,
                        tooltip=tool_tip)
        map1.to_html()
        return map1, dfMap

    elif mapChoice == "Filter By Location":
        countries = df.Country.unique()
        selectedCountry = st.sidebar.selectbox("Country ", sorted(countries))
        cities = df[df["Country"] == selectedCountry]["City"].unique()
        selectedCity = st.sidebar.selectbox("City: ", sorted(cities))
        latAvg = df[df["City"] == selectedCity]["Lat"].mean()
        lonAvg = df[df["City"] == selectedCity]["Lon"].mean()

        viewState = pdk.ViewState(
            latitude=round(latAvg, 4),
            longitude=round(lonAvg, 4),
            zoom=10,
            pitch=90,
            bearing=0)

        minHeight = math.floor(df[df["City"] == selectedCity][measureChoice].min())
        maxHeight = math.ceil(df[df["City"] == selectedCity][measureChoice].max())
        columns = ["Name", measureChoice, "Country", "City", "Lat", "Lon"]
        dfMap = df[(df["City"] == selectedCity)][columns]

        if dfMap.shape[0] != 1 and minHeight != maxHeight:
            heightRange = st.sidebar.slider(f"Select a height range (in {measureChoice.lower()})", minHeight, maxHeight)
            dfMap = df[(df["City"] == selectedCity) & (df[measureChoice] <= heightRange)][columns]

        column_layer = pdk.Layer("ColumnLayer",
                                 data=dfMap,
                                 get_position=["Lon", "Lat"],
                                 get_elevation=measureChoice,
                                 elevation_scale=8,
                                 radius=115,
                                 get_fill_color=[255, 165, 0, 80],
                                 pickable=True,
                                 extruded=True,
                                 auto_highlight=True)

        tool_tip = {"html": "{Name}", "style": {"color": "white"}}
        map2 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                        initial_view_state=viewState,
                        layers=column_layer,
                        tooltip=tool_tip)
        map2.to_html()
        st.markdown("_Note: Elevation scaled up by 10_")
        return map2, dfMap

    elif mapChoice == "Structures Near Me":
        latInput = float(st.sidebar.text_input("Enter approximate latitude", "40.75"))
        longInput = float(st.sidebar.text_input("Enter approximate longitude", "-74.0"))
        latMin = (latInput - 2)
        latMax = (latInput + 2)
        longMin = (longInput - 2)
        longMax = (longInput + 2)
        dfLat = df[(df["Lat"] >= latMin) & (df["Lat"] <= latMax)][["Name", "Lon", "Lat"]]
        dfMap = dfLat[(dfLat["Lon"] >= longMin) & (dfLat["Lon"] <= longMax)][["Name", "Lon", "Lat"]]

        if dfMap.empty:
            st.markdown("Looks like there are no structures near this location :white_frowning_face:")

        viewState = pdk.ViewState(
            latitude=latInput,
            longitude=longInput,
            zoom=11,
            pitch=0)
        scatter_layer = pdk.Layer("ScatterplotLayer",
                                  data=dfMap,
                                  get_position=["Lon", "Lat"],
                                  opacity=0.2,
                                  filled=True,
                                  get_radius=100000,
                                  get_radius_scale=1000,
                                  radius_min_pixels=3,
                                  radius_max_pixels=10,
                                  get_fill_color=[255, 0, 0],
                                  pickable=True)

        tool_tip = {"html": "{Name}", "style": {"color": "white"}}
        map3 = pdk.Deck(map_style='mapbox://styles/mapbox/light-v9',
                        initial_view_state=viewState,
                        layers=scatter_layer,
                        tooltip=tool_tip)
        map3.to_html()
        return map3, dfMap


def fun_facts(measureChoice):
    # tallest structure
    tallest = df[measureChoice].max()
    tallestName = str(df["Name"][df[measureChoice] == tallest].values)
    tallestName = tallestName[2:-2]
    tallestCountry = str(df["Country"][df[measureChoice] == tallest].values)
    tallestCountry = tallestCountry[3:-2]
    fact1 = f"* The {tallestName} in {tallestCountry} is the tallest structure standing at {tallest} {measureChoice.lower()}"

    # average height of structures
    average = df[measureChoice].mean()
    fact2 = f" * The average height of structures is {average:,.2f} {measureChoice.lower()}"

    # country with the most structures
    mostStructures = df["Country"].value_counts().max()
    mostCountry = df["Country"].value_counts().idxmax()
    fact3 = f"* {mostCountry} has the most tallest structures with {mostStructures} of them"

    st.markdown(f"{fact1} \n{fact2} \n{fact3}")


def pie1(paletteChoice):
    fig, ax = plt.subplots()
    df["Types"] = df["Type"].str.split('/').str[0]
    frequency = df["Types"].value_counts()
    ax.set_title("Types of Structures").set_weight('bold')
    ax.axis('equal')
    ax.pie(frequency, colors=paletteChoice, autopct='%1.2f%%')  # maybe add explode user customization
    ax.legend(labels=frequency.index, loc='best')
    plt.tight_layout()
    st.markdown(f"* The majority of tallest structures are {df['Type'].value_counts().idxmax().lower()}s")
    return plt


def pie2(paletteChoice):
    fig, ax = plt.subplots()
    df["Main use"] = df["Main use"].str.split(',').str[0]
    for use in df["Main use"]:
        if use not in ["Office", "Observation", "Power station", "Hotel", "UHF/VHF-transmission", "Residential"]:
            df["Main use"] = df["Main use"].replace(use, "Other")
    frequency = df["Main use"].value_counts()
    ax.set_title("Primary Main Uses of Structures").set_weight('bold')
    ax.axis('equal')
    ax.pie(frequency, colors=paletteChoice, autopct='%1.2f%%')  # maybe add explode user customization
    ax.legend(labels=frequency.index, loc='best')
    plt.tight_layout()
    st.markdown(f"* The majority of tallest structures are used as {df['Main use'].value_counts().idxmax().lower()}s")
    return plt


def histogram(colorChoice):
    fig, ax = plt.subplots()
    ax.set_title("Number of Structures Built Over the Years").set_weight('bold')
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Structures")
    frequency = df["Year"]
    ax.grid(True)
    ax.hist(frequency,
            bins=[1930, 1945, 1960, 1975, 1990, 2005, 2020],
            color=colorChoice)
    plt.tight_layout()
    st.markdown(f"* Between 1930 and 2020, {df['Name'].count()} structures were built")
    st.markdown(f"* {df[df['Year'] >= 2000]['Year'].count()} of these structures were built after 2000 alone")
    return plt


def barchart(measureChoice, colorChoice):
    fig, ax = plt.subplots()
    num = st.select_slider("Slide to select", options=[1, 5, 10, 15, 30])
    names = df.sort_values(measureChoice, ascending=False)["Name"].head(num)
    x = np.arange(len(names))
    y = df.sort_values(measureChoice, ascending=False)[measureChoice].head(num)
    ax.bar(x, y, color=colorChoice)
    ax.set_title(f"Top {len(names)} Tallest Freestanding Structures").set_weight('bold')
    ax.set_xlabel("Structure Name")
    ax.set_ylabel(f"Height (in {measureChoice})")
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    plt.tight_layout()
    return plt


def scatterplot(measureChoice, colorChoice):
    x = df["Year"]
    y = df[measureChoice]
    fig, ax = plt.subplots()
    ax.scatter(x, y, color=colorChoice)
    ax.set_title("Year vs Height of Structures")
    ax.set_xlabel("Year")
    ax.set_ylabel(f"Height in ({measureChoice})")
    return plt


def additional_search():
    countries = df.Country.unique()
    selectedCountry = st.sidebar.selectbox("Country ", sorted(countries))
    cities = df[df["Country"] == selectedCountry]["City"].unique()
    selectedCity = st.sidebar.selectbox("City ", sorted(cities))

    columnNames = ["Name", "Height", "Year", "Type", "Main use", "Country", "City", "Remarks", "Lat", "Lon"]
    columnSelection = st.sidebar.multiselect("Select columns", columnNames)

    minYear = int(df[df["City"] == selectedCity]["Year"].min())
    maxYear = int(df[df["City"] == selectedCity]["Year"].max())

    if "Height" in columnSelection and "Year" in columnSelection:
        measureChoice = measure_side_bar()
        minHeight = math.floor(df[df["City"] == selectedCity][measureChoice].min())
        maxHeight = math.ceil(df[df["City"] == selectedCity][measureChoice].max())
        columnSelection.remove("Height")
        columnSelection.append(measureChoice)
        if (minHeight != maxHeight) and (minYear != maxYear):
            heightRange = st.sidebar.slider("Height Range", minHeight, maxHeight)
            yearRange = st.sidebar.slider("Year Range", minYear, maxYear)
            st.table(df[(df["City"] == selectedCity) & (df["Year"] <= yearRange)
                        & (df[measureChoice] <= heightRange)][columnSelection])
        elif (minHeight == maxHeight) and (minYear != maxYear):
            yearRange = st.sidebar.slider("Year Range", minYear, maxYear)
            st.table(df[(df["City"] == selectedCity) & (df["Year"] <= yearRange)
                        & (df[measureChoice] == minHeight)][columnSelection])
        elif (minHeight != maxHeight) and (minYear == maxYear):
            heightRange = st.sidebar.slider("Height Range", minHeight, maxHeight)
            st.table(df[(df["City"] == selectedCity) & (df["Year"] == minYear)
                        & (df[measureChoice] <= heightRange)][columnSelection])
        else:
            st.table(df[(df["City"] == selectedCity) & (df["Year"] == minYear)
                        & (df[measureChoice] <= minHeight)][columnSelection])

    elif "Height" in columnSelection:
        measureChoice = measure_side_bar()
        columnSelection.remove("Height")
        columnSelection.append(measureChoice)
        minHeight = math.floor(df[df["City"] == selectedCity][measureChoice].min())
        maxHeight = math.ceil(df[df["City"] == selectedCity][measureChoice].max())
        if minHeight != maxHeight:
            heightRange = st.sidebar.slider("Height Range", minHeight, maxHeight)
            st.table(df[(df["City"] == selectedCity) & (df[measureChoice] <= heightRange)][columnSelection])
        else:
            st.table(df[(df["City"] == selectedCity) & (df[measureChoice] == minHeight)][columnSelection])

    elif "Year" in columnSelection:
        if minYear != maxYear:
            yearRange = st.sidebar.slider("Year Range", minYear, maxYear)
            st.table(df[(df["City"] == selectedCity) & (df["Year"] <= yearRange)][columnSelection])
        else:
            st.table(df[(df["City"] == selectedCity) & (df["Year"] == minYear)][columnSelection])
    else:
        st.table(df[df["City"] == selectedCity][columnSelection])


def measure_side_bar():
    measurements = {"Metres": "m", "Feet": "f"}
    measureChoice = st.sidebar.radio("Measurements Options", list(measurements.keys()))
    return measureChoice


def color_side_bar():
    # palette selection
    colorPalettes = {"Pastel": sns.color_palette("pastel"), "Colorblind": sns.color_palette("colorblind"),
                     "Bright": sns.color_palette("bright"), "Muted": sns.color_palette("muted"),
                     "Deep": sns.color_palette("deep"), "Dark": sns.color_palette("dark")}
    selectedPal = st.sidebar.selectbox("Color Palette", list(colorPalettes.keys()))
    paletteChoice = colorPalettes[selectedPal]
    # single color selection
    colorOption = st.sidebar.radio("Single Color", ["Default", "Custom"])
    if colorOption == "Default":
        defaultColors = {"Palette Blue": sns.color_palette(selectedPal.lower(), 1), "Cyan": "c", "Blue": "b",
                         "Green": "g", "Red": "r", "Magenta": "m", "Yellow": "y", "Black": "k"}
        colorChoice = defaultColors[st.sidebar.selectbox("Single Colors", list(defaultColors.keys()))]
    else:
        colorChoice = st.sidebar.color_picker("Custom Color")
    return paletteChoice, colorChoice


def main():
    st.title("Tallest Structures In the World :cityscape:")
    st.markdown("**_Data taken from Wikipedia_**")
    st.sidebar.subheader("Page Navigation")
    pageOptions = ["Home", "Locating Structures", "Learn More", "Additional Search"]
    selectedPage = st.sidebar.selectbox("View Page ", pageOptions)

    if selectedPage == "Home":
        home()

    elif selectedPage == "Locating Structures":
        st.header("Locating Structures")
        st.sidebar.subheader("Settings")
        measureChoice = measure_side_bar()
        newMap, dfMap = maps(measureChoice)
        st.pydeck_chart(newMap)  # map
        viewData = st.checkbox("View data")
        if viewData:
            st.table(dfMap)

    elif selectedPage == "Learn More":
        st.header("Learn More")
        st.sidebar.subheader("Settings")
        measureChoice = measure_side_bar()  # user measurement option selection
        paletteChoice, colorChoice = color_side_bar()  # user color palette selection
        fun_facts(measureChoice)  # facts
        st.subheader("Chart(s)")
        selectedChart = st.selectbox("Select Chart", ["Purpose of Structures", "Number Built Over Years",
                                                      "Top Tallest Structures", "Year vs Height", "All"])
        if selectedChart == "Purpose of Structures":
            pieChoice = st.radio("Select Pie Chart", ["Types of Structures", "Main Uses"])
            if pieChoice == "Types of Structures":
                st.pyplot(pie1(paletteChoice))
            else:
                st.pyplot(pie2(paletteChoice))
        elif selectedChart == "Number Built Over Years":
            st.pyplot(histogram(colorChoice))
        elif selectedChart == "Top Tallest Structures":
            st.pyplot(barchart(measureChoice, colorChoice))
        elif selectedChart == "Year vs Height":
            st.pyplot(scatterplot(measureChoice, colorChoice))
        else:
            st.pyplot(pie1(paletteChoice))  # pie chart
            st.pyplot(pie2(paletteChoice))
            st.pyplot(histogram(colorChoice))  # histogram
            st.pyplot(barchart(measureChoice, colorChoice))  # bar chart
            st.pyplot(scatterplot(measureChoice, colorChoice))  # scatterplot

    elif selectedPage == "Additional Search":
        st.header("Select Query")
        st.markdown("View data for any structure by location and filtering specific criteria")
        st.sidebar.subheader("Filter By")
        additional_search()


if __name__ == "__main__":
    main()
