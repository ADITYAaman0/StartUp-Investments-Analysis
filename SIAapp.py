import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import requests
from streamlit_lottie import st_lottie

# Constants
data_paths = ['cleaned_investments!.csv', './.devcontainer/cleaned_investments!.csv']
TOP_N = 10

@st.cache_data
def load_data():
    for path in data_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            for col, dtype in {'first_funding_year': int, 'funding_total_usd': float, 'funding_rounds': int}.items():
                if col in df:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(dtype)
            return df
    st.error('Data file not found.')
    return pd.DataFrame()


def load_lottieurl(url: str):
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None


def show_overview(df):
    total = df['funding_total_usd'].sum()
    st.metric('Total Funding (USD)', f"${total:,.0f}")
    st.dataframe(df.head(10))


def show_top_companies(df, n):
    data = df.groupby('name')['funding_total_usd'].sum().reset_index()
    top = data.nlargest(n, 'funding_total_usd')
    fig = px.bar(top, x='funding_total_usd', y='name', orientation='h', title=f'Top {n} Companies', animation_frame=None)
    st.plotly_chart(fig, use_container_width=True)


def show_funding_by_country(df, n):
    data = df.groupby('country')['funding_total_usd'].sum().reset_index()
    top = data.nlargest(n, 'funding_total_usd')
    fig = px.bar(top, x='funding_total_usd', y='country', orientation='h', title=f'Top {n} Countries')
    st.plotly_chart(fig, use_container_width=True)


def show_active_markets(df, n):
    data = df.groupby('primary_category')['name'].nunique().reset_index(name='count')
    top = data.nlargest(n, 'count')
    fig = px.bar(top, x='count', y='primary_category', orientation='h', title=f'Top {n} Markets')
    st.plotly_chart(fig, use_container_width=True)


def show_funding_trends(df):
    data = df[df['first_funding_year'] > 1980].groupby('first_funding_year')['funding_total_usd'].sum().reset_index()
    fig = px.bar(data, x='first_funding_year', y='funding_total_usd', animation_frame='first_funding_year', range_y=[0, data['funding_total_usd'].max()], title='Funding Trends Over Years')
    st.plotly_chart(fig, use_container_width=True)


def show_status_distribution(df):
    if 'status' in df:
        counts = df['status'].value_counts().reset_index()
        fig = px.pie(counts, values='status', names='index', title='Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("'status' column missing")


def show_rounds_vs_funding(df):
    df2 = df[(df['funding_rounds'] > 0) & (df['funding_total_usd'] > 0)]
    corr = df2['funding_rounds'].corr(df2['funding_total_usd'])
    fig = px.scatter(df2, x='funding_rounds', y='funding_total_usd', log_y=True, title=f'Rounds vs Funding (corr={corr:.2f})')
    st.plotly_chart(fig, use_container_width=True)


def show_category_boxplot(df):
    top_cats = df['primary_category'].value_counts().nlargest(10).index
    filt = df[df['primary_category'].isin(top_cats)]
    fig = px.box(filt, x='primary_category', y='funding_total_usd', log_y=True, title='Funding by Category')
    st.plotly_chart(fig, use_container_width=True)


def show_correlation(df):
    corr = df[['funding_total_usd','funding_rounds','first_funding_year']].corr()
    fig = px.imshow(corr, text_auto=True, title='Correlation Matrix')
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title='Startup Funding Insights', layout='wide')
    # Lottie animation header
    lottie_url = 'https://assets10.lottiefiles.com/packages/lf20_touohxv0.json'
    lottie_json = load_lottieurl(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=200, key='startup_animation')

    # Loading spinner and progress
    with st.spinner('Loading data...'):
        df = load_data()
        time.sleep(1)
    progress = st.progress(0)
    for i in range(1, 101):
        progress.progress(i)
        time.sleep(0.005)

    if df.empty:
        return

    sections = [
        'Overview','Top Funded Companies','Funding by Country','Active Markets',
        'Funding Trends','Status Distribution','Rounds vs Funding','Category Boxplot','Correlation'
    ]
    choice = st.sidebar.radio('Select Section', sections)

    if choice == 'Overview': show_overview(df)
    elif choice == 'Top Funded Companies': show_top_companies(df, st.sidebar.slider('N Companies',5,20,TOP_N))
    elif choice == 'Funding by Country': show_funding_by_country(df, st.sidebar.slider('N Countries',5,20,TOP_N))
    elif choice == 'Active Markets': show_active_markets(df, st.sidebar.slider('N Markets',5,20,TOP_N))
    elif choice == 'Funding Trends': show_funding_trends(df)
    elif choice == 'Status Distribution': show_status_distribution(df)
    elif choice == 'Rounds vs Funding': show_rounds_vs_funding(df)
    elif choice == 'Category Boxplot': show_category_boxplot(df)
    elif choice == 'Correlation': show_correlation(df)

if __name__ == '__main__':
    main()
