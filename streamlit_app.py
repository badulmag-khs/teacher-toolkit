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

    st.title("🧰 Teacher Toolkit")
    st.write("Use the filters or the search bar below to find the perfect app.")

    # REQUEST 4: Clear Filters Logic
    def clear_filters():
        for key in st.session_state.keys():
            if key.startswith('skill_') or key.startswith('prod_') or key.startswith('res_'):
                st.session_state[key] = False
            elif key == 'search_keyword':
                st.session_state[key] = ""

    # 2. Sidebar Filters (Condensed Layout)
    
    # Combined the Search Header and Input into one element to save space
    search_keyword = st.sidebar.text_input("**Search by keyword (e.g., video, math, quiz):**", key="search_keyword")
    
    # Placed the Clear button immediately after the Search input
    st.sidebar.button("Clear All Filters", on_click=clear_filters)

    # Replaced st.header with bold markdown to reduce empty vertical space
    st.sidebar.markdown("<br>", unsafe_allow_html=True) # Adds just a tiny breath of space between the button and the lists
    st.sidebar.markdown("**What skill(s) do you want students to practice?**")
    skill_options = [
        "AI", "Collaboration", "Communication", "Critical Thinking", 
        "Creativity/Design", "Data Analysis", "Digital Literacy", 
        "Organization", "Planning", "Problem-Solving", "Reading", 
        "Recall (Interactive games)", "Research", "SEL", "Time Management", "Writing", "NA"
    ]
    selected_skills = [skill for skill in skill_options if st.sidebar.checkbox(skill, key=f"skill_{skill}")]

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("**What product(s) do you want students to create?**")
    product_options = ["Visual", "Auditory", "Writing", "Performance", "NA"]
    selected_products = [prod for prod in product_options if st.sidebar.checkbox(prod, key=f"prod_{prod}")]

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("**What resource type do you want?**")
    resource_type_options = sorted([rt for rt in df['Resource Type'].unique() if str(rt).strip() != ''])
    selected_resource_types = [rt for rt in resource_type_options if st.sidebar.checkbox(rt, key=f"res_{rt}")]

    # 3. Filtering Logic
    filtered_df = df.copy()

    if selected_skills or selected_products or selected_resource_types or search_keyword:
        def matches_criteria(row, skills, products, resource_types, keyword):
            row_skills = str(row['Skill(s)']).lower()
            row_products = str(row['Product(s)']).lower()
            row_res_type = str(row['Resource Type']).strip()
            
            # The row MUST contain ALL selected skills to show up
            skill_match = all(skill.lower() in row_skills for skill in skills) if skills else True
            
            # The row MUST contain ALL selected products to show up
            product_match = all(prod.lower() in row_products for prod in products) if products else True
            
            # The row can be ANY of the selected Resource Types
            res_type_match = any(row_res_type == rt for rt in resource_types) if resource_types else True
            
            # Keyword matching
            if keyword:
                keyword = keyword.lower()
                row_text = f"{str(row.get('App Name', ''))} {str(row.get('Description', ''))} {row_skills} {row_products} {row_res_type} {str(row.get('Resources', ''))}".lower()
                keyword_match = keyword in row_text
            else:
                keyword_match = True
            
            return skill_match and product_match and res_type_match and keyword_match

        mask = filtered_df.apply(lambda row: matches_criteria(row, selected_skills, selected_products, selected_resource_types, search_keyword), axis=1)
        filtered_df = filtered_df[mask]

    # 4. Display Results
    st.subheader(f"Found {len(filtered_df)} match(es)")

    for index, row in filtered_df.iterrows():
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
