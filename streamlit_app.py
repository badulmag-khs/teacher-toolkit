import streamlit as st
import pandas as pd

# 1. Load and Clean the Data
@st.cache_data
def load_data():
    file_name = 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv'
    df = pd.read_csv(file_name)
    df.columns = df.columns.str.strip()
    df = df.fillna('') 
    return df

try:
    df = load_data()

    # REQUEST 1: New Title and Emoji
    st.title("🧰 Teacher Toolkit")
    st.write("Use the filters or the search bar below to find the perfect app.")

    # REQUEST 4: Clear Filters Logic
    # This function resets all the saved inputs back to their default state
    def clear_filters():
        for key in st.session_state.keys():
            if key.startswith('skill_') or key.startswith('prod_') or key.startswith('res_'):
                st.session_state[key] = False
            elif key == 'search_keyword':
                st.session_state[key] = ""

    # Place the clear button at the very top of the sidebar
    st.sidebar.button("Clear All Filters", on_click=clear_filters)
    st.sidebar.divider()

    # 2. Sidebar Filters
    st.sidebar.header("Search")
    # Note the added 'key' parameter so the Clear button knows how to reset it
    search_keyword = st.sidebar.text_input("Search by keyword (e.g., video, math, quiz):", key="search_keyword")

    st.sidebar.divider()

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

    st.sidebar.header("What resource type do you want?")
    resource_type_options = sorted([rt for rt in df['Resource Type'].unique() if str(rt).strip() != ''])
    selected_resource_types = [rt for rt in resource_type_options if st.sidebar.checkbox(rt, key=f"res_{rt}")]

    # 3. Filtering Logic
    filtered_df = df.copy()

    if selected_skills or selected_products or selected_resource_types or search_keyword:
        def matches_criteria(row, skills, products, resource_types, keyword):
            row_skills = str(row['Skill(s)']).lower()
            row_products = str(row['Product(s)']).lower()
            row_res_type = str(row['Resource Type']).strip()
            
            # REQUEST 2: Strict "AND" Filtering using `all()` instead of `any()`
            # The row MUST contain ALL selected skills to show up
            skill_match = all(skill.lower() in row_skills for skill in skills) if skills else True
            
            # The row MUST contain ALL selected products to show up
            product_match = all(prod.lower() in row_products for prod in products) if products else True
            
            # The row can be ANY of the selected Resource Types 
            # (since a single app is rarely multiple resource types in the sheet)
            res_type_match = any(row_res_type == rt for rt in resource_types) if resource_types else True
            
            # Keyword matching remains the same
            if keyword:
                keyword = keyword.lower()
                row_text = f"{str(row.get('App Name', ''))} {str(row.get('Description', ''))} {row_skills} {row_products} {row_res_type} {str(row.get('Resources', ''))}".lower()
                keyword_match = keyword in row_text
            else:
                keyword_match = True
            
            # Final Check: All activated categories must be a match
            return skill_match and product_match and res_type_match and keyword_match

        mask = filtered_df.apply(lambda row: matches_criteria(row, selected_skills, selected_products, selected_resource_types, search_keyword), axis=1)
        filtered_df = filtered_df[mask]

    # 4. Display Results
    st.subheader(f"Found {len(filtered_df)} match(es)")

    for index, row in filtered_df.iterrows():
        # REQUEST 3: Replaced the ⭐ with a 💡
        with st.expander(f"💡 {row['App Name']}"):
            st.write(f"**Description:** {row['Description']}")
            st.write(f"**Skills:** {row['Skill(s)']}")
            st.write(f"**Products:** {row['Product(s)']}")
            
            if 'Resource Type' in row and str(row['Resource Type']).strip() != '':
                st.info(f"**Resource Type:** {row['Resource Type']}")
                
            if 'Resources' in row and str(row['Resources']).strip() != '':
                st.markdown(f"**Resources:** {row['Resources']}")

except FileNotFoundError:
    st.error("Could not find the file. Please ensure 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv' is in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
