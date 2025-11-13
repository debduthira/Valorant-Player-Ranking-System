import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# --- Streamlit Page Setup ---
st.set_page_config(
    page_title="Valorant Player Statistics Tracker",
    page_icon="https://img.icons8.com/?size=100&id=aUZxT3Erwill&format=png&color=000000",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Environment Variables ---
load_dotenv()

# Option 1: Load from .env (recommended)
DATABASE_URL = os.getenv("DATABASE_URL")

# --- Database Connection ---
def get_connection():
    return psycopg2.connect(
        DATABASE_URL,
        sslmode="require",
        cursor_factory=RealDictCursor
    )

# --- Helper Functions ---
def calculate_kd_ratio(kills, deaths):
    return kills if deaths == 0 else kills / deaths

def add_match(player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists):
    query = """
        INSERT INTO matches (player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (player_name, win_loss, map_name, agent, current_rank, acs, econ_rating, kills, deaths, assists))
            conn.commit()

def delete_match(record_id):
    query = "DELETE FROM matches WHERE id = %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (record_id,))
            conn.commit()

def fetch_matches():
    query = "SELECT * FROM matches ORDER BY id DESC"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

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

def rank_players(aggregated_df):
    ranked_df = aggregated_df.sort_values(by="avg_acs", ascending=False).reset_index(drop=True)
    ranked_df.index += 1
    return ranked_df

# --- Streamlit Layout ---

st.title("Player Statistics Tracker")

# Add Match Form
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
        st.success("✅ Match details added successfully!")

# Delete Record Form
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
            st.success("🗑️ Record deleted successfully!")

# Display Data
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
