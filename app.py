import streamlit as st
import pandas as pd
import numpy as np
from pybaseball import team_batting, team_pitching, cache
import matplotlib.pyplot as plt

# Enable caching to make loading faster
cache.enable()

# --- Title ---
st.title("⚾ Monte Carlo MLB Game Simulator")

# --- Instructions ---
st.write("Select two MLB teams and simulate thousands of games to see win probabilities.")

# --- Load latest MLB stats ---
year = 2024
batting_stats = team_batting(year)
pitching_stats = team_pitching(year)

# --- Get list of teams ---
teams_list = batting_stats['Team'].unique()

# --- Team selectors ---
teamA_name = st.selectbox("Select Team A", teams_list, index=0)
teamB_name = st.selectbox("Select Team B", teams_list, index=1)

# --- Function to estimate runs ---
def estimate_team_runs(team_bat, opp_pitch):
    bat_avg = team_bat["R"].values[0] / team_bat["G"].values[0]
    pitch_avg_allowed = opp_pitch["R"].values[0] / opp_pitch["G"].values[0]
    return (bat_avg + pitch_avg_allowed) / 2

# --- Run simulation ---
if st.button("Run Simulation"):
    teamA_bat = batting_stats[batting_stats["Team"] == teamA_name]
    teamB_bat = batting_stats[batting_stats["Team"] == teamB_name]
    teamA_pitch = pitching_stats[pitching_stats["Team"] == teamA_name]
    teamB_pitch = pitching_stats[pitching_stats["Team"] == teamB_name]

    teamA_avg_runs = estimate_team_runs(teamA_bat, teamB_pitch)
    teamB_avg_runs = estimate_team_runs(teamB_bat, teamA_pitch)

    sims = 10000
    teamA_scores = np.random.poisson(teamA_avg_runs, sims)
    teamB_scores = np.random.poisson(teamB_avg_runs, sims)

    teamA_wins = np.sum(teamA_scores > teamB_scores)
    teamB_wins = np.sum(teamB_scores > teamA_scores)
    ties = sims - teamA_wins - teamB_wins

    st.subheader("Results")
    st.write(f"**{teamA_name} win probability:** {teamA_wins/sims:.1%}")
    st.write(f"**{teamB_name} win probability:** {teamB_wins/sims:.1%}")
    st.write(f"**Tie probability:** {ties/sims:.1%}")

    st.write(f"**Average score:** {teamA_name} {teamA_avg_runs:.2f} - {teamB_avg_runs:.2f} {teamB_name}")

    # --- Plot score distribution ---
    fig, ax = plt.subplots()
    ax.hist(teamA_scores, bins=range(0, 16), alpha=0.5, label=teamA_name)
    ax.hist(teamB_scores, bins=range(0, 16), alpha=0.5, label=teamB_name)
    ax.set_xlabel("Runs Scored")
    ax.set_ylabel("Frequency")
    ax.set_title("Runs Distribution (Monte Carlo Simulation)")
    ax.legend()
    st.pyplot(fig)
