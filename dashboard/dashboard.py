import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from datetime import date, datetime, timedelta
from babel.numbers import format_currency

# Define colors
colors = sns.color_palette("Set2", 8)

# Load data
day_dataFrame = pd.read_csv("https://raw.githubusercontent.com/MitaAdhani/day-datasheet/main/day.csv")
hour_dataFrame = pd.read_csv("https://raw.githubusercontent.com/MitaAdhani/day-datasheet/main/hour.csv")

# Merge dataframes
bike_dataFrame = hour_dataFrame.merge(day_dataFrame, on='dteday', how='inner', suffixes=('_hour', '_day'))

# Define weather labels
weather_labels = {
    1: 'Clear',
    2: 'Mist',
    3: 'Light Rainfall',
    4: 'Heavy Rainfall'
}
bike_dataFrame['weather_label'] = bike_dataFrame['weathersit_day'].map(weather_labels)

# Create a Streamlit app
st.title('Bike Sharing :bike:')

# Convert string dates to datetime.date objects
min_date = datetime.strptime('2004-01-01', '%Y-%m-%d').date()
max_date = datetime.strptime('2024-12-31', '%Y-%m-%d').date()

with st.sidebar:
    # Adding the company logo
    st.image("https://raw.githubusercontent.com/MitaAdhani/bike-sharing/main/bike-sharing-benefits-and-disadvantages.jpeg")
    # saya ambil dari https://kassandmoses.com/blog/bike-sharing-benefits-and-disadvantages/
    
    # Getting start_date & end_date from date_input
    date_range = st.date_input(
        label='Rentang Waktu',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )      

# Fungsi untuk menampilkan jumlah rental sepeda berdasarkan kondisi cuaca
def visualize_bike_count_by_weather(df):
    st.write('## Jumlah Rental Sepeda Berdasarkan Kondisi Cuaca')
    fig, ax = plt.subplots(figsize=(10, 6))  # Add fig, ax here
    sns.barplot(x='weather_label', y='cnt_day', data=df, ci=None, ax=ax)  # Add ax here
    plt.title('Jumlah Rental Sepeda Berdasarkan Kondisi Cuaca', fontsize=16)
    plt.xlabel('Kondisi Cuaca', fontsize=14)
    plt.ylabel('Jumlah Rental Sepeda', fontsize=14)
    plt.xticks(fontsize=12)  # Ukuran label pada sumbu x
    plt.yticks(fontsize=12)  # Ukuran label pada sumbu y
    st.pyplot(fig)

    # Menampilkan total keseleuruhan penyewa, total registered user, dan total casual user
    col1, col2, col3 = st.columns(3)

    with col1:
        total_customers = df['cnt_day'].sum()
        st.metric("Total Penyewa", value=total_customers)

    with col2:
        total_registered = df['registered_day'].sum()
        st.metric("Total Registered User", value=total_registered)

    with col3:
        total_casual = df['casual_day'].sum()
        st.metric("Total Casual User", value=total_casual)

def visualize_bike_count_by_weather_workingday(df):
    st.write('## Penggunaan Rental Sepeda Berdasarkan Kondisi Cuaca pada Hari Kerja')
    working_day_df = df[df['workingday_day'] == 1]

    # Menambahkan kolom total customers
    working_day_df['total_customers'] = working_day_df['registered_day'] + working_day_df['casual_day']

    fig, ax = plt.subplots(figsize=(10, 6))  # Add fig, ax here
    sns.barplot(x='weather_label', y='cnt_day', hue='total_customers', data=working_day_df, ci=None, ax=ax)  # Add ax here
    plt.title('Penggunaan Rental Sepeda Berdasarkan Kondisi Cuaca pada Hari Kerja', fontsize=16)
    plt.xlabel('Kondisi Cuaca', fontsize=14)
    plt.ylabel('Jumlah Rental Sepeda', fontsize=14)
    plt.xticks(fontsize=12)  # Ukuran label pada sumbu x
    plt.yticks(fontsize=12)  # Ukuran label pada sumbu y
    
    # Menempatkan legenda di atas grafik
    plt.legend(title='Total Customers', loc='upper center', bbox_to_anchor=(0.5, -0.15), fontsize=12, ncol=3)
    
    st.pyplot(fig)

def visualize_correlation_heatmap_with_windspeed(df):
    st.write('## Heatmap Korelasi antara Kondisi Berangin dan Jumlah Penggunaan Rental Sepeda')
    correlation = df[['windspeed_day', 'cnt_day']].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(correlation, annot=True, cmap='coolwarm', ax=ax)
    plt.title('Heatmap: Korelasi antara Kondisi Berangin dan Jumlah Penggunaan Rental Sepeda', fontsize=16)
    plt.xlabel('Variabel', fontsize=14)
    plt.ylabel('Variabel', fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    return fig

# Fungsi untuk menampilkan visualisasi RFM
def visualize_rfm(df):
    st.write('## Visualisasi RFM (Recency, Frequency, Monetary)')
    rfm_df = df.groupby('dteday').agg({
        'dteday': lambda date: (df['dteday'].max() - date.max()).days,  # Recency
        'cnt_day': 'count',  # Frequency
        'registered_day': 'sum',  # Monetary dari pelanggan terdaftar
        'casual_day': 'sum'  # Monetary dari pelanggan non-terdaftar
    }).rename(columns={
        'dteday': 'Recency',
        'cnt_day': 'Frequency',
        'registered_day': 'Monetary_Registered',
        'casual_day': 'Monetary_Casual'
    })

    # Rata-rata RFM
    avg_recency = round(rfm_df['Recency'].mean(), 1)
    avg_frequency = round(rfm_df['Frequency'].mean(), 2)
    avg_monetary_registered = round(rfm_df['Monetary_Registered'].mean(), 2)
    avg_monetary_casual = round(rfm_df['Monetary_Casual'].mean(), 2)

    st.write(f"Average Recency (days): {avg_recency}")
    st.write(f"Average Frequency: {avg_frequency}")
    st.write(f"Average Monetary (Registered): {avg_monetary_registered}")
    st.write(f"Average Monetary (Casual): {avg_monetary_casual}")

    st.write(rfm_df.head())

    fig, ax = plt.subplots(nrows=1, ncols=4, figsize=(35, 6))  # Menambahkan 4 kolom untuk metrik rata-rata

    # Visualisasi Recency
    sns.barplot(y="Recency", x="dteday", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel(None)
    ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
    ax[0].tick_params(axis ='x', labelsize=15)

    # Visualisasi Frequency
    sns.barplot(y="Frequency", x="dteday", data=rfm_df.sort_values(by="Frequency", ascending=False).head(5), palette=colors, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel(None)
    ax[1].set_title("By Frequency", loc="center", fontsize=18)
    ax[1].tick_params(axis='x', labelsize=15)

    # Visualisasi Monetary
    sns.barplot(y="Monetary_Registered", x="dteday", data=rfm_df.sort_values(by="Monetary_Registered", ascending=False).head(5), palette=colors, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel(None)
    ax[2].set_title("By Monetary (Registered)", loc="center", fontsize=18)
    ax[2].tick_params(axis='x', labelsize=15)

    # Visualisasi Monetary
    sns.barplot(y="Monetary_Casual", x="dteday", data=rfm_df.sort_values(by="Monetary_Casual", ascending=False).head(5), palette=colors, ax=ax[3])
    ax[3].set_ylabel(None)
    ax[3].set_xlabel(None)
    ax[3].set_title("By Monetary (Casual)", loc="center", fontsize=18)
    ax[3].tick_params(axis='x', labelsize=15)

    plt.suptitle("Best Customer Based on RFM Parameters (dteday)", fontsize=20)
    st.pyplot(fig)

def load_and_filter_data(filename, start_date, end_date):
    # Load data from file
    df = pd.read_csv(filename)

    # Convert 'dteday' column to datetime
    df['dteday'] = pd.to_datetime(df['dteday'])

    # Convert input date_range to datetime64[ns]
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.min.time()) + timedelta(days=1)

    # Filter data based on date range input by user
    filtered_df = df[(df['dteday'] >= start_date) & (df['dteday'] < end_date)]

    return filtered_df

# Memuat dan menyaring data
bike_dataFrame = load_and_filter_data("Bike_data.csv", date_range[0], date_range[1])

# Menampilkan visualisasi
visualize_bike_count_by_weather(bike_dataFrame)
visualize_bike_count_by_weather_workingday(bike_dataFrame)
# Fungsi untuk menampilkan heatmap korelasi
fig = visualize_correlation_heatmap_with_windspeed(bike_dataFrame)
st.pyplot(fig)
visualize_rfm(bike_dataFrame)