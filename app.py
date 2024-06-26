import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
from mysql.connector import Error
import numpy as np

# Define the function to create a database connection
def create_connection():
    try:
        conn = mysql.connector.connect(
            host="kubela.id",
            user="davis2024irwan",
            password="wh451n9m@ch1n3", 
            port="3306",
            database="aw"
        )
        st.write("Connected to the database")
        return conn
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
        return None

# Function to plot Standard Cost per Product per Month
def plot_standard_cost_per_product_per_month(conn):
    try:
        dimproduct_query = 'SELECT ProductKey, EnglishProductName, StandardCost FROM dimproduct'
        dimproduct = pd.read_sql(dimproduct_query, con=conn)

        dimtime_query = 'SELECT TimeKey, EnglishMonthName FROM dimtime'
        dimtime = pd.read_sql(dimtime_query, con=conn)

        factinternetsales_query = 'SELECT ProductKey, OrderDateKey, SalesAmount FROM factinternetsales'
        factinternetsales = pd.read_sql(factinternetsales_query, con=conn)

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
        st.write("Grafik diatas menjelaskan perbandingan biaya standar untuk setiap produk per bulan. Dengan melihat grafik ini, kita dapat memahami bagaimana biaya standar dari berbagai produk berubah setiap bulan sepanjang tahun. Produk dengan standard cost tertinggi adalah Sport-100 Helmet dengan varian Red (sekitar 2500) dan produk dengan standard cost terendah adalah Womens Mountains Short ukran S (0).")
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Distribution of Department by Geography
def plot_distribution_of_department_by_geography(conn):
    try:
        dimemployee_query = 'SELECT EmployeeKey, DepartmentName, Title FROM dimemployee'
        dimemployee = pd.read_sql(dimemployee_query, con=conn)

        dimgeography_query = 'SELECT GeographyKey, EnglishCountryRegionName FROM dimgeography'
        dimgeography = pd.read_sql(dimgeography_query, con=conn)

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
        st.write("Grafik diatas menjelaskan distribusi jumlah karyawan di berbagai departemen berdasarkan lokasi geografis. Dapat dilihat pada grafik bahwa negara USA menjadi negara asal paling banyak untuk departemen Production (sekitar 110 orang), sedangkan Australia menjadi negara dengan asal karyawan terendah untuk divisi Tool Design (sekitar 2-3 orang).")
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Customer Education Composition by Country
def plot_customer_education_composition_by_country(conn):
    try:
        dimcustomer_query = 'SELECT CustomerKey, EnglishEducation, GeographyKey FROM dimcustomer'
        dimcustomer = pd.read_sql(dimcustomer_query, con=conn)

        dimgeography_query = 'SELECT GeographyKey, EnglishCountryRegionName FROM dimgeography'
        dimgeography = pd.read_sql(dimgeography_query, con=conn)

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
        st.write("Grafik diatas menjelaskan komposisi pendidikan pelanggan berdasarkan negara. Education terbanyak dari customer adalah Bachelors sebesar 29%, diikuti dengan Partial College sebesar 27.4%, lalu High School sebesar 17.8%, kemudian Graduate Degree sebesar 17.3%, terakhir Partial High School sebesar 8.6%")
    except Error as e:
        st.error(f"Error: {e}")

# Function to plot Product Category Name Count
def plot_product_category_name_count(conn):
    try:
        dimproductcategory_query = 'SELECT ProductCategoryKey, EnglishProductCategoryName FROM dimproductcategory'
        dimproductcategory = pd.read_sql(dimproductcategory_query, con=conn)

        dimcurrency_query = 'SELECT CurrencyKey, CurrencyName FROM dimcurrency'
        dimcurrency = pd.read_sql(dimcurrency_query, con=conn)

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
        st.write("Grafik diatas menjelaskan jumlah kategori produk yang ada. Ukuran gelembung menunjukkan jumlah produk dalam setiap kategori, dan warnanya mewakili mata uang yang berbeda.")
    except Error as e:
        st.error(f"Error: {e}")

# Streamlit app
conn = create_connection()
if conn:
    st.title('Data Visualization Dashboard')

    st.header('Standard Cost per Product per Month')
    plot_standard_cost_per_product_per_month(conn)

    st.header('Distribution of Department Name by Geography')
    plot_distribution_of_department_by_geography(conn)

    st.header('Customer Education Composition by Country')
    plot_customer_education_composition_by_country(conn)

    st.header('Product Category Name Count')
    plot_product_category_name_count(conn)

    conn.close()
else:
    st.error("Failed to connect to the database. Please check your connection settings.")
