import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Function to generate the PDF factsheet
def generate_pdf(data, performance_chart_path):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, 750, "Professional Factsheet")
    
    # Key holdings section
    c.setFont("Helvetica", 12)
    c.drawString(30, 720, "Principal Holdings (Top Equity Holdings):")
    holdings = data['Holdings'].tolist()
    y = 700
    for holding in holdings:
        c.drawString(50, y, f"- {holding}")
        y -= 20

    # Fund performance
    c.drawString(30, y - 10, "Fund Performance (Year-to-Date):")
    performance_data = data[['Month', 'Portfolio Performance']].to_dict(orient='records')
    y -= 40
    for record in performance_data:
        c.drawString(50, y, f"{record['Month']}: {record['Portfolio Performance']}%")
        y -= 20

    # Insert the performance chart
    c.drawImage(performance_chart_path, 30, y - 150, width=540, height=200)

    c.save()
    buffer.seek(0)
    return buffer

# Function to generate a sample performance chart
def generate_performance_chart(data):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data['Month'], data['Portfolio Performance'], label="Portfolio Performance", marker='o')
    ax.set_title("Fund Performance")
    ax.set_xlabel("Month")
    ax.set_ylabel("Performance (%)")
    ax.legend()
    plt.tight_layout()

    # Save the chart to a temporary file and return the path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        plt.savefig(tmp_file.name, format='png')
        tmp_file_path = tmp_file.name
    return tmp_file_path

# Function to generate a downloadable CSV template
def generate_csv_template():
    template_data = {
        "Month": ["January", "February", "March", "April", "May", "June"],
        "Portfolio Performance": [1.5, 2.3, 3.8, -1.2, 0.5, -0.8],
        "Holdings": ["Company A", "Company B", "Company C", "Company D", "Company E", "Company F"]
    }
    template_df = pd.DataFrame(template_data)
    return template_df

# Streamlit App
st.title("Professional Factsheet Generator")

# CSV Template Download
st.subheader("Download CSV Template")
if st.button("Download Template"):
    template_df = generate_csv_template()
    csv_buffer = BytesIO()
    template_df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    st.download_button(
        label="Download Template CSV",
        data=csv_buffer,
        file_name="factsheet_template.csv",
        mime="text/csv"
    )

# Upload Section
st.subheader("Upload CSV Data")
uploaded_file = st.file_uploader("Upload a CSV file with factsheet data", type=["csv"])

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Uploaded Data Preview:")
    st.write(data)

    # Validate columns
    required_columns = {"Month", "Portfolio Performance", "Holdings"}
    if not required_columns.issubset(data.columns):
        st.error(f"The uploaded CSV must contain the following columns: {', '.join(required_columns)}")
    else:
        # Generate the performance chart
        performance_chart_path = generate_performance_chart(data)

        # Display the performance chart
        st.image(performance_chart_path, caption="Generated Performance Chart")

        # Generate PDF
        st.subheader("Download Factsheet")
        pdf_buffer = generate_pdf(data, performance_chart_path)
        st.download_button(
            label="Download Factsheet PDF",
            data=pdf_buffer,
            file_name="factsheet.pdf",
            mime="application/pdf"
        )
