import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data
@st.cache_data
def load_data():
    return pd.read_csv('data/honey-bee-colonies.csv')


# Visualization for colonies by state
def plot_lost_colonies(data, year, time_period):
    filtered_data = data[(data['year'] == year) & (data['time_period'] == time_period)]
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x='state', y='lost_colonies', data=filtered_data, ax=ax, palette='husl')
    ax.set_title(f'Lost Colonies by State ({time_period} {year})')
    ax.set_xlabel('State')
    ax.set_ylabel('Lost Colonies')
    plt.xticks(rotation=45)
    st.pyplot(fig)

# Main app layout
def main():
    st.title("Bee Colony Data Visualizations")
    
    # Load the dataset
    data = load_data()
    
    # Sidebar for user input
    st.sidebar.header("Choose Visualization")
    viz_choice = st.sidebar.selectbox("Select Visualization", 
                                      ["Lost Colonies by State", "Colony Trends", "Added vs Lost Colonies"])
    
    if viz_choice == "Lost Colonies by State":
        st.subheader("Lost Colonies by State")
        year = st.sidebar.selectbox("Select Year", data['year'].unique())
        time_period = st.sidebar.selectbox("Select Time Period", data['time_period'].unique())
        plot_lost_colonies(data, year, time_period)
        

if __name__ == "__main__":
    main()