-- Crear todas las tablas del PMS en el orden correcto respetando dependencias

-- 1. TABLAS PRINCIPALES SIN DEPENDENCIAS
CREATE TABLE IF NOT EXISTS global_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_global_admins_email ON global_admins(email);
CREATE INDEX ix_global_admins_is_active ON global_admins(is_active);

CREATE TABLE IF NOT EXISTS operational_admins (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_operational_admins_email ON operational_admins(email);
CREATE INDEX ix_operational_admins_is_active ON operational_admins(is_active);

CREATE TABLE IF NOT EXISTS washers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    commission_percentage INTEGER DEFAULT 0 CHECK (commission_percentage >= 0 AND commission_percentage <= 100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_washers_email ON washers(email);
CREATE INDEX ix_washers_is_active ON washers(is_active);

-- Tablas de configuración
CREATE TABLE IF NOT EXISTS business_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_business_config_config_key ON business_config(config_key);

CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_type VARCHAR(50) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX ix_password_reset_tokens_user ON password_reset_tokens(user_type, user_id);
CREATE INDEX ix_password_reset_tokens_is_used ON password_reset_tokens(is_used);
CREATE INDEX ix_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- 2. TABLAS DE VEHÍCULOS Y CONVENIOS
CREATE TABLE IF NOT EXISTS agreements (
    id SERIAL PRIMARY KEY,
    agreement_code VARCHAR(50) UNIQUE NOT NULL,
    company_name VARCHAR(200) NOT NULL,
    discount_percentage INTEGER NOT NULL CHECK (discount_percentage >= 0 AND discount_percentage <= 100),
    is_active BOOLEAN DEFAULT TRUE,
    start_date DATE NOT NULL,
    end_date DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_agreements_agreement_code ON agreements(agreement_code);
CREATE INDEX ix_agreements_is_active ON agreements(is_active);

CREATE TABLE IF NOT EXISTS vehicles (
    id SERIAL PRIMARY KEY,
    plate VARCHAR(20) UNIQUE NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    owner_name VARCHAR(200),
    owner_phone VARCHAR(20),
    is_frequent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_vehicles_plate ON vehicles(plate);
CREATE INDEX ix_vehicles_vehicle_type ON vehicles(vehicle_type);
CREATE INDEX ix_vehicles_is_frequent ON vehicles(is_frequent);
CREATE INDEX ix_vehicles_owner_name ON vehicles(owner_name);

--3. TABLAS RELACIONADAS CON VEHÍCULOS
CREATE TABLE IF NOT EXISTS agreement_vehicles (
    id SERIAL PRIMARY KEY,
    agreement_id INTEGER NOT NULL REFERENCES agreements(id) ON DELETE CASCADE,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(agreement_id, vehicle_id)
);

CREATE INDEX ix_agreement_vehicles_agreement_id ON agreement_vehicles(agreement_id);
CREATE INDEX ix_agreement_vehicles_vehicle_id ON agreement_vehicles(vehicle_id);

CREATE TABLE IF NOT EXISTS monthly_subscriptions (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    subscription_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    monthly_cost INTEGER NOT NULL CHECK (monthly_cost >= 0),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_monthly_subscriptions_vehicle_id ON monthly_subscriptions(vehicle_id);
CREATE INDEX ix_monthly_subscriptions_start_date ON monthly_subscriptions(start_date);
CREATE INDEX ix_monthly_subscriptions_end_date ON monthly_subscriptions(end_date);
CREATE INDEX ix_monthly_subscriptions_payment_status ON monthly_subscriptions(payment_status);
CREATE INDEX ix_monthly_subscriptions_dates ON monthly_subscriptions(start_date, end_date);

-- 4. TABLAS DE TARIFAS Y SERVICIOS
CREATE TABLE IF NOT EXISTS rates (
    id SERIAL PRIMARY KEY,
    rate_type VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    price_per_minute INTEGER,
    flat_rate INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE NOT NULL,
    effective_until DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_rates_rate_type ON rates(rate_type);
CREATE INDEX ix_rates_vehicle_type ON rates(vehicle_type);
CREATE INDEX ix_rates_is_active ON rates(is_active);
CREATE INDEX ix_rates_vehicle_type_rate_type ON rates(vehicle_type, rate_type);

CREATE TABLE IF NOT EXISTS washing_services (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    washer_id INTEGER REFERENCES washers(id) ON DELETE SET NULL,
    service_type VARCHAR(50) NOT NULL,
    service_date DATE NOT NULL,
    total_cost INTEGER NOT NULL CHECK (total_cost >= 0),
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'cancelled')),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_washing_services_vehicle_id ON washing_services(vehicle_id);
CREATE INDEX ix_washing_services_service_date ON washing_services(service_date);
CREATE INDEX ix_washing_services_payment_status ON washing_services(payment_status);

CREATE TABLE IF NOT EXISTS parking_records (
    id SERIAL PRIMARY KEY,
    vehicle_id INTEGER NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
    entry_time TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_time TIMESTAMP WITH TIME ZONE,
    parking_rate_id INTEGER NOT NULL REFERENCES rates(id) ON DELETE RESTRICT,
    subscription_id INTEGER REFERENCES monthly_subscriptions(id) ON DELETE SET NULL,
    washing_service_id INTEGER REFERENCES washing_services(id) ON DELETE SET NULL,
    total_cost INTEGER CHECK (total_cost >= 0),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'cancelled')),
    notes VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_parking_records_vehicle_id ON parking_records(vehicle_id);
CREATE INDEX ix_parking_records_entry_time ON parking_records(entry_time);
CREATE INDEX ix_parking_records_exit_time ON parking_records(exit_time);
CREATE INDEX ix_parking_records_payment_status ON parking_records(payment_status);

-- 5. TABLAS DE GESTIÓN FINANCIERA Y TURNOS
CREATE TABLE IF NOT EXISTS shifts (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES operational_admins(id) ON DELETE CASCADE,
    shift_date DATE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE,
    total_income INTEGER DEFAULT 0,
    tota_expenses INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_shifts_admin_id ON shifts(admin_id);
CREATE INDEX ix_shifts_shift_date ON shifts(shift_date);
CREATE INDEX ix_shifts_admin_date ON shifts(admin_id, shift_date);

CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    shift_id INTEGER NOT NULL REFERENCES shifts(id) ON DELETE CASCADE,
    expense_type VARCHAR(100) NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    description TEXT,
    expense_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_expenses_shift_id ON expenses(shift_id);
CREATE INDEX ix_expenses_expense_date ON expenses(expense_date);
CREATE INDEX ix_expenses_expense_type ON expenses(expense_type);

CREATE TABLE IF NOT EXISTS bonuses (
    id SERIAL PRIMARY KEY,
    washer_id INTEGER NOT NULL REFERENCES washers(id) ON DELETE CASCADE,
    shift_id INTEGER REFERENCES shifts(id) ON DELETE SET NULL,
    bonus_date DATE NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_bonuses_washer_id ON bonuses(washer_id);
CREATE INDEX ix_bonuses_shift_id ON bonuses(shift_id);
CREATE INDEX ix_bonuses_bonus_date ON bonuses(bonus_date);
CREATE INDEX ix_bonuses_washer_date ON bonuses(washer_id, bonus_date);

CREATE TABLE IF NOT EXISTS vouchers (
    id SERIAL PRIMARY KEY,
    voucher_number VARCHAR(50) UNIQUE NOT NULL,
    entity VARCHAR(50) NOT NULL,
    amount INTEGER NOT NULL CHECK (amount >= 0),
    description TEXT,
    payment_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_vouchers_voucher_number ON vouchers(voucher_number);
CREATE INDEX ix_vouchers_payment_date ON vouchers(payment_date);
CREATE INDEX ix_vouchers_entity ON vouchers(entity);

-- 6. TABLAS DE AUDITORÍA Y NOTIFICACIONES
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(100) NOT NULL,
    entity_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_type VARCHAR(50),
    user_id INTEGER,
    changes TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX ix_audit_logs_user ON audit_logs(user_type, user_id);
CREATE INDEX ix_audit_logs_action ON audit_logs(action);
CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    recipient_type VARCHAR(50) NOT NULL,
    recipient_id INTEGER NOT NULL,
    notification_type VARCHAR(100) NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_notifications_recipient ON notifications(recipient_type, recipient_id);
CREATE INDEX ix_notifications_is_read ON notifications(is_read);
CREATE INDEX ix_notifications_notification_type ON notifications(notification_type);
CREATE INDEX ix_notifications_recipient_type ON notifications(recipient_type);
CREATE INDEX ix_notifications_recipient_id ON notifications(recipient_id);

-- 7. TABLAS DE REPORTES
CREATE TABLE IF NOT EXISTS financial_reports (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(50) NOT NULL,
    report_date DATE NOT NULL,
    total_income INTEGER NOT NULL,
    total_expenses INTEGER NOT NULL,
    net_profit INTEGER NOT NULL,
    generated_by INTEGER REFERENCES global_admins(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

CREATE INDEX ix_financial_reports_report_date ON financial_reports(report_date);
CREATE INDEX ix_financial_reports_report_type ON financial_reports(report_type);
