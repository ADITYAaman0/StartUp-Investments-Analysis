import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
DEFAULT_DATA_PATH = 'cleaned_investments!.csv'
ALTERNATE_DATA_PATH = './.devcontainer/cleaned_investments!.csv'
TOP_N = 10

# Configure styling
sns.set_theme(style="whitegrid")
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

def show_overview(df):
    """Display overview section"""
    st.subheader("Total Funding Overview")
    total = df['funding_total_usd'].sum()
    st.metric(label="Total Startup Funding (USD)", value=f"${total:,.0f}")
    st.dataframe(df.head(10))

def show_top_companies(df, n):
    """Display top funded companies"""
    top = df.groupby('name')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    top.plot(kind='barh', color=sns.color_palette('viridis', n), ax=ax)
    ax.set_title(f'Top {n} Funded Companies')
    st.pyplot(fig)

def show_funding_by_country(df, n):
    """Display funding by country"""
    by_country = df.groupby('country')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    by_country.plot(kind='barh', color=sns.color_palette('magma', n), ax=ax)
    ax.set_title(f'Top {n} Countries by Funding')
    st.pyplot(fig)

def show_active_markets(df, n):
    """Display active markets"""
    markets = df.groupby('primary_category')['name'].nunique().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    markets.plot(kind='barh', color=sns.color_palette('coolwarm', n), ax=ax)
    ax.set_title(f'Top {n} Active Markets')
    st.pyplot(fig)

def show_funding_trends(df):
    """Display funding trends"""
    data = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum()
    fig, ax = plt.subplots()
    data.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Funding Trends Over Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Funding (USD)')
    st.pyplot(fig)

def show_status_distribution(df):
    """Display status distribution"""
    if 'status' in df.columns:
        counts = df['status'].value_counts()
        fig, ax = plt.subplots()
        counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        ax.set_title('Startup Status Distribution')
        st.pyplot(fig)
    else:
        st.warning("'status' column is missing in data.")

def show_funding_vs_rounds(df):
    """Display funding vs rounds"""
    df2 = df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)]
    corr = df2['funding_rounds'].corr(df2['funding_total_usd'])
    fig, ax = plt.subplots()
    sns.scatterplot(data=df2, x='funding_rounds', y='funding_total_usd', ax=ax, alpha=0.6)
    ax.set_yscale('log')
    ax.set_title(f'Rounds vs Funding (corr={corr:.2f})')
    st.pyplot(fig)

def show_category_boxplot(df):
    """Display category boxplot"""
    top_categories = df['primary_category'].value_counts().nlargest(10).index
    filtered = df[df['primary_category'].isin(top_categories)]
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered, x='primary_category', y='funding_total_usd', ax=ax)
    ax.set_yscale('log')
    ax.set_title('Funding Distribution by Category (Top 10)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig)

def show_correlation_heatmap(df):
    """Display correlation heatmap"""
    corr = df[['funding_total_usd', 'funding_rounds', 'first_funding_year']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Correlation Matrix')
    st.pyplot(fig)

def main():
    """Main application function"""
    st.set_page_config(
        page_title="Startup Funding Insights",
        layout="wide",
        initial_sidebar_state="expanded"  # Ensures sidebar is always visible
    )
    
    st.title("📊 Startup Funding Insights Dashboard")

    # Load data
    df = try_load_data()
    if df is None or df.empty:
        st.error("Failed to load data.")
        return

    # Navigation sidebar - now properly structured and always visible
    st.sidebar.title("Navigation")
    sections = [
        "Overview",
        "Top Funded Companies",
        "Funding by Country",
        "Active Markets",
        "Funding Trends",
        "Startup Status",
        "Rounds vs Funding",
        "Category Boxplot",
        "Correlation Heatmap"
    ]
    choice = st.sidebar.radio("Select Section", sections)

    # Main content area
    if choice == "Overview":
        show_overview(df)
    elif choice == "Top Funded Companies":
        n = st.slider("Top N Companies", 5, 20, TOP_N)
        show_top_companies(df, n)
    elif choice == "Funding by Country":
        n = st.slider("Top N Countries", 5, 20, TOP_N)
        show_funding_by_country(df, n)
    elif choice == "Active Markets":
        n = st.slider("Top N Markets", 5, 20, TOP_N)
        show_active_markets(df, n)
    elif choice == "Funding Trends":
        show_funding_trends(df)
    elif choice == "Startup Status":
        show_status_distribution(df)
    elif choice == "Rounds vs Funding":
        show_funding_vs_rounds(df)
    elif choice == "Category Boxplot":
        show_category_boxplot(df)
    elif choice == "Correlation Heatmap":
        show_correlation_heatmap(df)

    # Debug information (collapsible)
    with st.sidebar.expander("Debug Info"):
        st.write(f"Data shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")
        st.write(f"Current directory: {os.getcwd()}")
        if st.checkbox("Show files in directory"):
            st.write(f"Files present: {os.listdir('.')}")

if __name__ == '__main__':
    main()