import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from io import StringIO, BytesIO

def generate_download_link(df, fig):
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

    return st.markdown(excel_href + "&emsp;&emsp;" + html_href, unsafe_allow_html=True)

def main():
    st.set_page_config(page_title='GPT Report Card')
    st.title('GPT Report Card 📊')
    st.subheader('Evaluate and analyze LLM & Agent performance')

    uploaded_file = st.file_uploader('Choose a XLSX file', type='xlsx')
    if uploaded_file:
        st.markdown('---')
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        st.dataframe(df)
        groupby_column = st.selectbox(
            'What would you like to analyse?',
            ('Ship Mode', 'Segment', 'Category', 'Sub-Category'),
        )

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
        st.subheader('Downloads:')
        generate_download_link(df_grouped, fig1)

if __name__ == "__main__":
    main()
