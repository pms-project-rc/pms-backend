import csv
import io
from typing import List, Dict, Any, IO

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
        # Placeholder: Return CSV for now as it's compatible
        return self.export_to_csv(data)

    def export_to_pdf(self, data: List[Dict[str, Any]], title: str) -> IO:
        # Placeholder
        return io.BytesIO(b"PDF Export not implemented yet")
