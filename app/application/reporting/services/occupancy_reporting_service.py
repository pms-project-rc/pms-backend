from datetime import date, datetime, time, timedelta
from typing import List

from app.domain.reporting.repositories.occupancy_reporting_repository import OccupancyReportingRepository
from app.application.dto.reporting.occupancy_report_response import OccupancyReportResponse, OccupancyDataPoint

class OccupancyReportingService:
    def __init__(self, repository: OccupancyReportingRepository):
        self.repository = repository

    async def get_occupancy_report(self, report_date: date) -> OccupancyReportResponse:
        # Definir rango del día completo (Naive - Local Time)
        start_of_day = datetime.combine(report_date, time.min)
        end_of_day = datetime.combine(report_date, time.max)
        
        # Para consultar a la BD, necesitamos un rango que cubra el día local.
        # Como la BD está en UTC (probablemente), y no sabemos el offset exacto sin librerías extra,
        # pediremos un rango amplio (día anterior y posterior) y filtraremos en memoria.
        # Esto es ineficiente con millones de datos, pero seguro para este MVP.
        # O mejor: Usamos astimezone() para obtener el rango UTC aproximado.
        
        # Convertir start_of_day local a UTC para la query
        # Asumimos que el sistema corre en la zona horaria del negocio.
        start_utc = start_of_day.astimezone().astimezone(None) # Truco para asegurar aware
        # Mejor: simplemente pedimos un buffer de +/- 24 horas para estar seguros
        query_start = start_of_day - timedelta(days=1)
        query_end = end_of_day + timedelta(days=1)
        
        # Obtener todos los registros relevantes
        records = await self.repository.get_parking_records_overlapping(query_start, query_end)
        
        items = []
        max_occupancy = 0
        peak_hour = "00:00"

        # Calcular ocupación hora por hora (00:00 a 23:00 Local)
        for hour in range(24):
            current_time_point = start_of_day + timedelta(hours=hour)
            
            count = 0
            for record in records:
                # Convertir tiempos del registro a Local Naive para comparar con current_time_point
                # record.entry_time es Aware (UTC). .astimezone(None) lo pasa a Local Aware.
                # .replace(tzinfo=None) lo pasa a Local Naive.
                
                if record.entry_time:
                    entry_local = record.entry_time.astimezone(None).replace(tzinfo=None)
                else:
                    continue # Should not happen
                
                exit_local = None
                if record.exit_time:
                    exit_local = record.exit_time.astimezone(None).replace(tzinfo=None)
                
                # Lógica de conteo:
                # El carro cuenta si entró antes o en el momento del punto
                # Y (no ha salido O salió después del punto)
                if entry_local <= current_time_point:
                    if exit_local is None or exit_local > current_time_point:
                        count += 1
            
            hour_label = f"{hour:02d}:00"
            items.append(OccupancyDataPoint(hour=hour_label, count=count))
            
            if count > max_occupancy:
                max_occupancy = count
                peak_hour = hour_label
                
        return OccupancyReportResponse(
            report_date=report_date,
            items=items,
            total_peak_occupancy=max_occupancy,
            peak_hour=peak_hour
        )
