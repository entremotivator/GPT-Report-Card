import streamlit as st
import pandas as pd
import base64
from io import BytesIO, StringIO
import plotly.express as px
import plotly.graph_objects as go

# Function to generate download link for Excel file
def generate_excel_download_link(df):
    towrite = BytesIO()
    df.to_excel(towrite, encoding="utf-8", index=False, header=True)
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_download.xlsx">Download Excel File</a>'
    return st.markdown(href, unsafe_allow_html=True)

# Function to generate download link for Plotly chart as HTML
def generate_html_download_link(fig):
    towrite = StringIO()
    fig.write_html(towrite, include_plotlyjs="cdn")
    towrite = BytesIO(towrite.getvalue().encode())
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:text/html;charset=utf-8;base64, {b64}" download="plot.html">Download Plot</a>'
    return st.markdown(href, unsafe_allow_html=True)

# Function to display summary statistics for the selected LLM metric
def display_summary_statistics(df, metric_column):
    st.subheader('Summary Statistics:')
    summary_stats = df[metric_column].describe()
    st.write(summary_stats)

# Streamlit App
st.set_page_config(page_title='LLM Evaluator')
st.title('LLM Evaluator 🤖')
st.subheader('Feed me with your LLM data')

uploaded_file = st.file_uploader('Choose a CSV file', type='csv')
if uploaded_file:
    st.markdown('---')
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)

    # User customization options
    metric_column = st.selectbox(
        'What LLM metric would you like to analyze?',
        ('Relevance', 'Sentiment', 'Model Agreement', 'Language Match', 'Toxicity',
         'Moderation', 'Correctness: QA evaluation', 'No labels: criteria evaluation',
         'Criteria with labels', 'Embedding distance', 'String distance',
         'Log feedback for a run', 'Filter runs based on feedback', 'Export runs to dataset'),
    )

    plot_type = st.selectbox(
        'Select plot type',
        ('Bar Chart', 'Pie Chart', 'Box Plot'),
    )

    # GROUP DATAFRAME (Example: Count occurrences of each metric value)
    df_grouped = df.groupby(by=[metric_column], as_index=False).count()

    # PLOT DATAFRAME
    st.subheader(f'{metric_column} Analysis:')
    if plot_type == 'Bar Chart':
        fig = px.bar(
            df_grouped,
            x=metric_column,
            y='Column_Name',  # Replace 'Column_Name' with an actual column in your dataset
            template='plotly_white',
            title=f'<b>{metric_column} Analysis</b>'
        )
    elif plot_type == 'Pie Chart':
        fig = px.pie(
            df_grouped,
            names=metric_column,
            template='plotly_white',
            title=f'<b>{metric_column} Analysis</b>'
        )
    elif plot_type == 'Box Plot':
        fig = go.Figure()
        for value in df_grouped[metric_column].unique():
            subset = df[df[metric_column] == value]
            fig.add_trace(go.Box(y=subset['Column_Name'], name=str(value)))
        fig.update_layout(title=f'<b>{metric_column} Analysis</b>', showlegend=False)

    st.plotly_chart(fig)

    # Display summary statistics
    display_summary_statistics(df, metric_column)

    # DOWNLOAD SECTION
    st.subheader('Downloads:')
    generate_excel_download_link(df_grouped)
    generate_html_download_link(fig)
