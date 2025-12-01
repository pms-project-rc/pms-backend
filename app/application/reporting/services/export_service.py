from typing import List, Dict, Any
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class ExportService:
    """Service for exporting reports to different formats (CSV, Excel, PDF)"""

    def export_to_csv(self, data: List[Dict[str, Any]]) -> BytesIO:
        """
        Export list of dictionaries to CSV.
        Returns BytesIO object containing the CSV data.
        """
        df = pd.DataFrame(data)
        output = BytesIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return output

    def export_to_excel(self, data: List[Dict[str, Any]]) -> BytesIO:
        """
        Export list of dictionaries to Excel (xlsx).
        Returns BytesIO object containing the Excel data.
        """
        df = pd.DataFrame(data)
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)
        return output

    def export_to_pdf(self, data: List[Dict[str, Any]], title: str = "Report") -> BytesIO:
        """
        Export list of dictionaries to PDF.
        Returns BytesIO object containing the PDF data.
        """
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        
        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        if not data:
            elements.append(Paragraph("No data available for this report.", styles['Normal']))
            doc.build(elements)
            output.seek(0)
            return output

        # Prepare data for table
        # Get headers from the first dictionary keys
        headers = list(data[0].keys())
        table_data = [headers]
        
        for item in data:
            row = [str(item.get(key, '')) for key in headers]
            table_data.append(row)

        # Create Table
        # Calculate column widths dynamically or use fixed width
        # For simplicity, we'll let reportlab calculate, but might need adjustment for many columns
        t = Table(table_data)
        
        # Table Style
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        elements.append(t)
        doc.build(elements)
        output.seek(0)
        return output
