import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

DEFAULT_DATA_PATH = 'cleaned_investments!.csv'
ALTERNATE_DATA_PATH = './.devcontainer/cleaned_investments!.csv'
TOP_N = 10

sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 12

@st.cache_data
def load_data(path):
    try:
        df = pd.read_csv(path)
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
    for path in [DEFAULT_DATA_PATH, ALTERNATE_DATA_PATH]:
        if os.path.exists(path):
            return load_data(path)
    st.warning("Data file not found at default locations.")
    return None

def show_overview(df):
    st.subheader("Total Funding Overview")
    total = df['funding_total_usd'].sum()
    st.metric(label="Total Startup Funding (USD)", value=f"${total:,.0f}")
    st.dataframe(df.head(10))

def show_top_companies(df, n):
    top = df.groupby('name')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    top.plot(kind='barh', color=sns.color_palette('tab10', n), ax=ax)
    ax.set_title(f'Top {n} Funded Companies')
    st.pyplot(fig)

def show_funding_by_country(df, n):
    by_country = df.groupby('country')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    by_country.plot(kind='barh', color=sns.color_palette('pastel', n), ax=ax)
    ax.set_title(f'Top {n} Countries by Funding')
    st.pyplot(fig)

def show_active_markets(df, n):
    markets = df.groupby('primary_category')['name'].nunique().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    markets.plot(kind='barh', color=sns.color_palette('Set2', n), ax=ax)
    ax.set_title(f'Top {n} Active Markets')
    st.pyplot(fig)

def show_funding_trends(df):
    data = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum()
    fig, ax = plt.subplots()
    data.plot(kind='line', marker='o', color='darkorange', ax=ax)
    ax.set_title('Funding Trends Over Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Funding (USD)')
    st.pyplot(fig)

def show_status_distribution(df):
    if 'status' in df.columns:
        counts = df['status'].value_counts()
        fig, ax = plt.subplots()
        counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=sns.color_palette('Set3'), ax=ax)
        ax.set_ylabel('')
        ax.set_title('Startup Status Distribution')
        st.pyplot(fig)
    else:
        st.warning("'status' column is missing in data.")

def show_funding_vs_rounds(df):
    df2 = df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)]
    corr = df2['funding_rounds'].corr(df2['funding_total_usd'])
    fig, ax = plt.subplots()
    sns.scatterplot(data=df2, x='funding_rounds', y='funding_total_usd', ax=ax, alpha=0.6, hue='funding_rounds', palette='cool')
    ax.set_yscale('log')
    ax.set_title(f'Rounds vs Funding (corr={corr:.2f})')
    st.pyplot(fig)

def show_category_boxplot(df):
    top_categories = df['primary_category'].value_counts().nlargest(10).index
    filtered = df[df['primary_category'].isin(top_categories)]
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered, x='primary_category', y='funding_total_usd', palette='Spectral', ax=ax)
    ax.set_yscale('log')
    ax.set_title('Funding Distribution by Category (Top 10)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig)

def show_correlation_heatmap(df):
    corr = df[['funding_total_usd', 'funding_rounds', 'first_funding_year']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Correlation Matrix')
    st.pyplot(fig)

def main():
    st.set_page_config(
        page_title="Startup Funding Insights",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Startup Funding Insights Dashboard")
    df = try_load_data()

    if df is None or df.empty:
        st.error("Failed to load data.")
        return

    st.sidebar.title("Navigation")
    sections = [
        "Overview", "Top Funded Companies", "Funding by Country", "Active Markets",
        "Funding Trends", "Startup Status", "Rounds vs Funding", "Category Boxplot", "Correlation Heatmap"
    ]
    choice = st.sidebar.radio("Select Section", sections)

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

    with st.sidebar.expander("Debug Info"):
        st.write(f"Data shape: {df.shape}")
        st.write(f"Columns: {list(df.columns)}")
        st.write(f"Current directory: {os.getcwd()}")
        if st.checkbox("Show files in directory"):
            st.write(f"Files present: {os.listdir('.')}")

if __name__ == '__main__':
    main()
