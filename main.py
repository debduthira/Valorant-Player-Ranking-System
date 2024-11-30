import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Supabase connection setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Function to calculate K/D ratio
def calculate_kd_ratio(kills, deaths):
    return kills if deaths == 0 else kills / deaths

# Function to add match details to the Supabase database
def add_match(player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists):
    response = supabase.table("matches").insert({
        "player_name": player_name,
        "win_loss": win_loss,
        "map_name": map_name,
        "agent": agent,
        "current_rank": current_rank,
        "acs": acs,
        "econ_rating": econ_rating,
        "kills": kills,
        "deaths": deaths,
        "assists": assists
    }).execute()
    return response

# Function to delete a match from the Supabase database
def delete_match(record_id):
    response = supabase.table("matches").delete().eq("id", record_id).execute()
    return response

# Function to fetch all matches from the Supabase database
def fetch_matches():
    response = supabase.table("matches").select("*").execute()
    return response.data 

# Function to aggregate player statistics
def aggregate_player_stats(data):
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["K/D Ratio"] = df.apply(lambda row: calculate_kd_ratio(row["kills"], row["deaths"]), axis=1)
    aggregated_df = (
        df.groupby("player_name")
        .agg({
            "acs": "mean",
            "econ_rating": "mean",
            "kills": "sum",
            "deaths": "sum",
            "assists": "sum",
            "K/D Ratio": "mean",
            "win_loss": "count"
        })
        .reset_index()
        .rename(columns={"win_loss": "matches_played", "acs": "avg_acs", "econ_rating": "avg_econ_rating"})
    )
    return aggregated_df

# Function to rank players based on aggregated ACS
def rank_players(aggregated_df):
    ranked_df = aggregated_df.sort_values(by="avg_acs", ascending=False).reset_index(drop=True)
    ranked_df.index += 1
    return ranked_df

# Streamlit app layout
st.title("Player Statistics Tracker")

# Input form for match details
with st.form("match_form"):
    st.subheader("Enter Match Details")
    player_name = st.text_input("Player Name")
    win_loss = st.selectbox("Win/Loss", ["Win", "Loss"])
    map_name = st.selectbox("Map", ["Bind", "Split", "Ascent", "Haven", "Breeze", "Fracture", "Icebox", "Pearl", "Sunset", "Abyss"])
    agent = st.selectbox("Agent", ["Astra", "Breach", "Brimstone", "Chamber", "Clove", "Cypher", "Deadlock", "Harbor", "Iso", "Jett", "Kay/O", "Killjoy", "Neon", "Omen", "Phoenix", "Raze", "Reyna", "Sage", "Skye", "Sova", "Viper", "Vyse", "Yoru"])
    current_rank = st.selectbox("Current Rank", ["Unranked", "Iron 1", "Iron 2", "Iron 3", "Bronze 1", "Bronze 2", "Bronze 3", "Silver 1", "Silver 2", "Silver 3", "Gold 1", "Gold 2", "Gold 3", "Platinum 1", "Platinum 2", "Platinum 3", "Diamond 1", "Diamond 2", "Diamond 3", "Ascendant 1", "Ascendant 2", "Ascendant 3", "Immortal 1", "Immortal 2", "Immortal 3", "Radiant"])
    acs = st.number_input("Average Combat Score (ACS)", min_value=0)
    econ_rating = st.number_input("Econ Rating", min_value=0.0)
    kills = st.number_input("Kills", min_value=0)
    deaths = st.number_input("Deaths", min_value=0)
    assists = st.number_input("Assists", min_value=0)
    submitted = st.form_submit_button("Add Match")
    if submitted and player_name:
        add_match(player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists)
        st.success("Match details added successfully!")

# Input form for deleting a record
with st.form("delete_form"):
    st.subheader("Delete a Record")
    match_data = fetch_matches()
    if match_data:
        df = pd.DataFrame(match_data)
        record_options = df.apply(lambda row: f"{row['id']} | {row['player_name']} | {row['map_name']} | {row['agent']} | {row['current_rank']} | {row['kills']}/{row['deaths']}", axis=1)
        record_to_delete = st.selectbox("Select Record to Delete", record_options)
        if st.form_submit_button("Delete Record"):
            record_id = int(record_to_delete.split(" | ")[0])
            delete_match(record_id)
            st.success("Record deleted successfully!")

# Display match data and aggregated stats
match_data = fetch_matches()
if match_data:
    df = pd.DataFrame(match_data)
    df["K/D Ratio"] = df.apply(lambda row: calculate_kd_ratio(row["kills"], row["deaths"]), axis=1)
    st.subheader("Match Details")
    st.dataframe(df.drop(columns=["id"]))
    aggregated_df = aggregate_player_stats(match_data)
    if not aggregated_df.empty:
        st.subheader("Aggregated Player Statistics")
        st.dataframe(aggregated_df)
        st.subheader("Ranked Players by Avg ACS")
        ranked_df = rank_players(aggregated_df)
        st.dataframe(ranked_df)
else:
    st.info("No match data available. Please add match details.")