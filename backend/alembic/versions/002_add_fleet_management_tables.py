"""Add Fleet Management tables

Revision ID: 002
Revises: 001
Create Date: 2025-11-06 15:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create vehicles table first (referenced by couriers)
    op.create_table(
        'vehicles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plate_number', sa.String(20), nullable=False),
        sa.Column('vehicle_type', sa.String(20), nullable=False),
        sa.Column('make', sa.String(100), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('color', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('ownership_type', sa.String(20), nullable=True),
        sa.Column('registration_number', sa.String(50), nullable=True),
        sa.Column('registration_expiry_date', sa.Date(), nullable=True),
        sa.Column('insurance_company', sa.String(200), nullable=True),
        sa.Column('insurance_policy_number', sa.String(100), nullable=True),
        sa.Column('insurance_expiry_date', sa.Date(), nullable=True),
        sa.Column('vin_number', sa.String(50), nullable=True),
        sa.Column('engine_number', sa.String(50), nullable=True),
        sa.Column('engine_capacity', sa.String(20), nullable=True),
        sa.Column('transmission', sa.String(20), nullable=True),
        sa.Column('fuel_type', sa.String(20), nullable=True),
        sa.Column('current_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('fuel_capacity', sa.Numeric(5, 2), nullable=True),
        sa.Column('purchase_price', sa.Numeric(10, 2), nullable=True),
        sa.Column('purchase_date', sa.Date(), nullable=True),
        sa.Column('monthly_lease_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('depreciation_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('last_service_date', sa.Date(), nullable=True),
        sa.Column('last_service_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('next_service_due_date', sa.Date(), nullable=True),
        sa.Column('next_service_due_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('gps_device_id', sa.String(100), nullable=True),
        sa.Column('gps_device_imei', sa.String(50), nullable=True),
        sa.Column('is_gps_active', sa.Boolean(), nullable=True),
        sa.Column('assigned_to_city', sa.String(100), nullable=True),
        sa.Column('assigned_to_project', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_pool_vehicle', sa.Boolean(), nullable=True),
        sa.Column('total_trips', sa.Integer(), nullable=True),
        sa.Column('total_distance', sa.Numeric(10, 2), nullable=True),
        sa.Column('avg_fuel_consumption', sa.Numeric(5, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehicles_id', 'vehicles', ['id'])
    op.create_index('ix_vehicles_plate_number', 'vehicles', ['plate_number'], unique=True)
    op.create_index('ix_vehicles_status', 'vehicles', ['status'])
    op.create_index('ix_vehicles_vehicle_type', 'vehicles', ['vehicle_type'])

    # Create couriers table
    op.create_table(
        'couriers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('barq_id', sa.String(50), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('mobile_number', sa.String(20), nullable=False),
        sa.Column('employee_id', sa.String(50), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('sponsorship_status', sa.String(20), nullable=True),
        sa.Column('project_type', sa.String(20), nullable=True),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.Column('last_working_day', sa.Date(), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('national_id', sa.String(50), nullable=True),
        sa.Column('nationality', sa.String(100), nullable=True),
        sa.Column('iqama_number', sa.String(50), nullable=True),
        sa.Column('iqama_expiry_date', sa.Date(), nullable=True),
        sa.Column('passport_number', sa.String(50), nullable=True),
        sa.Column('passport_expiry_date', sa.Date(), nullable=True),
        sa.Column('license_number', sa.String(50), nullable=True),
        sa.Column('license_expiry_date', sa.Date(), nullable=True),
        sa.Column('license_type', sa.String(20), nullable=True),
        sa.Column('bank_account_number', sa.String(50), nullable=True),
        sa.Column('bank_name', sa.String(100), nullable=True),
        sa.Column('iban', sa.String(50), nullable=True),
        sa.Column('jahez_driver_id', sa.String(50), nullable=True),
        sa.Column('hunger_rider_id', sa.String(50), nullable=True),
        sa.Column('mrsool_courier_id', sa.String(50), nullable=True),
        sa.Column('current_vehicle_id', sa.Integer(), nullable=True),
        sa.Column('supervisor_name', sa.String(200), nullable=True),
        sa.Column('accommodation_building_id', sa.Integer(), nullable=True),
        sa.Column('accommodation_room_id', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('emergency_contact_name', sa.String(200), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(20), nullable=True),
        sa.Column('performance_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('total_deliveries', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['current_vehicle_id'], ['vehicles.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_couriers_id', 'couriers', ['id'])
    op.create_index('ix_couriers_barq_id', 'couriers', ['barq_id'], unique=True)
    op.create_index('ix_couriers_email', 'couriers', ['email'], unique=True)
    op.create_index('ix_couriers_status', 'couriers', ['status'])
    op.create_index('ix_couriers_city', 'couriers', ['city'])
    op.create_index('ix_couriers_full_name', 'couriers', ['full_name'])

    # Create courier_vehicle_assignments table
    op.create_table(
        'courier_vehicle_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('assignment_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('start_mileage', sa.Integer(), nullable=True),
        sa.Column('end_mileage', sa.Integer(), nullable=True),
        sa.Column('assigned_by', sa.String(200), nullable=True),
        sa.Column('assignment_reason', sa.Text(), nullable=True),
        sa.Column('termination_reason', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_assignments_id', 'courier_vehicle_assignments', ['id'])
    op.create_index('ix_assignments_courier_id', 'courier_vehicle_assignments', ['courier_id'])
    op.create_index('ix_assignments_vehicle_id', 'courier_vehicle_assignments', ['vehicle_id'])
    op.create_index('ix_assignments_status', 'courier_vehicle_assignments', ['status'])
    op.create_index('ix_assignments_start_date', 'courier_vehicle_assignments', ['start_date'])

    # Create vehicle_logs table
    op.create_table(
        'vehicle_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('log_type', sa.String(20), nullable=False),
        sa.Column('log_date', sa.Date(), nullable=False),
        sa.Column('log_time', sa.Time(), nullable=True),
        sa.Column('start_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('end_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('distance_covered', sa.Numeric(10, 2), nullable=True),
        sa.Column('start_location', sa.String(300), nullable=True),
        sa.Column('end_location', sa.String(300), nullable=True),
        sa.Column('route_description', sa.Text(), nullable=True),
        sa.Column('fuel_refilled', sa.Numeric(8, 2), nullable=True),
        sa.Column('fuel_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('fuel_provider', sa.String(20), nullable=True),
        sa.Column('fuel_station_location', sa.String(300), nullable=True),
        sa.Column('fuel_receipt_number', sa.String(100), nullable=True),
        sa.Column('number_of_deliveries', sa.Integer(), nullable=True),
        sa.Column('number_of_orders', sa.Integer(), nullable=True),
        sa.Column('revenue_generated', sa.Numeric(10, 2), nullable=True),
        sa.Column('vehicle_condition', sa.String(50), nullable=True),
        sa.Column('issues_reported', sa.Text(), nullable=True),
        sa.Column('has_issues', sa.Boolean(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('working_hours', sa.Numeric(5, 2), nullable=True),
        sa.Column('weather_conditions', sa.String(100), nullable=True),
        sa.Column('traffic_conditions', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('recorded_by', sa.String(200), nullable=True),
        sa.Column('receipt_image_url', sa.String(500), nullable=True),
        sa.Column('log_photo_urls', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_vehicle_logs_id', 'vehicle_logs', ['id'])
    op.create_index('ix_vehicle_logs_vehicle_id', 'vehicle_logs', ['vehicle_id'])
    op.create_index('ix_vehicle_logs_courier_id', 'vehicle_logs', ['courier_id'])
    op.create_index('ix_vehicle_logs_log_type', 'vehicle_logs', ['log_type'])
    op.create_index('ix_vehicle_logs_log_date', 'vehicle_logs', ['log_date'])

    # Create vehicle_maintenance table
    op.create_table(
        'vehicle_maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('maintenance_type', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('service_provider', sa.String(20), nullable=True),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('mileage_at_service', sa.Numeric(10, 2), nullable=True),
        sa.Column('service_description', sa.Text(), nullable=False),
        sa.Column('work_performed', sa.Text(), nullable=True),
        sa.Column('parts_replaced', sa.Text(), nullable=True),
        sa.Column('parts_list_json', sa.Text(), nullable=True),
        sa.Column('service_center_name', sa.String(300), nullable=True),
        sa.Column('service_center_location', sa.String(300), nullable=True),
        sa.Column('technician_name', sa.String(200), nullable=True),
        sa.Column('technician_phone', sa.String(20), nullable=True),
        sa.Column('labor_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('parts_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('total_cost', sa.Numeric(10, 2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('payment_method', sa.String(50), nullable=True),
        sa.Column('invoice_number', sa.String(100), nullable=True),
        sa.Column('invoice_date', sa.Date(), nullable=True),
        sa.Column('payment_status', sa.String(50), nullable=True),
        sa.Column('has_warranty', sa.Boolean(), nullable=True),
        sa.Column('warranty_expiry_date', sa.Date(), nullable=True),
        sa.Column('warranty_details', sa.Text(), nullable=True),
        sa.Column('next_service_date', sa.Date(), nullable=True),
        sa.Column('next_service_mileage', sa.Numeric(10, 2), nullable=True),
        sa.Column('quality_rating', sa.Integer(), nullable=True),
        sa.Column('approved_by', sa.String(200), nullable=True),
        sa.Column('approval_date', sa.Date(), nullable=True),
        sa.Column('issues_found', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('invoice_image_url', sa.String(500), nullable=True),
        sa.Column('report_file_url', sa.String(500), nullable=True),
        sa.Column('photos_json', sa.Text(), nullable=True),
        sa.Column('vehicle_downtime_hours', sa.Numeric(6, 2), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_maintenance_id', 'vehicle_maintenance', ['id'])
    op.create_index('ix_maintenance_vehicle_id', 'vehicle_maintenance', ['vehicle_id'])
    op.create_index('ix_maintenance_type', 'vehicle_maintenance', ['maintenance_type'])
    op.create_index('ix_maintenance_status', 'vehicle_maintenance', ['status'])
    op.create_index('ix_maintenance_scheduled_date', 'vehicle_maintenance', ['scheduled_date'])

    # Create vehicle_inspections table
    op.create_table(
        'vehicle_inspections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('inspector_id', sa.Integer(), nullable=True),
        sa.Column('inspection_type', sa.String(20), nullable=False),
        sa.Column('inspection_date', sa.Date(), nullable=False),
        sa.Column('inspection_time', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('overall_condition', sa.String(20), nullable=True),
        sa.Column('mileage_at_inspection', sa.Numeric(10, 2), nullable=True),
        # Checklist fields (Boolean)
        sa.Column('engine_condition', sa.Boolean(), nullable=True),
        sa.Column('engine_oil_level', sa.Boolean(), nullable=True),
        sa.Column('coolant_level', sa.Boolean(), nullable=True),
        sa.Column('battery_condition', sa.Boolean(), nullable=True),
        sa.Column('transmission', sa.Boolean(), nullable=True),
        sa.Column('headlights', sa.Boolean(), nullable=True),
        sa.Column('taillights', sa.Boolean(), nullable=True),
        sa.Column('indicators', sa.Boolean(), nullable=True),
        sa.Column('brake_lights', sa.Boolean(), nullable=True),
        sa.Column('horn', sa.Boolean(), nullable=True),
        sa.Column('dashboard_lights', sa.Boolean(), nullable=True),
        sa.Column('brake_pads_front', sa.Boolean(), nullable=True),
        sa.Column('brake_pads_rear', sa.Boolean(), nullable=True),
        sa.Column('brake_fluid_level', sa.Boolean(), nullable=True),
        sa.Column('handbrake', sa.Boolean(), nullable=True),
        sa.Column('tire_front_left', sa.Boolean(), nullable=True),
        sa.Column('tire_front_right', sa.Boolean(), nullable=True),
        sa.Column('tire_rear_left', sa.Boolean(), nullable=True),
        sa.Column('tire_rear_right', sa.Boolean(), nullable=True),
        sa.Column('spare_tire', sa.Boolean(), nullable=True),
        sa.Column('tire_pressure_ok', sa.Boolean(), nullable=True),
        sa.Column('body_condition', sa.Boolean(), nullable=True),
        sa.Column('windshield', sa.Boolean(), nullable=True),
        sa.Column('mirrors', sa.Boolean(), nullable=True),
        sa.Column('wipers', sa.Boolean(), nullable=True),
        sa.Column('doors', sa.Boolean(), nullable=True),
        sa.Column('windows', sa.Boolean(), nullable=True),
        sa.Column('seats', sa.Boolean(), nullable=True),
        sa.Column('seatbelts', sa.Boolean(), nullable=True),
        sa.Column('air_conditioning', sa.Boolean(), nullable=True),
        sa.Column('steering', sa.Boolean(), nullable=True),
        sa.Column('first_aid_kit', sa.Boolean(), nullable=True),
        sa.Column('fire_extinguisher', sa.Boolean(), nullable=True),
        sa.Column('warning_triangle', sa.Boolean(), nullable=True),
        sa.Column('jack_and_tools', sa.Boolean(), nullable=True),
        sa.Column('registration_document', sa.Boolean(), nullable=True),
        sa.Column('insurance_document', sa.Boolean(), nullable=True),
        # Issues and follow-up
        sa.Column('issues_found', sa.Text(), nullable=True),
        sa.Column('critical_issues', sa.Text(), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('required_repairs', sa.Text(), nullable=True),
        sa.Column('requires_immediate_repair', sa.Boolean(), nullable=True),
        sa.Column('requires_follow_up', sa.Boolean(), nullable=True),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('repairs_completed', sa.Boolean(), nullable=True),
        sa.Column('repairs_completion_date', sa.Date(), nullable=True),
        sa.Column('inspector_name', sa.String(200), nullable=True),
        sa.Column('inspector_signature', sa.String(500), nullable=True),
        sa.Column('inspector_comments', sa.Text(), nullable=True),
        sa.Column('weather_during_inspection', sa.String(100), nullable=True),
        sa.Column('location', sa.String(300), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('inspection_report_url', sa.String(500), nullable=True),
        sa.Column('photos_json', sa.Text(), nullable=True),
        sa.Column('inspection_score', sa.Integer(), nullable=True),
        sa.Column('total_checks', sa.Integer(), nullable=True),
        sa.Column('passed_checks', sa.Integer(), nullable=True),
        sa.Column('failed_checks', sa.Integer(), nullable=True),
        sa.Column('meets_safety_standards', sa.Boolean(), nullable=True),
        sa.Column('roadworthy', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspector_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_inspections_id', 'vehicle_inspections', ['id'])
    op.create_index('ix_inspections_vehicle_id', 'vehicle_inspections', ['vehicle_id'])
    op.create_index('ix_inspections_type', 'vehicle_inspections', ['inspection_type'])
    op.create_index('ix_inspections_status', 'vehicle_inspections', ['status'])
    op.create_index('ix_inspections_date', 'vehicle_inspections', ['inspection_date'])

    # Create accident_logs table
    op.create_table(
        'accident_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vehicle_id', sa.Integer(), nullable=False),
        sa.Column('courier_id', sa.Integer(), nullable=True),
        sa.Column('accident_date', sa.Date(), nullable=False),
        sa.Column('accident_time', sa.Time(), nullable=True),
        sa.Column('accident_type', sa.String(20), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('location_description', sa.Text(), nullable=False),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('latitude', sa.Numeric(10, 8), nullable=True),
        sa.Column('longitude', sa.Numeric(11, 8), nullable=True),
        sa.Column('street_address', sa.String(500), nullable=True),
        sa.Column('weather_conditions', sa.String(100), nullable=True),
        sa.Column('road_conditions', sa.String(100), nullable=True),
        sa.Column('visibility', sa.String(50), nullable=True),
        sa.Column('traffic_conditions', sa.String(100), nullable=True),
        sa.Column('fault_status', sa.String(20), nullable=True),
        sa.Column('our_vehicle_at_fault', sa.Boolean(), nullable=True),
        sa.Column('accident_description', sa.Text(), nullable=False),
        sa.Column('courier_statement', sa.Text(), nullable=True),
        sa.Column('witness_statements', sa.Text(), nullable=True),
        sa.Column('other_party_name', sa.String(200), nullable=True),
        sa.Column('other_party_phone', sa.String(20), nullable=True),
        sa.Column('other_party_insurance', sa.String(200), nullable=True),
        sa.Column('other_party_policy_number', sa.String(100), nullable=True),
        sa.Column('other_party_vehicle_plate', sa.String(20), nullable=True),
        sa.Column('other_party_vehicle_details', sa.Text(), nullable=True),
        sa.Column('any_injuries', sa.Boolean(), nullable=True),
        sa.Column('injury_details', sa.Text(), nullable=True),
        sa.Column('casualties_count', sa.Integer(), nullable=True),
        sa.Column('hospitalization_required', sa.Boolean(), nullable=True),
        sa.Column('hospital_name', sa.String(300), nullable=True),
        sa.Column('police_notified', sa.Boolean(), nullable=True),
        sa.Column('police_report_number', sa.String(100), nullable=True),
        sa.Column('police_station', sa.String(200), nullable=True),
        sa.Column('police_officer_name', sa.String(200), nullable=True),
        sa.Column('police_officer_badge', sa.String(50), nullable=True),
        sa.Column('vehicle_damage_description', sa.Text(), nullable=True),
        sa.Column('estimated_repair_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('actual_repair_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('vehicle_towed', sa.Boolean(), nullable=True),
        sa.Column('tow_company', sa.String(200), nullable=True),
        sa.Column('tow_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('insurance_claim_filed', sa.Boolean(), nullable=True),
        sa.Column('insurance_claim_number', sa.String(100), nullable=True),
        sa.Column('insurance_claim_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('insurance_approved_amount', sa.Numeric(10, 2), nullable=True),
        sa.Column('insurance_claim_status', sa.String(50), nullable=True),
        sa.Column('claim_filed_date', sa.Date(), nullable=True),
        sa.Column('claim_settlement_date', sa.Date(), nullable=True),
        sa.Column('repair_start_date', sa.Date(), nullable=True),
        sa.Column('repair_completion_date', sa.Date(), nullable=True),
        sa.Column('repair_shop_name', sa.String(300), nullable=True),
        sa.Column('repair_shop_location', sa.String(300), nullable=True),
        sa.Column('total_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('insurance_covered', sa.Numeric(10, 2), nullable=True),
        sa.Column('out_of_pocket_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('lost_revenue', sa.Numeric(10, 2), nullable=True),
        sa.Column('vehicle_downtime_days', sa.Integer(), nullable=True),
        sa.Column('vehicle_available_date', sa.Date(), nullable=True),
        sa.Column('investigated_by', sa.String(200), nullable=True),
        sa.Column('investigation_date', sa.Date(), nullable=True),
        sa.Column('investigation_findings', sa.Text(), nullable=True),
        sa.Column('corrective_actions', sa.Text(), nullable=True),
        sa.Column('courier_action_taken', sa.String(100), nullable=True),
        sa.Column('courier_notes', sa.Text(), nullable=True),
        sa.Column('accident_photos_json', sa.Text(), nullable=True),
        sa.Column('police_report_url', sa.String(500), nullable=True),
        sa.Column('insurance_documents_json', sa.Text(), nullable=True),
        sa.Column('repair_invoices_json', sa.Text(), nullable=True),
        sa.Column('requires_follow_up', sa.Boolean(), nullable=True),
        sa.Column('follow_up_date', sa.Date(), nullable=True),
        sa.Column('follow_up_notes', sa.Text(), nullable=True),
        sa.Column('reported_by', sa.String(200), nullable=True),
        sa.Column('reported_date', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('legal_action_required', sa.Boolean(), nullable=True),
        sa.Column('legal_case_number', sa.String(100), nullable=True),
        sa.Column('legal_status', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['vehicle_id'], ['vehicles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['courier_id'], ['couriers.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_accidents_id', 'accident_logs', ['id'])
    op.create_index('ix_accidents_vehicle_id', 'accident_logs', ['vehicle_id'])
    op.create_index('ix_accidents_courier_id', 'accident_logs', ['courier_id'])
    op.create_index('ix_accidents_date', 'accident_logs', ['accident_date'])
    op.create_index('ix_accidents_severity', 'accident_logs', ['severity'])
    op.create_index('ix_accidents_status', 'accident_logs', ['status'])
    op.create_index('ix_accidents_city', 'accident_logs', ['city'])


def downgrade() -> None:
    # Drop tables in reverse order (respecting foreign keys)
    op.drop_index('ix_accidents_city', table_name='accident_logs')
    op.drop_index('ix_accidents_status', table_name='accident_logs')
    op.drop_index('ix_accidents_severity', table_name='accident_logs')
    op.drop_index('ix_accidents_date', table_name='accident_logs')
    op.drop_index('ix_accidents_courier_id', table_name='accident_logs')
    op.drop_index('ix_accidents_vehicle_id', table_name='accident_logs')
    op.drop_index('ix_accidents_id', table_name='accident_logs')
    op.drop_table('accident_logs')

    op.drop_index('ix_inspections_date', table_name='vehicle_inspections')
    op.drop_index('ix_inspections_status', table_name='vehicle_inspections')
    op.drop_index('ix_inspections_type', table_name='vehicle_inspections')
    op.drop_index('ix_inspections_vehicle_id', table_name='vehicle_inspections')
    op.drop_index('ix_inspections_id', table_name='vehicle_inspections')
    op.drop_table('vehicle_inspections')

    op.drop_index('ix_maintenance_scheduled_date', table_name='vehicle_maintenance')
    op.drop_index('ix_maintenance_status', table_name='vehicle_maintenance')
    op.drop_index('ix_maintenance_type', table_name='vehicle_maintenance')
    op.drop_index('ix_maintenance_vehicle_id', table_name='vehicle_maintenance')
    op.drop_index('ix_maintenance_id', table_name='vehicle_maintenance')
    op.drop_table('vehicle_maintenance')

    op.drop_index('ix_vehicle_logs_log_date', table_name='vehicle_logs')
    op.drop_index('ix_vehicle_logs_log_type', table_name='vehicle_logs')
    op.drop_index('ix_vehicle_logs_courier_id', table_name='vehicle_logs')
    op.drop_index('ix_vehicle_logs_vehicle_id', table_name='vehicle_logs')
    op.drop_index('ix_vehicle_logs_id', table_name='vehicle_logs')
    op.drop_table('vehicle_logs')

    op.drop_index('ix_assignments_start_date', table_name='courier_vehicle_assignments')
    op.drop_index('ix_assignments_status', table_name='courier_vehicle_assignments')
    op.drop_index('ix_assignments_vehicle_id', table_name='courier_vehicle_assignments')
    op.drop_index('ix_assignments_courier_id', table_name='courier_vehicle_assignments')
    op.drop_index('ix_assignments_id', table_name='courier_vehicle_assignments')
    op.drop_table('courier_vehicle_assignments')

    op.drop_index('ix_couriers_full_name', table_name='couriers')
    op.drop_index('ix_couriers_city', table_name='couriers')
    op.drop_index('ix_couriers_status', table_name='couriers')
    op.drop_index('ix_couriers_email', table_name='couriers')
    op.drop_index('ix_couriers_barq_id', table_name='couriers')
    op.drop_index('ix_couriers_id', table_name='couriers')
    op.drop_table('couriers')

    op.drop_index('ix_vehicles_vehicle_type', table_name='vehicles')
    op.drop_index('ix_vehicles_status', table_name='vehicles')
    op.drop_index('ix_vehicles_plate_number', table_name='vehicles')
    op.drop_index('ix_vehicles_id', table_name='vehicles')
    op.drop_table('vehicles')
