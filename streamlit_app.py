import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

# Streamlit app definition
def main():
    st.title("Professional Factsheet Generator")
    st.write("Upload your CSV data to generate a professional factsheet.")

    # File upload
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    logo_file = st.file_uploader("Upload Logo (Optional)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Load CSV data
        try:
            data = pd.read_csv(uploaded_file)
            st.write("Preview of Uploaded Data:")
            st.dataframe(data.head())
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return

        # Generate factsheet when user clicks the button
        if st.button("Generate Factsheet"):
            try:
                output_file = "Generated_Factsheet.pdf"
                graph_path = "performance_graph.png"

                # Generate performance graph
                performance_data = data.iloc[:, 1:]
                months = performance_data.columns
                portfolio_performance = performance_data.iloc[0].values
                sapy_performance = performance_data.iloc[1].values

                plt.figure(figsize=(8, 4))
                plt.plot(months, portfolio_performance, label="Portfolio Performance", marker="o")
                plt.plot(months, sapy_performance, label="SAPY", marker="o")
                plt.title("Fund Performance (Year to Date)")
                plt.xlabel("Month")
                plt.ylabel("Performance (%)")
                plt.legend()
                plt.grid()
                plt.savefig(graph_path)
                plt.close()

                # Create PDF factsheet
                doc = SimpleDocTemplate(output_file, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = []

                # Add logo if provided
                if logo_file is not None:
                    logo_path = "uploaded_logo.png"
                    with open(logo_path, "wb") as f:
                        f.write(logo_file.read())
                    elements.append(Image(logo_path, width=100, height=50))

                # Add title
                title = Paragraph("<b>MSM Property Fund</b>", styles['Title'])
                elements.append(title)
                elements.append(Spacer(1, 12))

                # Add fund objective and strategy
                fund_objective = data.loc[0, "Fund Objective"]
                elements.append(Paragraph("<b>Fund Objective and Strategy:</b>", styles['Heading2']))
                elements.append(Paragraph(fund_objective, styles['BodyText']))
                elements.append(Spacer(1, 12))

                # Add who is it for
                who_is_it_for = data.loc[0, "Who is it for"]
                elements.append(Paragraph("<b>Who is it for:</b>", styles['Heading2']))
                elements.append(Paragraph(who_is_it_for, styles['BodyText']))
                elements.append(Spacer(1, 12))

                # Add fees
                management_fee = data.loc[0, "Management Fee"]
                brokerage_fee = data.loc[0, "Brokerage Fee"]
                elements.append(Paragraph("<b>Fees:</b>", styles['Heading2']))
                fee_table_data = [["Management Fee", management_fee], ["Brokerage Fee", brokerage_fee]]
                fee_table = Table(fee_table_data, colWidths=[150, 100])
                fee_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ]))
                elements.append(fee_table)
                elements.append(Spacer(1, 12))

                # Add performance graph
                elements.append(Paragraph("<b>Fund Performance:</b>", styles['Heading2']))
                if os.path.exists(graph_path):
                    elements.append(Image(graph_path, width=400, height=200))

                # Build PDF
                doc.build(elements)

                # Show success message and download link
                st.success("Factsheet generated successfully!")
                with open(output_file, "rb") as f:
                    st.download_button(
                        label="Download Factsheet",
                        data=f,
                        file_name=output_file,
                        mime="application/pdf",
                    )

                # Clean up temporary files
                if os.path.exists(graph_path):
                    os.remove(graph_path)
                if logo_file is not None and os.path.exists(logo_path):
                    os.remove(logo_path)

            except Exception as e:
                st.error(f"Error generating factsheet: {e}")

if __name__ == "__main__":
    main()
