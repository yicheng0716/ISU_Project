import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "fishing_trips.db"


def create_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            location TEXT NOT NULL,
            weather TEXT NOT NULL,
            bait TEXT NOT NULL,
            caught TEXT NOT NULL,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()


def add_trip(date, location, weather, bait, caught, notes):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO trips (date, location, weather, bait, caught, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, location, weather, bait, caught, notes))
    conn.commit()
    conn.close()


def get_trips():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM trips ORDER BY id DESC", conn)
    conn.close()
    return df


def delete_trip(trip_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM trips WHERE id = ?", (trip_id,))
    conn.commit()
    conn.close()


def get_statistics(df):
    if df.empty:
        return 0, "No data", "No data", "Add a trip to get suggestions."

    successful_trips = df[df["caught"] == "Yes"]
    success_count = len(successful_trips)

    most_used_bait = df["bait"].mode()[0]

    if successful_trips.empty:
        best_bait = "No successful catches yet"
        suggestion = "Add more successful fishing trips to get better suggestions."
    else:
        best_bait = successful_trips["bait"].mode()[0]
        suggestion = "Try using " + best_bait + " because it has the most successful catches."

    return success_count, most_used_bait, best_bait, suggestion


create_table()

st.set_page_config(page_title="Fishing Assistant", layout="wide")

st.title("Fishing Assistant")

df = get_trips()

success_count, most_used_bait, best_bait, suggestion = get_statistics(df)

st.header("Dashboard")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Successful Trips", success_count)

with col2:
    st.metric("Most Used Bait", most_used_bait)

with col3:
    st.metric("Best Bait for Catches", best_bait)

with col4:
    st.metric("Total Trips", len(df))

st.header("Add New Fishing Trip")

with st.form("add_trip_form"):
    date = st.date_input("Date")
    location = st.text_input("Location")
    weather = st.selectbox("Weather", ["Sunny", "Cloudy", "Overcast", "Rainy", "Windy"])
    bait = st.selectbox("Bait Used", ["Worm", "Minnow", "Spinner", "Cricket", "Other"])
    caught = st.radio("Did you catch fish?", ["Yes", "No"])
    notes = st.text_area("Notes")

    submit = st.form_submit_button("Add Trip")

    if submit:
        if location.strip() == "":
            st.error("Please enter a location.")
        else:
            add_trip(str(date), location, weather, bait, caught, notes)
            st.success("Fishing trip added successfully.")
            st.rerun()

st.header("Suggestions")
st.write(suggestion)

st.header("Trip History")

if df.empty:
    st.write("No fishing trips have been added yet.")
else:
    st.dataframe(df, use_container_width=True)

    st.subheader("Delete a Trip")

    trip_id = st.number_input("Enter the ID of the trip you want to delete", min_value=1, step=1)

    if st.button("Delete Trip"):
        delete_trip(trip_id)
        st.success("Trip deleted successfully.")
        st.rerun()

st.header("Statistics")

if df.empty:
    st.write("Add trips to see statistics.")
else:
    st.subheader("Bait Usage")
    bait_counts = df["bait"].value_counts()
    st.bar_chart(bait_counts)

    st.subheader("Catch Results")
    catch_counts = df["caught"].value_counts()
    st.bar_chart(catch_counts)