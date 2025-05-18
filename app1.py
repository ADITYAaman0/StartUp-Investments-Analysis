import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

CLEANED_DATA_PATH = 'cleaned_investments.csv'
TOP_N_DEFAULT = 10

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    df['first_funding_year'] = pd.to_numeric(df.get('first_funding_year', pd.Series()), errors='coerce').fillna(0).astype(int)
    df['funding_total_usd'] = pd.to_numeric(df.get('funding_total_usd', pd.Series()), errors='coerce').fillna(0)
    df['funding_rounds'] = pd.to_numeric(df.get('funding_rounds', pd.Series()), errors='coerce').fillna(0).astype(int)
    return df

def plot_barh(data, title, xlabel, palette='viridis'):
    fig, ax = plt.subplots()
    data.sort_values().plot(kind='barh', ax=ax, color=sns.color_palette(palette, len(data)))
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    st.pyplot(fig)

def main():
    st.title("📊 Startup Investment Analysis")
    df = load_data(CLEANED_DATA_PATH)
    
    if df.empty:
        st.error("No data loaded.")
        return

    st.sidebar.header("Filter Options")
    top_n = st.sidebar.slider("Top N", 5, 30, TOP_N_DEFAULT)

    st.markdown("### 💵 Total Funding Overview")
    total_funding = df['funding_total_usd'].sum()
    unique_startups = df['name'].nunique()
    avg_funding = df['funding_total_usd'].mean()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Funding", f"${total_funding:,.0f}")
    col2.metric("Unique Startups", unique_startups)
    col3.metric("Avg. Funding", f"${avg_funding:,.0f}")

    with st.expander("📌 View Raw Data"):
        st.dataframe(df)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Top Funded Companies", "Funding by Country", "Active Markets",
        "Funding Trends", "Startup Status", "Funding Rounds vs Total"
    ])

    with tab1:
        st.subheader(f"Top {top_n} Funded Companies")
        top_companies = df.groupby('name')['funding_total_usd'].sum().nlargest(top_n)
        plot_barh(top_companies, f"Top {top_n} Funded Companies", "Funding (USD)")

    with tab2:
        st.subheader(f"Top {top_n} Countries by Funding")
        country_funding = df.groupby('country')['funding_total_usd'].sum().nlargest(top_n)
        plot_barh(country_funding, f"Top {top_n} Countries", "Funding (USD)", palette='magma')

    with tab3:
        st.subheader(f"Top {top_n} Active Markets")
        active_markets = df.groupby('primary_category')['name'].nunique().nlargest(top_n)
        plot_barh(active_markets, f"Top {top_n} Markets by Startup Count", "Number of Startups", palette='coolwarm')

    with tab4:
        st.subheader("Funding Trends Over the Years")
        yearly = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum()
        fig, ax = plt.subplots()
        yearly.plot(kind='line', marker='o', ax=ax)
        ax.set_title("Funding Over Years")
        ax.set_xlabel("Year")
        ax.set_ylabel("Funding (USD)")
        st.pyplot(fig)

    with tab5:
        st.subheader("Startup Status Distribution")
        if 'status' in df.columns:
            status_counts = df['status'].value_counts()
            fig, ax = plt.subplots()
            status_counts.plot(kind='pie', autopct='%1.1f%%', ax=ax)
            ax.set_ylabel('')
            ax.set_title("Startup Status")
            st.pyplot(fig)
        else:
            st.warning("Status column not available.")

    with tab6:
        st.subheader("Funding Rounds vs Total Funding")
        df2 = df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)]
        if df2.empty:
            st.warning("Not enough data for correlation.")
        else:
            corr = df2['funding_rounds'].corr(df2['funding_total_usd'])
            fig, ax = plt.subplots()
            sns.scatterplot(data=df2, x='funding_rounds', y='funding_total_usd', alpha=0.6, ax=ax)
            ax.set_yscale('log')
            ax.set_title(f'Funding Rounds vs Total Funding (Corr={corr:.2f})')
            st.pyplot(fig)

if __name__ == "__main__":
    main()
