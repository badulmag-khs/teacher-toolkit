import streamlit as st
import pandas as pd

# 1. Load and Clean the Data
@st.cache_data
def load_data():
    # Make sure this filename matches your uploaded file exactly
    file_name = 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv'
    df = pd.read_csv(file_name)
    
    # Clean column names (removes hidden spaces like 'Resource Type ')
    df.columns = df.columns.str.strip()
    
    # Fill empty cells with an empty string so the filter doesn't crash
    df = df.fillna('') 
    return df

try:
    df = load_data()

    st.title("🎓 Student Activity Matcher")
    st.write("Check the skills and products you want your students to practice/create to find the perfect app.")

    # 2. Sidebar Filters (Checklists)
    st.sidebar.header("What skill(s) do you want students to practice?")
    skill_options = [
        "AI", "Collaboration", "Communication", "Critical Thinking", 
        "Creativity/Design", "Data Analysis", "Digital Literacy", 
        "Organization", "Planning", "Problem-Solving", "Reading", 
        "Recall (Interactive games)", "Research", "SEL", "Time Management", "Writing", "NA"
    ]
    
    # Generate checkboxes and store the selected ones in a list
    selected_skills = [skill for skill in skill_options if st.sidebar.checkbox(skill, key=f"skill_{skill}")]

    st.sidebar.divider()

    st.sidebar.header("What product(s) do you want students to create?")
    product_options = ["Visual", "Auditory", "Writing", "Performance", "NA"]
    
    # Generate checkboxes and store the selected ones in a list
    selected_products = [prod for prod in product_options if st.sidebar.checkbox(prod, key=f"prod_{prod}")]

    # 3. Filtering Logic
    filtered_df = df.copy()

    if selected_skills or selected_products:
        def matches_criteria(row, skills, products):
            row_skills = str(row['Skill(s)']).lower()
            row_products = str(row['Product(s)']).lower()
            
            # Check if ANY selected skill is inside the row's skills string
            skill_match = any(skill.lower() in row_skills for skill in skills) if skills else True
            
            # Check if ANY selected product is inside the row's products string
            product_match = any(prod.lower() in row_products for prod in products) if products else True
            
            return skill_match and product_match

        # Apply the filter mask
        mask = filtered_df.apply(lambda row: matches_criteria(row, selected_skills, selected_products), axis=1)
        filtered_df = filtered_df[mask]

    # 4. Display Results
    st.subheader(f"Found {len(filtered_df)} match(es)")

    for index, row in filtered_df.iterrows():
        with st.expander(f"⭐ {row['App Name']}"):
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Skills:** {row['Skill(s)']}")
            st.write(f"**Products:** {row['Product(s)']}")
            
            # Using Resource Type based on the new CSV structure
            if 'Resource Type' in row:
                st.info(f"**Access Through / Type:** {row['Resource Type']}")
                
            # Render the link if there is one
            if row['Resources']:
                st.write(f"**Resources:** {row['Resources']}")

except FileNotFoundError:
    st.error("Could not find the file. Please ensure 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv' is in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
