import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from mysql.connector import Error
import numpy as np

# Ensure we get database configuration from secrets
db_config = st.secrets["mysql"]
user = db_config["user"]
password = db_config["password"]
host = db_config["host"]
port = db_config["port"]
database = db_config["database"]

# Membuat koneksi
try:
    dataBase = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        port=port,
        database=database
    )
    connection_successful = True
    st.write("Connected to the database")
except Error as e:
    st.error(f"Failed to connect to the database: {e}")
    connection_successful = False

# Function to plot Standard Cost per Product per Month
def plot_standard_cost_per_product_per_month(dataBase):
    try:
        dimproduct_query = 'SELECT ProductKey, EnglishProductName, StandardCost FROM dimproduct'
        dimproduct = pd.read_sql(dimproduct_query, con=dataBase)

        dimtime_query = 'SELECT TimeKey, EnglishMonthName FROM dimtime'
        dimtime = pd.read_sql(dimtime_query, con=dataBase)

        factinternetsales_query = 'SELECT ProductKey, OrderDateKey, SalesAmount FROM factinternetsales'
        factinternetsales = pd.read_sql(factinternetsales_query, con=dataBase)

        merged_data_time = pd.merge(factinternetsales, dimtime, left_on='OrderDateKey', right_on='TimeKey')
        merged_data = pd.merge(merged_data_time, dimproduct, on='ProductKey')

        agg_data = merged_data.groupby(['EnglishMonthName', 'EnglishProductName'])['StandardCost'].mean().reset_index()
        pivot_data = agg_data.pivot(index='EnglishMonthName', columns='EnglishProductName', values='StandardCost')

        months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        pivot_data = pivot_data.reindex(months_order)

        plt.figure(figsize=(14, 8))
        for column in pivot_data.columns:
            plt.plot(pivot_data.index, pivot_data[column], marker='o', label=column)

        plt.xlabel('Month')
        plt.ylabel('Standard Cost')
        plt.title('Comparison of Standard Cost per Product per Month')
        plt.legend(title='Product')
        plt.grid(True)
        plt.xticks(rotation=45)
        st.pyplot(plt)
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Distribution of Department by Geography
def plot_distribution_of_department_by_geography(dataBase):
    try:
        dimemployee_query = 'SELECT EmployeeKey, DepartmentName, Title FROM dimemployee'
        dimemployee = pd.read_sql(dimemployee_query, con=dataBase)

        dimgeography_query = 'SELECT GeographyKey, EnglishCountryRegionName FROM dimgeography'
        dimgeography = pd.read_sql(dimgeography_query, con=dataBase)

        np.random.seed(42)
        random_geographies = np.random.choice(dimgeography['EnglishCountryRegionName'], len(dimemployee))
        dimemployee['EnglishCountryRegionName'] = random_geographies

        plt.figure(figsize=(14, 8))
        sns.countplot(data=dimemployee, x='DepartmentName', hue='EnglishCountryRegionName')
        plt.xlabel('Department Name')
        plt.ylabel('Count')
        plt.title('Distribution of Department Name by Geography')
        plt.xticks(rotation=90)
        plt.grid(True)
        plt.legend(title='Geography')
        st.pyplot(plt)
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Customer Education Composition by Country
def plot_customer_education_composition_by_country(dataBase):
    try:
        dimcustomer_query = 'SELECT CustomerKey, EnglishEducation, GeographyKey FROM dimcustomer'
        dimcustomer = pd.read_sql(dimcustomer_query, con=dataBase)

        dimgeography_query = 'SELECT GeographyKey, EnglishCountryRegionName FROM dimgeography'
        dimgeography = pd.read_sql(dimgeography_query, con=dataBase)

        merged_data = pd.merge(dimcustomer, dimgeography, on='GeographyKey')
        composition_data = merged_data.groupby(['EnglishCountryRegionName', 'EnglishEducation']).size().unstack()

        country = composition_data.index
        education_levels = composition_data.columns
        values = composition_data.sum(axis=0)

        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(aspect="equal"))
        wedges, texts, autotexts = ax.pie(values, autopct='%1.1f%%', startangle=140, pctdistance=0.85, colors=plt.cm.Paired.colors)

        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        fig.gca().add_artist(centre_circle)

        ax.legend(wedges, education_levels, title="Education Levels", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.title('Customer Education Composition by Country')

        st.pyplot(fig)
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Product Category Name Count
def plot_product_category_name_count(dataBase):
    try:
        dimproductcategory_query = 'SELECT ProductCategoryKey, EnglishProductCategoryName FROM dimproductcategory'
        dimproductcategory = pd.read_sql(dimproductcategory_query, con=dataBase)

        dimcurrency_query = 'SELECT CurrencyKey, CurrencyName FROM dimcurrency'
        dimcurrency = pd.read_sql(dimcurrency_query, con=dataBase)

        np.random.seed(42)
        random_currency = np.random.choice(dimcurrency['CurrencyName'], len(dimproductcategory))
        dimproductcategory['CurrencyName'] = random_currency

        product_category_count = dimproductcategory['EnglishProductCategoryName'].value_counts().reset_index()
        product_category_count.columns = ['EnglishProductCategoryName', 'Count']
        product_category_count['CurrencyName'] = dimproductcategory.groupby('EnglishProductCategoryName')['CurrencyName'].first().values

        plt.figure(figsize=(14, 10))
        bubble = plt.scatter(product_category_count['EnglishProductCategoryName'], 
                             product_category_count['Count'], 
                             s=product_category_count['Count']*100, alpha=0.5, 
                             c=pd.factorize(product_category_count['CurrencyName'])[0], cmap='viridis')

        plt.xlabel('Product Category Name')
        plt.ylabel('Count')
        plt.title('Product Category Name Count')
        plt.colorbar(bubble, label='Currency (Encoded)')
        plt.xticks(rotation=90)
        plt.tight_layout()

        st.pyplot(plt)
    except Error as e:
        st.error(f"Error: {e}")

# Streamlit app
if connection_successful:
    st.title('Data Visualization Dashboard')

    st.header('Standard Cost per Product per Month')
    plot_standard_cost_per_product_per_month(dataBase)

    st.header('Distribution of Department Name by Geography')
    plot_distribution_of_department_by_geography(dataBase)

    st.header('Customer Education Composition by Country')
    plot_customer_education_composition_by_country(dataBase)

    st.header('Product Category Name Count')
    plot_product_category_name_count(dataBase)
else:
    st.error("Failed to connect to the database. Please check your connection settings.")
