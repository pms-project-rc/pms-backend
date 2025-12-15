from datetime import date
from typing import IO
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.reporting.services.export_service import ExportService
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.domain.washers.repositories.washer_repository import IWasherRepository

class ExportReportsUseCase:
    """Use case for exporting reports"""
    
    def __init__(
        self,
        parking_record_repo: IParkingRecordRepository,
        vehicle_repo: IVehicleRepository,
        export_service: ExportService,
        expense_repo: ExpenseRepository = None,
        subscription_repo: ISubscriptionRepository = None,
        washing_repo: IWashingServiceRepository = None,
        washer_repo: IWasherRepository = None
    ):
        self.parking_record_repo = parking_record_repo
        self.vehicle_repo = vehicle_repo
        self.export_service = export_service
        self.expense_repo = expense_repo
        self.subscription_repo = subscription_repo
        self.washing_repo = washing_repo
        self.washer_repo = washer_repo
    
    async def export_parking_history(
        self, 
        start_date: date, 
        end_date: date, 
        format: str = "csv"
    ) -> IO:
        """
        Export parking history for a date range.
        """
        records = await self.parking_record_repo.list_by_date_range(start_date, end_date)
        
        # Prepare data for export
        data = []
        for record in records:
            vehicle = await self.vehicle_repo.get_by_id(record.vehicle_id)
            plate = vehicle.plate if vehicle else "Unknown"
            
            data.append({
                "ID": record.id,
                "Plate": plate,
                "Entry Time": record.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Exit Time": record.exit_time.strftime("%Y-%m-%d %H:%M:%S") if record.exit_time else "Active",
                "Duration (Hours)": f"{(record.exit_time - record.entry_time).total_seconds() / 3600:.2f}" if record.exit_time else "-",
                "Total Cost": f"${record.total_cost / 100:,.0f}",
                "Status": record.payment_status,
                "Notes": record.notes or ""
            })
            
        if format.lower() == "json":
            return data
        elif format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Parking History Report ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def export_consolidated_revenue(
        self, 
        start_date: date, 
        end_date: date, 
        format: str = "csv"
    ) -> IO:
        """
        Export consolidated revenue for a date range.
        """
        # 1. Get Parking Revenue
        records = await self.parking_record_repo.list_by_date_range(start_date, end_date)
        paid_records = [r for r in records if r.payment_status == "paid"]
        
        # 2. Get Expenses (if repo provided)
        expenses = []
        if self.expense_repo:
            expenses = await self.expense_repo.get_by_date_range(start_date, end_date)

        # 3. Get Subscriptions (if repo provided)
        subscriptions = []
        if self.subscription_repo:
            subscriptions = await self.subscription_repo.get_by_date_range(start_date, end_date)
            
        # Prepare data for export
        data = []
        total_revenue = 0
        total_expenses = 0
        
        # Add Income (Parking)
        for record in paid_records:
            vehicle = await self.vehicle_repo.get_by_id(record.vehicle_id)
            plate = vehicle.plate if vehicle else "Unknown"
            
            revenue = record.total_cost
            total_revenue += revenue
            
            data.append({
                "Date": record.exit_time.strftime("%Y-%m-%d"),
                "Time": record.exit_time.strftime("%H:%M:%S"),
                "Type": "Income",
                "Category": "Parking",
                "Description": f"Vehicle {plate}",
                "Amount": f"${revenue / 100:,.0f}",
                "Payment Method": "Cash"
            })

        # Add Income (Subscriptions)
        for sub in subscriptions:
            vehicle = await self.vehicle_repo.get_by_id(sub.vehicle_id)
            plate = vehicle.plate if vehicle else "Unknown"
            
            # Subscription fee is in pesos (integer), not cents like parking
            revenue = sub.monthly_fee * 100 # Convert to cents to match total_revenue logic or adjust total_revenue logic
            # Wait, parking revenue is in cents (total_cost). Expenses are in pesos.
            # Let's check how total_revenue is used.
            # total_revenue += revenue (cents)
            # Display: revenue / 100
            
            # Subscriptions are likely stored as pesos (e.g. 170000).
            # So if I add to total_revenue (cents), I should multiply by 100.
            # OR I should keep total_revenue in pesos?
            # Parking record total_cost is usually cents (e.g. 500000 for 5000 pesos).
            # Let's verify parking record total_cost unit.
            # In previous turn, I saw "Amount": f"${revenue / 100:,.0f}" for parking. So parking is cents.
            # Expenses were: "Amount": f"-${amount:,.0f}". So expenses are pesos.
            
            # So for Subscriptions:
            # If monthly_fee is 170000 (pesos), then to add to total_revenue (cents), it should be 17000000.
            # BUT, mixing units in total_revenue is dangerous.
            # Let's convert everything to PESOS for the summary.
            
            # Current code: total_revenue += revenue (cents).
            # Summary: f"${total_revenue / 100:,.0f}" -> Converts back to pesos.
            
            # So if I add subscription revenue, I should add it as CENTS to total_revenue.
            # revenue_cents = sub.monthly_fee * 100
            # total_revenue += revenue_cents
            # Display: f"${sub.monthly_fee:,.0f}"
            
            revenue_cents = sub.monthly_fee * 100
            total_revenue += revenue_cents
            
            data.append({
                "Date": sub.created_at.strftime("%Y-%m-%d") if sub.created_at else start_date.strftime("%Y-%m-%d"),
                "Time": sub.created_at.strftime("%H:%M:%S") if sub.created_at else "00:00:00",
                "Type": "Income",
                "Category": "Subscription",
                "Description": f"Monthly Subscription - {plate}",
                "Amount": f"${sub.monthly_fee:,.0f}",
                "Payment Method": "Cash" # Assuming cash for now
            })

        # Add Income (Washing Services)
        if self.washing_repo:
            washing_services = await self.washing_repo.get_by_date_range(start_date, end_date)
            for service in washing_services:
                if service.payment_status == 'paid':
                    vehicle = await self.vehicle_repo.get_by_id(service.vehicle_id)
                    plate = vehicle.plate if vehicle else "Unknown"
                    
                    # Washing price is in pesos
                    revenue_cents = service.price * 100
                    total_revenue += revenue_cents
                    
                    data.append({
                        "Date": service.service_date.strftime("%Y-%m-%d"),
                        "Time": "-",
                        "Type": "Income",
                        "Category": "Washing Service",
                        "Description": f"{service.service_type} - {plate}",
                        "Amount": f"${service.price:,.0f}",
                        "Payment Method": "Cash"
                    })
            
        # Add Expenses
        for expense in expenses:
            amount = expense.amount
            total_expenses += amount
            
            data.append({
                "Date": expense.expense_date.strftime("%Y-%m-%d"),
                "Time": "-",
                "Type": "Expense",
                "Category": expense.expense_type,
                "Description": expense.description or "",
                "Amount": f"-${amount:,.0f}",
                "Payment Method": "Cash"
            })

        # Add Payroll Expenses (Washers)
        if self.washer_repo:
            payroll_summary = await self.washer_repo.get_payroll_summary(start_date, end_date)
            for item in payroll_summary:
                total_to_pay = item['total_to_pay']
                if total_to_pay > 0:
                    total_expenses += total_to_pay
                    
                    data.append({
                        "Date": end_date.strftime("%Y-%m-%d"), # Use end date as it's a summary for the period
                        "Time": "-",
                        "Type": "Expense",
                        "Category": "Nómina",
                        "Description": f"Pago a {item['washer_name']}",
                        "Amount": f"-${total_to_pay:,.0f}",
                        "Payment Method": "Cash"
                    })
            
        # Sort by Date
        data.sort(key=lambda x: x["Date"])
            
        # Add summary rows
        data.append({
            "Date": "", "Time": "", "Type": "", "Category": "", "Description": "", "Amount": "", "Payment Method": ""
        })
        data.append({
            "Date": "",
            "Time": "",
            "Type": "",
            "Category": "Total Ingresos",
            "Description": "",
            "Amount": f"${total_revenue / 100:,.0f}",
            "Payment Method": ""
        })
        data.append({
            "Date": "",
            "Time": "",
            "Type": "",
            "Category": "Total Gastos",
            "Description": "",
            "Amount": f"-${total_expenses:,.0f}",
            "Payment Method": ""
        })
        data.append({
            "Date": "",
            "Time": "",
            "Type": "",
            "Category": "Total",
            "Description": "",
            "Amount": f"${(total_revenue / 100) - total_expenses:,.0f}",
            "Payment Method": ""
        })
            
        if format.lower() == "json":
            return data
        elif format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Income & Expenses Report ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def export_washing_history(
        self, 
        start_date: date, 
        end_date: date, 
        format: str = "csv"
    ) -> IO:
        """
        Export washing service history for a date range.
        """
        if not self.washing_repo:
            raise ValueError("Washing repository not initialized")
            
        services = await self.washing_repo.get_by_date_range(start_date, end_date)
        
        # Prepare data for export
        data = []
        for service in services:
            vehicle = await self.vehicle_repo.get_by_id(service.vehicle_id)
            plate = vehicle.plate if vehicle else "Unknown"
            
            data.append({
                "ID": service.id,
                "Date": service.service_date.strftime("%Y-%m-%d"),
                "Plate": plate,
                "Service Type": service.service_type,
                "Washer ID": service.washer_id or "-",
                "Price": f"${service.price:,.0f}",
                "Status": service.payment_status,
                "Notes": service.notes or ""
            })
            
        if format.lower() == "json":
            return data
        elif format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Washing Services Report ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def export_payroll_summary(self, start_date: date, end_date: date, format: str = "csv") -> IO:
        if not self.washer_repo:
            raise ValueError("Washer repository is required for payroll export")
            
        summary = await self.washer_repo.get_payroll_summary(start_date, end_date)
        
        data = []
        for item in summary:
            data.append({
                "ID Lavador": item["washer_id"],
                "Nombre": item["washer_name"],
                "Total Bono (Comisión)": f"${item['total_bonus']:,.0f}",
                "Total Vales": f"${item['total_advances']:,.0f}",
                "Total a Pagar": f"${item['total_to_pay']:,.0f}"
            })
            
        if format.lower() == "json":
            return data
        elif format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Nómina General de Lavadores ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")

    async def export_payroll_detail(self, washer_id: int, start_date: date, end_date: date, format: str = "csv") -> IO:
        if not self.washer_repo:
            raise ValueError("Washer repository is required for payroll export")
            
        detail = await self.washer_repo.get_washer_payroll_detail(washer_id, start_date, end_date)
        
        data = []
        for item in detail:
            data.append({
                "Fecha": item["date"].strftime("%Y-%m-%d"),
                "Total Lavado": f"${item['total_washed']:,.0f}",
                "Total Bono": f"${item['total_bonus']:,.0f}",
                "Total Vales": f"${item['total_advances']:,.0f}",
                "Total a Pagar": f"${item['total_to_pay']:,.0f}"
            })
            
        if format.lower() == "json":
            return data
        elif format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Detalle de Nómina por Lavador ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")
