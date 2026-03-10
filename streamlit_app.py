import streamlit as st
import pandas as pd

# 1. Load and Clean the Data
@st.cache_data
def load_data():
    # Make sure this filename matches your uploaded file exactly
    file_name = 'your_spreadsheet.csv'
    df = pd.read_csv(file_name)
    
    # Clean column names (removes hidden spaces like 'Resource Type ')
    df.columns = df.columns.str.strip()
    
    # Fill empty cells with an empty string so the filter doesn't crash
    df = df.fillna('') 
    return df

try:
    df = load_data()

    st.title("🎓 Student Activity Matcher")
    st.write("Check the skills, products, and resource types you want to find the perfect app.")

    # 2. Sidebar Filters (Checklists)
    
    # NEW: Keyword Search Feature
    st.sidebar.header("Search")
    search_keyword = st.sidebar.text_input("Search by keyword (e.g., video, math, quiz):")
    
    st.sidebar.header("What skill(s) do you want students to practice?")
    skill_options = [
        "AI", "Collaboration", "Communication", "Critical Thinking", 
        "Creativity/Design", "Data Analysis", "Digital Literacy", 
        "Organization", "Planning", "Problem-Solving", "Reading", 
        "Recall (Interactive games)", "Research", "SEL", "Time Management", "Writing", "NA"
    ]
    selected_skills = [skill for skill in skill_options if st.sidebar.checkbox(skill, key=f"skill_{skill}")]

    st.sidebar.divider()

    st.sidebar.header("What product(s) do you want students to create?")
    product_options = ["Visual", "Auditory", "Writing", "Performance", "NA"]
    selected_products = [prod for prod in product_options if st.sidebar.checkbox(prod, key=f"prod_{prod}")]

    st.sidebar.divider()

    # NEW: Dynamic Resource Type Filter
    st.sidebar.header("What resource type do you want?")
    
    # This automatically finds all unique resource types in your CSV (ignoring blank cells)
    resource_type_options = sorted([rt for rt in df['Resource Type'].unique() if str(rt).strip() != ''])
    
    # Generate checkboxes for each unique resource type
    selected_resource_types = [rt for rt in resource_type_options if st.sidebar.checkbox(rt, key=f"res_{rt}")]

    # 3. Filtering Logic
    filtered_df = df.copy()

    if selected_skills or selected_products or selected_resource_types or search_keyword:
        def matches_criteria(row, skills, products, resource_types, keyword):
            row_skills = str(row['Skill(s)']).lower()
            row_products = str(row['Product(s)']).lower()
            row_res_type = str(row['Resource Type']).strip()
            
            # Check if ANY selected skill is inside the row's skills string
            skill_match = any(skill.lower() in row_skills for skill in skills) if skills else True
            
            # Check if ANY selected product is inside the row's products string
            product_match = any(prod.lower() in row_products for prod in products) if products else True
            
            # Check if the row's resource type matches ANY of the selected resource types
            res_type_match = (row_res_type in resource_types) if resource_types else True

            # 2. Check Keyword Search (Scans across multiple columns)
            if keyword:
                keyword = keyword.lower()
                # Combine relevant columns into one block of text to search through
                row_text = f"{str(row.get('App Name', ''))} {str(row.get('Description', ''))} {row_skills} {row_products} {row_res_type} {str(row.get('Resources', ''))}".lower()
                keyword_match = keyword in row_text
            else:
                keyword_match = True
                
            # A row only shows up if it matches ALL active criteria
            return skill_match and product_match and res_type_match

        # Apply the filter mask
        mask = filtered_df.apply(lambda row: matches_criteria(row, selected_skills, selected_products, selected_resource_types), axis=1)
        filtered_df = filtered_df[mask]

    # 4. Display Results
    st.subheader(f"Found {len(filtered_df)} match(es)")

    for index, row in filtered_df.iterrows():
        with st.expander(f"⭐ {row['App Name']}"):
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Skills:** {row['Skill(s)']}")
            st.write(f"**Products:** {row['Product(s)']}")
            
            if 'Resource Type' in row and str(row['Resource Type']).strip() != '':
                st.info(f"**Resource Type:** {row['Resource Type']}")
                
            # NEW: Displaying the Resources column
            if 'Resources' in row and str(row['Resources']).strip() != '':
                # Using st.markdown ensures that if you put URLs or markdown links in your CSV, they become clickable.
                st.markdown(f"**Resources:** {row['Resources']}")

except FileNotFoundError:
    st.error("Could not find the file. Please ensure 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv' is in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
