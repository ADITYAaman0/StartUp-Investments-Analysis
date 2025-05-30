# StartUp-Investments-Analysis
The pipeline consists of three major Python scripts:

1. Data Cleaning Script – investment anylsis report data cleaningg.py
This script loads the raw data (investments_VC.csv), cleans it, and saves a cleaned version as cleaned_investments!.csv.
What it does:

Fixes column names (e.g., lowercase, no spaces)

Converts strings like '1,000,000' into numeric format

Extracts year from date columns

Handles missing values, renames columns

Creates useful features like primary_category, founded_year, etc.

2. EDA + Visualization Script – investment anylsis report data visualazation.py
This script reads the cleaned data and creates static charts and graphs using Matplotlib and Seaborn.
Visuals include:

Total funding amounts


APP LINK 
https://siaapppy-vc2ufbbredilx6bvrcdbu9.streamlit.app/

Top N funded companies

Funding by country

Most active startup categories

Trends in funding over years

Pie chart of startup status (e.g., operating, acquired)

Correlation between funding and number of funding rounds

📊 This is your exploratory data analysis (EDA) phase — understanding the story behind the numbers.


3. Streamlit Dashboard – SIAapp.py
This script is a fully interactive web dashboard built using Streamlit.
Users can:

View top funded startups

Explore funding trends and categories

Interact with filters (e.g., Top N countries or companies)

Use visual tools like pie charts, boxplots, and heatmaps

This dashboard reads the cleaned_investments!.csv file and offers a user-friendly interface for exploring the insights you’ve generated.
