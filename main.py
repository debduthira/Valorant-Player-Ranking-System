"""import streamlit as st
import pandas as pd

# Initialize data storage
if "match_data" not in st.session_state:
    st.session_state.match_data = []


# Function to calculate K/D ratio
def calculate_kd_ratio(kills, deaths):
    if deaths == 0:
        return kills  # Return kills if deaths are zero to avoid division by zero
    return kills / deaths


# Function to aggregate player statistics
def aggregate_player_stats(data):
    if len(data) == 0:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Calculate K/D ratio for each match
    df["K/D Ratio"] = df.apply(
        lambda row: calculate_kd_ratio(row["Kills"], row["Deaths"]), axis=1
    )

    # Group by player name and calculate aggregated stats
    aggregated_df = (
        df.groupby("Player Name")
        .agg(
            {
                "Average Combat Score (ACS)": "mean",  # Average ACS
                "Econ Rating": "mean",  # Average Econ Rating
                "Kills": "sum",  # Total Kills
                "Deaths": "sum",  # Total Deaths
                "Assists": "sum",  # Total Assists
                "K/D Ratio": "mean",  # Average K/D Ratio
                "Win/Loss": "count",  # Total Matches Played
            }
        )
        .reset_index()
    )

    # Rename columns for clarity
    aggregated_df.rename(
        columns={
            "Win/Loss": "Matches Played",
            "Average Combat Score (ACS)": "Avg ACS",
            "Econ Rating": "Avg Econ Rating",
        },
        inplace=True,
    )

    return aggregated_df


# Function to rank players based on aggregated ACS
def rank_players(aggregated_df):
    ranked_df = aggregated_df.sort_values(by="Avg ACS", ascending=False).reset_index(
        drop=True
    )
    ranked_df.index += 1  # Make index start from 1
    return ranked_df


# Streamlit app layout
st.title("Player Statistics Tracker")

# Input form for match details
with st.form("match_form"):
    st.subheader("Enter Match Details")

    player_name = st.text_input("Player Name")
    win_loss = st.selectbox("Win/Loss", ["Win", "Loss"])

    # Dropdown list for "Map"
    map_name = st.selectbox(
        "Map",
        [
            "Bind",
            "Split",
            "Ascent",
            "Haven",
            "Breeze",
            "Fracture",
            "Icebox",
            "Pearl",
            "Sunset",
            "Abyss",
        ],
    )

    # Dropdown list for "Agent"
    agent = st.selectbox(
        "Agent",
        [
            "Astra",
            "Breach",
            "Brimstone",
            "Chamber",
            "Clove",
            "Cypher",
            "Deadlock",
            "Harbor",
            "Iso",
            "Jett",
            "Kay/O",
            "Killjoy",
            "Neon",
            "Omen",
            "Phoenix",
            "Raze",
            "Reyna",
            "Sage",
            "Skye",
            "Sova",
            "Viper",
            "Vyse",
            "Yoru",
        ],
    )

    # Dropdown list for "Current Rank"
    current_rank = st.selectbox(
        "Current Rank",
        [
            "Unranked",
            "Iron 1",
            "Iron 2",
            "Iron 3",
            "Bronze 1",
            "Bronze 2",
            "Bronze 3",
            "Silver 1",
            "Silver 2",
            "Silver 3",
            "Gold 1",
            "Gold 2",
            "Gold 3",
            "Platinum 1",
            "Platinum 2",
            "Platinum 3",
            "Diamond 1",
            "Diamond 2",
            "Diamond 3",
            "Ascendant 1",
            "Ascendant 2",
            "Ascendant 3",
            "Immortal 1",
            "Immortal 2",
            "Immortal 3",
            "Radiant",
        ],
    )

    acs = st.number_input("Average Combat Score (ACS)", min_value=0)
    econ_rating = st.number_input("Econ Rating", min_value=0.0)
    kills = st.number_input("Kills", min_value=0)
    deaths = st.number_input("Deaths", min_value=0)
    assists = st.number_input("Assists", min_value=0)

    # Submit button for form
    submitted = st.form_submit_button("Add Match")
    if submitted and player_name:
        # Append new match data to the session state
        st.session_state.match_data.append(
            {
                "Player Name": player_name,
                "Win/Loss": win_loss,
                "Map": map_name,
                "Agent": agent,
                "Current Rank": current_rank,
                "Average Combat Score (ACS)": acs,
                "Econ Rating": econ_rating,
                "Kills": kills,
                "Deaths": deaths,
                "Assists": assists,
            }
        )
        st.success("Match details added successfully!")

# Input form for deleting a record
with st.form("delete_form"):
    st.subheader("Delete a Record")

    if st.session_state.match_data:
        df = pd.DataFrame(st.session_state.match_data)
        # Create a selectbox to choose the record to delete
        record_options = df.apply(
            lambda row: f"{row['Player Name']} | {row['Map']} | {row['Agent']} | {row['Current Rank']} | {row['Kills']}/{row['Deaths']}",
            axis=1,
        )
        record_to_delete = st.selectbox("Select Record to Delete", record_options)

        if st.form_submit_button("Delete Record"):
            # Find the index of the selected record
            record_index = record_options[record_options == record_to_delete].index[0]
            # Remove the selected record from session state
            st.session_state.match_data.pop(record_index)
            st.success("Record deleted successfully!")

# Convert match data to a DataFrame
if st.session_state.match_data:
    df = pd.DataFrame(st.session_state.match_data)

    # Calculate K/D ratio for each match
    df["K/D Ratio"] = df.apply(
        lambda row: calculate_kd_ratio(row["Kills"], row["Deaths"]), axis=1
    )

    st.subheader("Match Details")
    st.dataframe(df)

    # Aggregate player statistics
    aggregated_df = aggregate_player_stats(st.session_state.match_data)

    # Display aggregated player statistics
    if not aggregated_df.empty:
        st.subheader("Aggregated Player Statistics")
        st.dataframe(aggregated_df)

        # Display ranked players
        st.subheader("Ranked Players by Avg ACS")
        ranked_df = rank_players(aggregated_df)
        st.dataframe(ranked_df)
else:
    st.info("No match data available. Please add match details using the form above.")
"""

import streamlit as st
import pandas as pd
import sqlite3

# Database connection setup
conn = sqlite3.connect("player_stats.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute(
    """
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY,
    player_name TEXT,
    win_loss TEXT,
    map_name TEXT,
    agent TEXT,
    current_rank TEXT,
    acs INTEGER,
    econ_rating REAL,
    kills INTEGER,
    deaths INTEGER,
    assists INTEGER
)
"""
)
conn.commit()


# Function to calculate K/D ratio
def calculate_kd_ratio(kills, deaths):
    if deaths == 0:
        return kills  # Return kills if deaths are zero to avoid division by zero
    return kills / deaths


# Function to add match details to the database
def add_match(
    player_name,
    win_loss,
    map_name,
    agent,
    current_rank,
    acs,
    econ_rating,
    kills,
    deaths,
    assists,
):
    c.execute(
        """
    INSERT INTO matches (player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            player_name,
            win_loss,
            map_name,
            agent,
            current_rank,
            acs,
            econ_rating,
            kills,
            deaths,
            assists,
        ),
    )
    conn.commit()


# Function to delete a match from the database
def delete_match(record_id):
    c.execute("DELETE FROM matches WHERE id = ?", (record_id,))
    conn.commit()


# Function to fetch all matches from the database
def fetch_matches():
    c.execute("SELECT * FROM matches")
    return c.fetchall()


# Function to aggregate player statistics
def aggregate_player_stats(data):
    if len(data) == 0:
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(
        data,
        columns=[
            "ID",
            "Player Name",
            "Win/Loss",
            "Map",
            "Agent",
            "Current Rank",
            "Average Combat Score (ACS)",
            "Econ Rating",
            "Kills",
            "Deaths",
            "Assists",
        ],
    )

    # Calculate K/D ratio for each match
    df["K/D Ratio"] = df.apply(
        lambda row: calculate_kd_ratio(row["Kills"], row["Deaths"]), axis=1
    )

    # Group by player name and calculate aggregated stats
    aggregated_df = (
        df.groupby("Player Name")
        .agg(
            {
                "Average Combat Score (ACS)": "mean",  # Average ACS
                "Econ Rating": "mean",  # Average Econ Rating
                "Kills": "sum",  # Total Kills
                "Deaths": "sum",  # Total Deaths
                "Assists": "sum",  # Total Assists
                "K/D Ratio": "mean",  # Average K/D Ratio
                "Win/Loss": "count",  # Total Matches Played
            }
        )
        .reset_index()
    )

    # Rename columns for clarity
    aggregated_df.rename(
        columns={
            "Win/Loss": "Matches Played",
            "Average Combat Score (ACS)": "Avg ACS",
            "Econ Rating": "Avg Econ Rating",
        },
        inplace=True,
    )

    return aggregated_df


# Function to rank players based on aggregated ACS
def rank_players(aggregated_df):
    ranked_df = aggregated_df.sort_values(by="Avg ACS", ascending=False).reset_index(
        drop=True
    )
    ranked_df.index += 1  # Make index start from 1
    return ranked_df


# Streamlit app layout
st.title("Player Statistics Tracker")

# Input form for match details
with st.form("match_form"):
    st.subheader("Enter Match Details")

    player_name = st.text_input("Player Name")
    win_loss = st.selectbox("Win/Loss", ["Win", "Loss"])

    # Dropdown list for "Map"
    map_name = st.selectbox(
        "Map",
        [
            "Bind",
            "Split",
            "Ascent",
            "Haven",
            "Breeze",
            "Fracture",
            "Icebox",
            "Pearl",
            "Sunset",
            "Abyss",
        ],
    )

    # Dropdown list for "Agent"
    agent = st.selectbox(
        "Agent",
        [
            "Astra",
            "Breach",
            "Brimstone",
            "Chamber",
            "Clove",
            "Cypher",
            "Deadlock",
            "Harbor",
            "Iso",
            "Jett",
            "Kay/O",
            "Killjoy",
            "Neon",
            "Omen",
            "Phoenix",
            "Raze",
            "Reyna",
            "Sage",
            "Skye",
            "Sova",
            "Viper",
            "Vyse",
            "Yoru",
        ],
    )

    # Dropdown list for "Current Rank"
    current_rank = st.selectbox(
        "Current Rank",
        [
            "Unranked",
            "Iron 1",
            "Iron 2",
            "Iron 3",
            "Bronze 1",
            "Bronze 2",
            "Bronze 3",
            "Silver 1",
            "Silver 2",
            "Silver 3",
            "Gold 1",
            "Gold 2",
            "Gold 3",
            "Platinum 1",
            "Platinum 2",
            "Platinum 3",
            "Diamond 1",
            "Diamond 2",
            "Diamond 3",
            "Ascendant 1",
            "Ascendant 2",
            "Ascendant 3",
            "Immortal 1",
            "Immortal 2",
            "Immortal 3",
            "Radiant",
        ],
    )

    acs = st.number_input("Average Combat Score (ACS)", min_value=0)
    econ_rating = st.number_input("Econ Rating", min_value=0.0)
    kills = st.number_input("Kills", min_value=0)
    deaths = st.number_input("Deaths", min_value=0)
    assists = st.number_input("Assists", min_value=0)

    # Submit button for form
    submitted = st.form_submit_button("Add Match")
    if submitted and player_name:
        # Add new match data to the database
        add_match(
            player_name,
            win_loss,
            map_name,
            agent,
            current_rank,
            acs,
            econ_rating,
            kills,
            deaths,
            assists,
        )
        st.success("Match details added successfully!")

# Input form for deleting a record
with st.form("delete_form"):
    st.subheader("Delete a Record")

    match_data = fetch_matches()

    if match_data:
        # Create a selectbox to choose the record to delete
        df = pd.DataFrame(
            match_data,
            columns=[
                "ID",
                "Player Name",
                "Win/Loss",
                "Map",
                "Agent",
                "Current Rank",
                "Average Combat Score (ACS)",
                "Econ Rating",
                "Kills",
                "Deaths",
                "Assists",
            ],
        )
        record_options = df.apply(
            lambda row: f"{row['ID']} | {row['Player Name']} | {row['Map']} | {row['Agent']} | {row['Current Rank']} | {row['Kills']}/{row['Deaths']}",
            axis=1,
        )
        record_to_delete = st.selectbox("Select Record to Delete", record_options)

        if st.form_submit_button("Delete Record"):
            # Extract ID from the selected record
            record_id = int(record_to_delete.split(" | ")[0])
            delete_match(record_id)
            st.success("Record deleted successfully!")

# Fetch match data from the database
match_data = fetch_matches()

# Convert match data to a DataFrame
if match_data:
    df = pd.DataFrame(
        match_data,
        columns=[
            "ID",
            "Player Name",
            "Win/Loss",
            "Map",
            "Agent",
            "Current Rank",
            "Average Combat Score (ACS)",
            "Econ Rating",
            "Kills",
            "Deaths",
            "Assists",
        ],
    )

    # Calculate K/D ratio for each match
    df["K/D Ratio"] = df.apply(
        lambda row: calculate_kd_ratio(row["Kills"], row["Deaths"]), axis=1
    )

    st.subheader("Match Details")
    st.dataframe(df.drop(columns=["ID"]))  # Hide ID column

    # Aggregate player statistics
    aggregated_df = aggregate_player_stats(match_data)

    # Display aggregated player statistics
    if not aggregated_df.empty:
        st.subheader("Aggregated Player Statistics")
        st.dataframe(aggregated_df)

        # Display ranked players
        st.subheader("Ranked Players by Avg ACS")
        ranked_df = rank_players(aggregated_df)
        st.dataframe(ranked_df)
else:
    st.info("No match data available. Please add match details using the form above.")
