import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
DEFAULT_DATA_PATH = 'cleaned_investments.csv'
ALTERNATE_DATA_PATH = './.devcontainer/cleaned_investments.csv'
TOP_N = 10

# Configure styling - UPDATED STYLE NAME
sns.set_theme(style="whitegrid")  # Using seaborn's built-in theming
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 12

@st.cache_data
def load_data(path):
    """Load and preprocess the investment data"""
    try:
        df = pd.read_csv(path)
        
        # Data cleaning and type conversion
        numeric_cols = {
            'first_funding_year': 'int',
            'funding_total_usd': 'float',
            'funding_rounds': 'int'
        }
        
        for col, dtype in numeric_cols.items():
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(dtype)
        
        return df
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def try_load_data():
    """Attempt to load data from multiple possible locations"""
    possible_paths = [DEFAULT_DATA_PATH, ALTERNATE_DATA_PATH]
    
    for path in possible_paths:
        if os.path.exists(path):
            return load_data(path)
    
    st.warning(f"Data file not found at default locations. Tried:")
    for path in possible_paths:
        st.write(f"- {path}")
    return None

def display_dataframe_summary(df):
    """Show key metrics and sample data"""
    st.subheader("Total Funding Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Companies", len(df))
    with col2:
        st.metric("Total Funding (USD)", f"${df['funding_total_usd'].sum():,.0f}")
    
    with st.expander("📊 Dataset Summary"):
        st.dataframe(df.describe())
    
    with st.expander("👀 View Sample Data"):
        st.dataframe(df.head(10))

def create_visualizations(df):
    """Generate all visualization components"""
    st.sidebar.title("Visualization Options")
    n = st.sidebar.slider("Number of Top Items", 5, 20, TOP_N)
    
    tab1, tab2, tab3 = st.tabs(["Top Performers", "Trends", "Relationships"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Top {n} Funded Companies")
            top_companies = df.groupby('name')['funding_total_usd'].sum().nlargest(n)
            fig, ax = plt.subplots()
            top_companies.sort_values().plot(kind='barh', color='skyblue', ax=ax)
            st.pyplot(fig)
        
        with col2:
            st.subheader(f"Top {n} Countries by Funding")
            top_countries = df.groupby('country')['funding_total_usd'].sum().nlargest(n)
            fig, ax = plt.subplots()
            top_countries.sort_values().plot(kind='barh', color='salmon', ax=ax)
            st.pyplot(fig)
    
    with tab2:
        st.subheader("Funding Trends Over Time")
        trend_data = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum()
        fig, ax = plt.subplots()
        trend_data.plot(kind='line', marker='o', ax=ax, color='green')
        ax.set_xlabel('Year')
        ax.set_ylabel('Total Funding (USD)')
        st.pyplot(fig)
    
    with tab3:
        st.subheader("Funding vs Rounds")
        fig, ax = plt.subplots()
        sns.scatterplot(
            data=df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)],
            x='funding_rounds',
            y='funding_total_usd',
            alpha=0.6,
            ax=ax
        )
        ax.set_yscale('log')
        st.pyplot(fig)

def main():
    """Main application function"""
    st.set_page_config(page_title="Startup Funding Insights", layout="wide")
    st.title("📈 Startup Funding Insights Dashboard")
    
    # Attempt to load data
    df = try_load_data()
    
    # If data not found, show file uploader
    if df is None:
        uploaded_file = st.file_uploader("Upload your investment data (CSV)", type="csv")
        if uploaded_file:
            df = load_data(uploaded_file)
        else:
            st.info("Please upload a CSV file or ensure the data file is in the correct location.")
            return
    
    # Show debug info in sidebar
    with st.sidebar:
        st.subheader("Debug Info")
        st.write(f"Data shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")
        st.write(f"Current directory: {os.getcwd()}")
        if st.checkbox("Show files in directory"):
            st.write(f"Files present: {os.listdir('.')}")
    
    # Main app sections
    display_dataframe_summary(df)
    create_visualizations(df)

if __name__ == '__main__':
    main()
