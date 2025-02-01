import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# Generate a factsheet PDF
def generate_pdf(data, performance_chart_path, sector_chart_path):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Title section
    title_data = [
        ["Fund Factsheet"],
        [f"Fund Name: {data['Fund Name'][0]}"],
        [f"Fund Manager: {data['Fund Manager'][0]}"],
        [f"Investment Objective: {data['Investment Objective'][0]}"],
        [f"Expense Ratio: {data['Expense Ratio'][0]}%"],
        [f"Assets Under Management: ${data['Assets Under Management'][0]} Million"]
    ]
    title_table = Table(title_data)
    title_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ]))
    elements.append(title_table)

    # Holdings section
    elements.append(Table([["Principal Holdings (Top Equity Holdings):"]]))
    holdings = [[holding] for holding in data['Holdings']]
    holdings_table = Table(holdings)
    elements.append(holdings_table)

    # Add charts
    elements.append(Table([["Fund Performance Chart"]]))
    elements.append(performance_chart_path)
    elements.append(Table([["Sector Allocation Chart"]]))
    elements.append(sector_chart_path)

    doc.build(elements)
    buffer.seek(0)
    return buffer




# Generate performance chart
def generate_performance_chart(data):
    plt.figure(figsize=(8, 4))
    plt.plot(data['Month'], data['Portfolio Performance'], marker='o', label='Portfolio Performance')
    plt.title('Fund Performance')
    plt.xlabel('Month')
    plt.ylabel('Performance (%)')
    plt.legend()
    plt.grid(True)
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp_file.name)
    plt.close()
    return temp_file.name

# Generate sector allocation chart
def generate_sector_chart(data):
    sectors = data['Sector Allocations'].str.split(', ', expand=True)
    sector_labels = sectors[0]
    sector_values = sectors[1].astype(float)
    
    plt.figure(figsize=(6, 6))
    plt.pie(sector_values, labels=sector_labels, autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    plt.title('Sector Allocations')
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    plt.savefig(temp_file.name)
    plt.close()
    return temp_file.name

# Generate CSV template
def generate_csv_template():
    template_data = {
        'Fund Name': ['Sample Fund'],
        'Fund Manager': ['John Doe'],
        'Investment Objective': ['Maximize long-term growth.'],
        'Expense Ratio': [0.75],
        'Assets Under Management': [500],
        'Month': ['January', 'February', 'March'],
        'Portfolio Performance': [1.5, 2.3, 3.1],
        'Holdings': ['Company A, Company B, Company C'],
        'Sector Allocations': ['Technology, 50', 'Healthcare, 30', 'Finance, 20']
    }
    return pd.DataFrame(template_data)

# Streamlit App
st.title("Professional Factsheet Generator")

# Template Download
st.subheader("Download Template")
if st.button("Download CSV Template"):
    template_df = generate_csv_template()
    csv_buffer = BytesIO()
    template_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        label="Download Template",
        data=csv_buffer,
        file_name="factsheet_template.csv",
        mime="text/csv"
    )

# File Upload Section
st.subheader("Upload CSV File")
uploaded_file = st.file_uploader("Upload a CSV file with the required data", type=['csv'])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Uploaded Data Preview:")
    st.write(data)

    # Generate Charts
    performance_chart_path = generate_performance_chart(data)
    sector_chart_path = generate_sector_chart(data)

    # Display Charts
    st.image(performance_chart_path, caption="Fund Performance Chart")
    st.image(sector_chart_path, caption="Sector Allocation Chart")

    # Generate PDF
    pdf_buffer = generate_pdf(data, performance_chart_path, sector_chart_path)
    st.download_button(
        label="Download Factsheet PDF",
        data=pdf_buffer,
        file_name="factsheet.pdf",
        mime="application/pdf"
    )
