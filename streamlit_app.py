import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to generate a sample CSV template
def generate_csv_template():
    template_data = {
        "Fund Objective": ["We identify companies whose share prices differ materially from intrinsic valuations."],
        "Principal Holdings": ["Growth Point, Redefine, Hyprop, Investec Property"],
        "Fees": ["Management Fee: 1.5% per annum, Brokerage Fee: 0.60%"],
        "Portfolio Performance (Jan)": ["-0.1%"],
        "Portfolio Performance (Feb)": ["0.94%"],
        "Portfolio Performance (Mar)": ["8.49%"],
        "Portfolio Performance (Apr)": ["1.46%"],
        "Portfolio Performance (May)": ["-1.85%"],
        "Portfolio Performance (Jun)": ["-1.56%"],
        "SAPY Performance (Jan)": ["-3.0%"],
        "SAPY Performance (Feb)": ["1.6%"],
        "SAPY Performance (Mar)": ["7.1%"],
        "SAPY Performance (Apr)": ["1.7%"],
        "SAPY Performance (May)": ["-4.09%"],
        "SAPY Performance (Jun)": ["-4.09%"]
    }
    return pd.DataFrame(template_data)

# Function to generate PDF
def generate_pdf(data, performance_chart):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, 750, "MSM Property Fund Factsheet")

    y = 720
    for key, value in data.items():
        c.setFont("Helvetica", 12)
        c.drawString(30, y, f"{key}: {value}")
        y -= 20

    c.drawImage(performance_chart, 30, y - 150, width=540, height=200)
    c.save()

    buffer.seek(0)
    return buffer

# Function to create a performance chart
def create_performance_chart(data):
    fig, ax = plt.subplots()

    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    portfolio_perf = [float(data[f"Portfolio Performance ({month})"].strip('%')) for month in months]
    sapy_perf = [float(data[f"SAPY Performance ({month})"].strip('%')) for month in months]

    ax.plot(months, portfolio_perf, label="Portfolio Performance", marker="o")
    ax.plot(months, sapy_perf, label="SAPY Performance", marker="o")

    ax.set_title("Performance Comparison")
    ax.set_xlabel("Months")
    ax.set_ylabel("Performance (%)")
    ax.legend()

    chart_buffer = BytesIO()
    plt.savefig(chart_buffer, format='png')
    chart_buffer.seek(0)
    plt.close(fig)

    return chart_buffer

# Streamlit App
st.title("Factsheet Generator")

st.sidebar.header("Actions")

# Download Template CSV
if st.sidebar.button("Download CSV Template"):
    template_df = generate_csv_template()
    csv = template_df.to_csv(index=False)
    st.sidebar.download_button(
        label="Download Template",
        data=csv,
        file_name="factsheet_template.csv",
        mime="text/csv"
    )

# Upload CSV Data
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Uploaded Data:")
    st.dataframe(data)

    # Convert data to dictionary
    data_dict = data.iloc[0].to_dict()

    # Generate Performance Chart
    performance_chart = create_performance_chart(data_dict)

    # Generate PDF
    pdf_buffer = generate_pdf(data_dict, performance_chart)

    # Display Download Button for PDF
    st.download_button(
        label="Download Factsheet as PDF",
        data=pdf_buffer,
        file_name="factsheet.pdf",
        mime="application/pdf"
    )
