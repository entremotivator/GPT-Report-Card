import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO

def generate_download_link(df, fig, groupby_column, download_section):
    # Download as Excel
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, encoding="utf-8", index=False, header=True, engine='openpyxl')
    excel_buffer.seek(0)
    excel_b64 = base64.b64encode(excel_buffer.read()).decode()
    excel_href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="data_download.xlsx">Download Excel File</a>'

    # Download as HTML
    html_buffer = StringIO()
    fig.write_html(html_buffer, include_plotlyjs="cdn")
    html_buffer = BytesIO(html_buffer.getvalue().encode())
    html_b64 = base64.b64encode(html_buffer.read()).decode()
    html_href = f'<a href="data:text/html;charset=utf-8;base64, {html_b64}" download="plot.html">Download HTML Plot</a>'

    download_section.markdown(
        f"Download: {excel_href} &emsp;&emsp; {html_href}", 
        unsafe_allow_html=True
    )

def main():
    st.set_page_config(page_title='GPT Report Card')
    st.title('GPT Report Card 📊')
    st.subheader('Evaluate and analyze LLM & Agent performance')

    uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
    if not uploaded_file:
        st.info("Please upload an XLSX file.")
        return

    st.markdown('---')
    
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
    except Exception as e:
        st.error(f"Error: {e}")
        return

    st.dataframe(df)

    groupby_column = st.selectbox(
        'What would you like to analyse?',
        ('Ship Mode', 'Segment', 'Category', 'Sub-Category'),
    )

    # Check if the selected groupby_column exists in the DataFrame
    if groupby_column not in df.columns:
        st.warning(f"Warning: '{groupby_column}' column not found in the DataFrame.")
        st.warning(f"Available columns: {', '.join(df.columns)}")  # Display available columns
        return

    # -- GROUP DATAFRAME
    output_columns = ['Sales', 'Profit']
    df_grouped = df.groupby(by=[groupby_column], as_index=False)[output_columns].sum()

    # -- PLOT DATAFRAME
    fig1 = px.bar(
        df_grouped,
        x=groupby_column,
        y='Sales',
        color='Profit',
        color_continuous_scale=['red', 'yellow', 'green'],
        template='plotly_white',
        title=f'<b>Sales & Profit by {groupby_column}</b>'
    )
    st.plotly_chart(fig1)

    fig2 = px.pie(
        df_grouped,
        names=groupby_column,
        values='Sales',
        title=f'<b>Sales Distribution by {groupby_column}</b>'
    )
    st.plotly_chart(fig2)

    fig3 = px.scatter(
        df_grouped,
        x='Sales',
        y='Profit',
        color=groupby_column,
        title=f'<b>Scatter Plot of Sales vs Profit</b>'
    )
    st.plotly_chart(fig3)

    # -- DOWNLOAD SECTION
   def generate_download_link(df, fig, groupby_column, download_section):
    # Download as Excel
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl', options={'encoding':'utf-8'}) as writer:
        df.to_excel(writer, index=False, header=True)

    excel_buffer.seek(0)
    excel_b64 = base64.b64encode(excel_buffer.read()).decode()
    excel_href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{excel_b64}" download="data_download.xlsx">Download Excel File</a>'

    # Download as HTML
    html_buffer = StringIO()
    fig.write_html(html_buffer, include_plotlyjs="cdn")
    html_buffer = BytesIO(html_buffer.getvalue().encode())
    html_b64 = base64.b64encode(html_buffer.read()).decode()
    html_href = f'<a href="data:text/html;charset=utf-8;base64, {html_b64}" download="plot.html">Download HTML Plot</a>'

    download_section.markdown(
        f"Download: {excel_href} &emsp;&emsp; {html_href}", 
        unsafe_allow_html=True
    )
