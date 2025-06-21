# app.py

import streamlit as st
import sqlite3

# --- DATABASE FUNCTIONS (CRUD) ---

# Function to create a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('recipes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to initialize the database table
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# C - Create a new recipe
def add_recipe(title, ingredients, instructions):
    conn = get_db_connection()
    conn.execute('INSERT INTO recipes (title, ingredients, instructions) VALUES (?, ?, ?)',
                 (title, ingredients, instructions))
    conn.commit()
    conn.close()

# R - Read all recipes
def view_all_recipes():
    conn = get_db_connection()
    recipes = conn.execute('SELECT * FROM recipes').fetchall()
    conn.close()
    return recipes

# U - Update a recipe
def update_recipe(id, title, ingredients, instructions):
    conn = get_db_connection()
    conn.execute('UPDATE recipes SET title = ?, ingredients = ?, instructions = ? WHERE id = ?',
                 (title, ingredients, instructions, id))
    conn.commit()
    conn.close()

# D - Delete a recipe
def delete_recipe(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM recipes WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# --- STREAMLIT APP ---

# Initialize the database
init_db()

st.title("My Recipe Book")

# Sidebar for navigation
menu = ["Add Recipe", "View Recipes", "Edit/Delete Recipe"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Recipe":
    st.subheader("Add a New Recipe")

    with st.form("recipe_form"):
        title = st.text_input("Recipe Title")
        ingredients = st.text_area("Ingredients (one per line)")
        instructions = st.text_area("Instructions")
        
        submitted = st.form_submit_button("Add Recipe")
        if submitted:
            if title and ingredients and instructions:
                add_recipe(title, ingredients, instructions)
                st.success(f"Recipe '{title}' added successfully!")
            else:
                st.warning("Please fill in all fields.")

elif choice == "View Recipes":
    st.subheader("All Your Recipes")
    recipes = view_all_recipes()
    
    if not recipes:
        st.info("No recipes found. Add one from the 'Add Recipe' menu!")
    else:
        for recipe in recipes:
            with st.expander(f"{recipe['title']}"):
                st.markdown("**Ingredients:**")
                st.text(recipe['ingredients'])
                st.markdown("**Instructions:**")
                st.text(recipe['instructions'])

elif choice == "Edit/Delete Recipe":
    st.subheader("Edit or Delete a Recipe")
    recipes = view_all_recipes()
    
    if not recipes:
        st.info("No recipes to edit or delete.")
    else:
        # Create a list of recipe titles for the selectbox
        recipe_titles = [recipe['title'] for recipe in recipes]
        selected_title = st.selectbox("Select a recipe to edit/delete", recipe_titles)
        
        # Find the full recipe data based on the selected title
        selected_recipe = None
        for recipe in recipes:
            if recipe['title'] == selected_title:
                selected_recipe = recipe
                break

        if selected_recipe:
            with st.form("edit_form"):
                st.write(f"Editing: {selected_recipe['title']}")
                new_title = st.text_input("Recipe Title", value=selected_recipe['title'])
                new_ingredients = st.text_area("Ingredients", value=selected_recipe['ingredients'])
                new_instructions = st.text_area("Instructions", value=selected_recipe['instructions'])
                
                col1, col2 = st.columns(2)
                with col1:
                    updated = st.form_submit_button("Update Recipe")
                with col2:
                    deleted = st.form_submit_button("Delete Recipe")

                if updated:
                    update_recipe(selected_recipe['id'], new_title, new_ingredients, new_instructions)
                    st.success(f"Recipe '{new_title}' updated successfully!")
                    st.info("The page will refresh to show changes.")
                    # A small delay to let the user read the message
                    import time
                    time.sleep(1)
                    st.rerun() # This command refreshes the page

                if deleted:
                    delete_recipe(selected_recipe['id'])
                    st.warning(f"Recipe '{selected_recipe['title']}' has been deleted.")
                    st.info("The page will refresh to show changes.")
                    import time
                    time.sleep(1)
                    st.rerun()