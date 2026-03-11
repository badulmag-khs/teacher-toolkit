import streamlit as st
import pandas as pd
import re

# 1. Load and Clean the Data
@st.cache_data
def load_data():
    file_name = 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv'
    df = pd.read_csv(file_name)
    # Clean column names (removes hidden spaces)
    df.columns = df.columns.str.strip()
    df = df.fillna('') 
    return df

# NEW: A robust function to find ALL markdown links, even if they have commas inside the text
def format_multiple_links(text):
    text = str(text).strip()
    if not text:
        return ""
    
    formatted_items = []
    
    # 1. Search for all instances of [Text](URL) or [Text] (URL) in the entire string
    # This ignores commas outside the brackets so it won't break your formatting
    matches = re.findall(r'\[(.*?)\]\s*\((.*?)\)', text)
    
    if matches:
        for text_part, url_part in matches:
            link_text = text_part.strip()
            link_url = url_part.strip()
            if link_text and link_url:
                formatted_items.append(f'<a href="{link_url}" target="_blank">{link_text}</a>')
    else:
        # Fallback: If no brackets are found, it checks for comma-separated raw http links
        items = [item.strip() for item in text.split(',')]
        for item in items:
            if item.startswith('http'):
                formatted_items.append(f'<a href="{item}" target="_blank">Visit Website</a>')
            elif item:
                formatted_items.append(item)

    # Output formatting
    if len(formatted_items) == 1:
        return formatted_items[0]
    elif len(formatted_items) > 1:
        bullets = "".join(f"<li>{item}</li>" for item in formatted_items)
        return f"<ul style='margin-top: 5px; margin-bottom: 0px; padding-left: 20px;'>{bullets}</ul>"
    else:
        return text

try:
    df = load_data()

    # --- CUSTOM CSS FOR COMPACT SIDEBAR & HEADERS ---
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] div[data-testid="stCheckbox"] {
                min-height: 1.5rem;
                padding-bottom: 0px !important;
                padding-top: 0px !important;
            }
            section[data-testid="stSidebar"] label {
                padding-top: 0px !important;
                padding-bottom: 0px !important;
            }
            .sidebar-header {
                font-size: 1.15rem;
                font-weight: 700;
                margin-top: 15px;
                margin-bottom: 5px;
                color: inherit;
            }
        </style>
    """, unsafe_allow_html=True)
    # ------------------------------------------------

    st.title("🧰 Teacher Toolkit")
    
    st.write("Use the filters to find the perfect app and/or resource to use with your students. If you have any questions or suggestions, please contact your ITS Team.")

    def clear_filters():
        for key in st.session_state.keys():
            if key.startswith('skill_') or key.startswith('prod_') or key.startswith('res_'):
                st.session_state[key] = False
            elif key == 'search_keyword':
                st.session_state[key] = ""

    # 2. Sidebar Filters
    st.sidebar.markdown('<div class="sidebar-header">Search by keyword:</div>', unsafe_allow_html=True)
    search_keyword = st.sidebar.text_input("Search", label_visibility="collapsed", placeholder="e.g., video, math, quiz", key="search_keyword")
    
    st.sidebar.button("Clear All Filters", on_click=clear_filters)

    st.sidebar.markdown('<div class="sidebar-header">What skill(s) do you want students to practice?</div>', unsafe_allow_html=True)
    skill_options = [
        "AI", "Collaboration", "Communication", "Critical Thinking", 
        "Creativity/Design", "Data Analysis", "Digital Literacy", 
        "Organization", "Planning", "Problem-Solving", "Reading", 
        "Recall (Interactive games)", "Research", "SEL", "Time Management", "Writing"
    ]
    selected_skills = [skill for skill in skill_options if st.sidebar.checkbox(skill, key=f"skill_{skill}")]

    st.sidebar.markdown('<div class="sidebar-header">What product(s) do you want students to create?</div>', unsafe_allow_html=True)
    product_options = ["Visual", "Auditory", "Writing", "Performance"]
    selected_products = [prod for prod in product_options if st.sidebar.checkbox(prod, key=f"prod_{prod}")]

    st.sidebar.markdown('<div class="sidebar-header">What resource type do you want?</div>', unsafe_allow_html=True)
    resource_type_options = sorted([rt for rt in df['Resource Type'].unique() if str(rt).strip() != ''])
    selected_resource_types = [rt for rt in resource_type_options if st.sidebar.checkbox(rt, key=f"res_{rt}")]

    # 3. Filtering Logic
    filtered_df = df.copy()

    if selected_skills or selected_products or selected_resource_types or search_keyword:
        def matches_criteria(row, skills, products, resource_types, keyword):
            row_skills = str(row['Skill(s)']).lower()
            row_products = str(row['Product(s)']).lower()
            row_res_type = str(row['Resource Type']).strip()
            
            skill_match = all(skill.lower() in row_skills for skill in skills) if skills else True
            product_match = all(prod.lower() in row_products for prod in products) if products else True
            res_type_match = any(row_res_type == rt for rt in resource_types) if resource_types else True
            
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
            
            st.info(f"**Description:** {row['Description']}")
            
            st.write(f"**Skills:** {row['Skill(s)']}")
            st.write(f"**Products:** {row['Product(s)']}")
            
            if 'Resource Type' in row and str(row['Resource Type']).strip() != '':
                st.write(f"**Resource Type:** {row['Resource Type']}")
                
            # Formatting the Website URL
            url_col = 'Website URL (if applicable):'
            if url_col in row and str(row[url_col]).strip() != '':
                html_url = format_multiple_links(row[url_col])
                st.markdown(f"**Website URL:** {html_url}", unsafe_allow_html=True)
                
            # Formatting the Resources
            if 'Resources' in row and str(row['Resources']).strip() != '':
                html_resources = format_multiple_links(row['Resources'])
                st.markdown(f"**Resources:** {html_resources}", unsafe_allow_html=True)

# Important Note: Indentation below is exactly 0 spaces for except, and exactly 4 spaces for st.error
except FileNotFoundError:
    st.error("Could not find the file. Please ensure 'Apps and Resources - KHS Instructional Tech Central - Apps and Resources.csv' is in the same folder as this script.")
except Exception as e:
    st.error(f"An error occurred: {e}")
