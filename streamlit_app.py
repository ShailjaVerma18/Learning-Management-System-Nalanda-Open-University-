import sqlite3
import streamlit as st

# Connect to the SQLite DB
conn = sqlite3.connect("db.sqlite3")   # this file is in your repo root
cur = conn.cursor()

# Fetch all programs
cur.execute("SELECT program FROM adminapp_program;")
programs = [row[0] for row in cur.fetchall()]

# UI
st.title("Nalanda Open University - LMS")
st.subheader("Available Programs")

# Show as bullet list
for p in programs:
    st.write(f"- {p}")
