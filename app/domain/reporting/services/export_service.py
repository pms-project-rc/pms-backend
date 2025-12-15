import csv
import io
from typing import List, Dict, Any, IO
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class ExportService:
    def export_to_csv(self, data: List[Dict[str, Any]]) -> IO:
        output = io.StringIO()
        if not data:
            return io.BytesIO(b"")
            
        keys = data[0].keys()
        writer = csv.DictWriter(output, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
        
        # Convert to bytes
        mem = io.BytesIO()
        mem.write(output.getvalue().encode('utf-8'))
        mem.seek(0)
        return mem

    def export_to_excel(self, data: List[Dict[str, Any]]) -> IO:
        if not data:
            return io.BytesIO(b"")
            
        df = pd.DataFrame(data)
        output = io.BytesIO()
        
        # Use ExcelWriter to write to the BytesIO object
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
            
        output.seek(0)
        return output

    def export_to_pdf(self, data: List[Dict[str, Any]], title: str) -> IO:
        if not data:
            return io.BytesIO(b"")
            
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(letter))
        elements = []
        
        styles = getSampleStyleSheet()
        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))
        
        # Prepare data for table
        # Get headers from first item
        headers = list(data[0].keys())
        table_data = [headers]
        
        for item in data:
            row = [str(item.get(key, '')) for key in headers]
            table_data.append(row)
            
        # Create table
        # Calculate column widths based on content or fixed width
        # For simplicity, we'll let reportlab calculate it or use auto
        table = Table(table_data)
        
        # Add style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 0), (-1, -1), 8),  # Smaller font to fit more columns
        ])
        table.setStyle(style)
        
        elements.append(table)
        doc.build(elements)
        
        output.seek(0)
        return output
