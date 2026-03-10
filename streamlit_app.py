import streamlit as st
import pandas as pd

# 1. Load the Data
# Replace 'your_spreadsheet.csv' with your actual filename (CSV is best)
@st.cache_data
def load_data():
    df = pd.read_csv('your_spreadsheet.csv')
    return df

try:
    df = load_data()

    st.title("🎓 Student Activity Matcher")
    st.write("Find the perfect app based on the skills and products you want for your students.")

    # 2. Sidebar Filters (The Questions)
    st.sidebar.header("Filter Criteria")

    skill_options = [
        "AI", "Collaboration", "Communication", "Critical Thinking", 
        "Creativity/Design", "Data Analysis", "Digital Literacy", 
        "Organization", "Planning", "Problem-Solving", "Reading", 
        "Recall (Interactive games)", "Research", "SEL", "Time Management", "Writing", "NA"
    ]
    
    product_options = ["visual", "auditory", "writing", "performance", "NA"]

    selected_skills = st.sidebar.multiselect("What skill(s) do you want students to practice?", skill_options)
    selected_products = st.sidebar.multiselect("What product(s) do you want students to create?", product_options)

    # 3. Filtering Logic
    if selected_skills and selected_products:
        # We look for rows where the Skills column contains ANY of the selected skills
        # and the Products column contains ANY of the selected products
        mask = df.apply(lambda row: 
            any(skill in str(row['Skills']) for skill in selected_skills) and
            any(prod in str(row['Products']) for prod in selected_products), axis=1)
        
        filtered_df = df[mask]
    else:
        filtered_df = df

    # 4. Display Results in a User-Friendly Format
    st.subheader(f"Found {len(filtered_df)} matches")

    for index, row in filtered_df.iterrows():
        with st.expander(f"⭐ {row['App Name']}"):
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Skills:** {row['Skills']}")
            st.write(f"**Products:** {row['Products']}")
            st.info(f"**Access Through:** {row['Access Through']}")
            st.write(f"**Resources:** [Click here]({row['Resources']})")

except FileNotFoundError:
    st.error("Please ensure your spreadsheet is in the same folder as this script and named correctly.")
