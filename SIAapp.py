import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
CLEANED_DATA_PATH = 'cleaned_investments!.csv'
TOP_N = 10

# Styling
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 12

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['first_funding_year'] = pd.to_numeric(df.get('first_funding_year'), errors='coerce').fillna(0).astype(int)
    df['funding_total_usd'] = pd.to_numeric(df.get('funding_total_usd'), errors='coerce').fillna(0)
    df['funding_rounds'] = pd.to_numeric(df.get('funding_rounds'), errors='coerce').fillna(0).astype(int)
    return df

# Visualization functions
def top_funded_companies(df, n):
    top = df.groupby('name')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    top.plot(kind='barh', color=sns.color_palette('viridis', n), ax=ax)
    ax.set_title(f'Top {n} Funded Companies')
    st.pyplot(fig)

def funding_by_country(df, n):
    by_country = df.groupby('country')['funding_total_usd'].sum().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    by_country.plot(kind='barh', color=sns.color_palette('magma', n), ax=ax)
    ax.set_title(f'Top {n} Countries by Funding')
    st.pyplot(fig)

def most_active_markets(df, n):
    markets = df.groupby('primary_category')['name'].nunique().nlargest(n).sort_values()
    fig, ax = plt.subplots()
    markets.plot(kind='barh', color=sns.color_palette('coolwarm', n), ax=ax)
    ax.set_title(f'Top {n} Active Markets')
    st.pyplot(fig)

def funding_trends(df):
    data = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum()
    fig, ax = plt.subplots()
    data.plot(kind='line', marker='o', ax=ax)
    ax.set_title('Funding Trends Over Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Funding (USD)')
    st.pyplot(fig)

def status_distribution(df):
    counts = df['status'].value_counts()
    fig, ax = plt.subplots()
    counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
    ax.set_ylabel('')
    ax.set_title('Startup Status Distribution')
    st.pyplot(fig)

def funding_vs_rounds(df):
    df2 = df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)]
    corr = df2['funding_rounds'].corr(df2['funding_total_usd'])
    fig, ax = plt.subplots()
    sns.scatterplot(data=df2, x='funding_rounds', y='funding_total_usd', ax=ax, alpha=0.6)
    ax.set_yscale('log')
    ax.set_title(f'Rounds vs Funding (corr={corr:.2f})')
    st.pyplot(fig)

def category_funding_boxplot(df):
    top_categories = df['primary_category'].value_counts().nlargest(10).index
    filtered = df[df['primary_category'].isin(top_categories)]
    fig, ax = plt.subplots()
    sns.boxplot(data=filtered, x='primary_category', y='funding_total_usd', ax=ax)
    ax.set_yscale('log')
    ax.set_title('Funding Distribution by Category (Top 10)')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    st.pyplot(fig)

def correlation_heatmap(df):
    corr = df[['funding_total_usd', 'funding_rounds', 'first_funding_year']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
    ax.set_title('Correlation Matrix')
    st.pyplot(fig)

# Main App
def main():
    st.title("📊 Startup Funding Insights Dashboard")

    df = load_data(CLEANED_DATA_PATH)
    if df is None or df.empty:
        st.error("Failed to load data.")
        return

    # Sidebar options
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

    if choice == "Overview":
        st.subheader("Total Funding Overview")
        total = df['funding_total_usd'].sum()
        st.metric(label="Total Startup Funding (USD)", value=f"${total:,.0f}")
        st.dataframe(df.head(10))

    elif choice == "Top Funded Companies":
        n = st.slider("Top N Companies", 5, 20, TOP_N)
        top_funded_companies(df, n)

    elif choice == "Funding by Country":
        n = st.slider("Top N Countries", 5, 20, TOP_N)
        funding_by_country(df, n)

    elif choice == "Active Markets":
        n = st.slider("Top N Markets", 5, 20, TOP_N)
        most_active_markets(df, n)

    elif choice == "Funding Trends":
        funding_trends(df)

    elif choice == "Startup Status":
        if 'status' in df.columns:
            status_distribution(df)
        else:
            st.warning("'status' column is missing in data.")

    elif choice == "Rounds vs Funding":
        funding_vs_rounds(df)

    elif choice == "Category Boxplot":
        category_funding_boxplot(df)

    elif choice == "Correlation Heatmap":
        correlation_heatmap(df)

    with st.expander("📄 Show Raw Data"):
        st.dataframe(df)
if __name__ == '__main__':
    main()
