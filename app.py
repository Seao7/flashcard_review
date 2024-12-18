import streamlit as st
import sqlite3
import json

# ---------------------------- Section 1: Application Title and Welcome Message ----------------------------

st.title("Flashcard Review")
st.write("Welcome to the flashcard review system!")

# ---------------------------- Section 2: Load and Display Flashcards ----------------------------

# Function to load flashcards from a JSON file
def load_flashcards(file_path):
    """Load flashcards from a JSON file."""
    with open(file_path, 'r') as file:
        return json.load(file)

# Load the flashcards
flashcards = load_flashcards('flashcards.json')

# Function to display a flashcard
def display_flashcard(flashcard):
    """
    Display the current flashcard.
    Renders the question, answer, and additional metadata with markdown support.
    """
    st.subheader(f"Question: {flashcard['front']}")
    st.markdown(f"**Answer:** {flashcard['back']}", unsafe_allow_html=True)
    
    # Display additional metadata
    st.markdown(f"**Topic:** {flashcard['topic']}")
    st.markdown(f"**Course:** {flashcard['course']}")
    st.markdown(f"**Type:** {flashcard['type']}")

# Get the current flashcard index from session state
flashcard_index = st.session_state.get('flashcard_index', 0)

# Navigation buttons to go through flashcards
if st.button("Previous"):
    flashcard_index = max(0, flashcard_index - 1)  # Prevent going below the first flashcard
if st.button("Next"):
    flashcard_index = min(len(flashcards) - 1, flashcard_index + 1)  # Prevent going beyond the last flashcard

# Save the updated index in session state
st.session_state['flashcard_index'] = flashcard_index

# Display the current flashcard
current_flashcard = flashcards[flashcard_index]
display_flashcard(current_flashcard)

# ---------------------------- Section 3: Initialize Database ----------------------------

def init_db():
    """
    Initialize the SQLite database.
    Creates a table for storing votes with default values if it doesn't already exist.
    """
    conn = sqlite3.connect('flashcards.db')  # Connect to SQLite database
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            flashcard_id INTEGER PRIMARY KEY,
            looks_good INTEGER DEFAULT 0,
            needs_improvement INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

# ---------------------------- Section 4: Voting Logic ----------------------------

def update_votes(flashcard_id, vote_type):
    """
    Update the votes for a given flashcard.
    If the flashcard doesn't exist in the database, insert it with default values.
    Increment the appropriate vote count based on user input.
    """
    conn = sqlite3.connect('flashcards.db')  # Connect to SQLite database
    cursor = conn.cursor()
    cursor.execute(f'''
        INSERT INTO votes (flashcard_id, {vote_type}) 
        VALUES (?, 1)
        ON CONFLICT(flashcard_id) 
        DO UPDATE SET {vote_type} = {vote_type} + 1
    ''', (flashcard_id,))
    conn.commit()
    conn.close()

# Buttons for voting
st.write("Rate this flashcard:")
if st.button("Looks Good 👍"):
    update_votes(current_flashcard['id'], 'looks_good')
if st.button("Needs Improvement 👎"):
    update_votes(current_flashcard['id'], 'needs_improvement')

# ---------------------------- Section 5: Fetch and Display Votes ----------------------------

def fetch_votes(flashcard_id):
    """
    Fetch the vote counts for a given flashcard.
    Returns the counts of 'looks_good' and 'needs_improvement'.
    """
    conn = sqlite3.connect('flashcards.db')  # Connect to SQLite database
    cursor = conn.cursor()
    cursor.execute('''
        SELECT looks_good, needs_improvement 
        FROM votes WHERE flashcard_id = ?
    ''', (flashcard_id,))
    votes = cursor.fetchone()
    conn.close()
    return votes if votes else (0, 0)  # Return default values if no record exists

# Fetch and display vote counts for the current flashcard
looks_good, needs_improvement = fetch_votes(current_flashcard['id'])
st.write(f"👍 Looks Good: {looks_good}")
st.write(f"👎 Needs Improvement: {needs_improvement}")
