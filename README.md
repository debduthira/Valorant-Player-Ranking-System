# Player Statistics Tracker

This Streamlit application allows users to track and analyze player performance in a competitive gaming environment. The app enables data entry for match details, visualization of match records, and generation of aggregated player statistics based on Average Combat Score (ACS), kill/death (K/D) ratio, and other key performance indicators.

## Features

1. **Add Match Details:** 
   - Enter player information, match outcomes, and stats for detailed tracking.
   - Select from pre-defined values for Map, Agent, and Rank.

2. **Delete Records:**
   - Remove any match records from the database as needed.

3. **Display Match Details:**
   - View all stored match details in a clean, tabular format.

4. **Aggregate Player Statistics:**
   - Aggregates data by player name to show averages for ACS, Econ Rating, total Kills, Deaths, Assists, and K/D Ratio.
   - Display ranked players based on Average ACS for quick comparisons.

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/debduthira/Valorant-Player-Ranking-System.git
   ```
2. Install required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```

## Database Structure

The application uses Supabase Postgres database with a single table, `matches`, containing the following fields:

- `id`: Unique identifier for each match record
- `player_name`: Name of the player
- `win_loss`: Match outcome (`Win` or `Loss`)
- `map_name`: Map name
- `agent`: Agent played by the player
- `current_rank`: Player’s current rank
- `acs`: Average Combat Score
- `econ_rating`: Economy rating
- `kills`: Number of kills
- `deaths`: Number of deaths
- `assists`: Number of assists

## Functionality

- **calculate_kd_ratio**: Calculates the K/D ratio (Kills divided by Deaths) for a match. 
- **add_match**: Adds match details to the database.
- **delete_match**: Removes a specified match from the database.
- **fetch_matches**: Retrieves all match records.
- **aggregate_player_stats**: Aggregates player data to calculate average ACS, total kills, deaths, assists, and average K/D ratio.
- **rank_players**: Sorts players by average ACS, displaying a leaderboard.

## Usage

1. Use the **Enter Match Details** form to add a new record.
2. View all records in the **Match Details** table.
3. **Delete Record** allows deletion of any selected record.
4. View **Aggregated Player Statistics** for overall performance metrics.
5. Check **Ranked Players by Avg ACS** to see player rankings based on performance.

## Dependencies

- `Streamlit`: Web framework for building interactive applications
- `Pandas`: Data manipulation and analysis

## Author

Debdut Hira (debduthira48@gmail.com)
