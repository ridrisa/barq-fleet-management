--
-- PostgreSQL database dump
--

-- Dumped from database version 14.18 (Homebrew)
-- Dumped by pg_dump version 14.18 (Homebrew)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: barq; Type: SCHEMA; Schema: -; Owner: ramiz_new
--

CREATE SCHEMA barq;


ALTER SCHEMA barq OWNER TO ramiz_new;

--
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- Name: accidentseverity; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.accidentseverity AS ENUM (
    'MINOR',
    'MODERATE',
    'MAJOR',
    'TOTAL_LOSS'
);


ALTER TYPE public.accidentseverity OWNER TO postgres;

--
-- Name: accidentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.accidentstatus AS ENUM (
    'REPORTED',
    'UNDER_INVESTIGATION',
    'INSURANCE_CLAIM_FILED',
    'IN_REPAIR',
    'RESOLVED',
    'CLOSED'
);


ALTER TYPE public.accidentstatus OWNER TO postgres;

--
-- Name: accidenttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.accidenttype AS ENUM (
    'COLLISION',
    'SINGLE_VEHICLE',
    'PEDESTRIAN',
    'PROPERTY_DAMAGE',
    'ROLLOVER',
    'OTHER'
);


ALTER TYPE public.accidenttype OWNER TO postgres;

--
-- Name: approvalstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.approvalstatus AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'DELEGATED',
    'EXPIRED'
);


ALTER TYPE public.approvalstatus OWNER TO postgres;

--
-- Name: articlestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.articlestatus AS ENUM (
    'draft',
    'published',
    'archived'
);


ALTER TYPE public.articlestatus OWNER TO postgres;

--
-- Name: assetstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.assetstatus AS ENUM (
    'assigned',
    'returned',
    'damaged',
    'lost'
);


ALTER TYPE public.assetstatus OWNER TO postgres;

--
-- Name: assettype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.assettype AS ENUM (
    'uniform',
    'mobile_device',
    'equipment',
    'tools'
);


ALTER TYPE public.assettype OWNER TO postgres;

--
-- Name: assignmentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.assignmentstatus AS ENUM (
    'ACTIVE',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.assignmentstatus OWNER TO postgres;

--
-- Name: assignmenttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.assignmenttype AS ENUM (
    'PERMANENT',
    'TEMPORARY',
    'TRIAL'
);


ALTER TYPE public.assignmenttype OWNER TO postgres;

--
-- Name: attendancestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.attendancestatus AS ENUM (
    'present',
    'absent',
    'late',
    'half_day',
    'on_leave'
);


ALTER TYPE public.attendancestatus OWNER TO postgres;

--
-- Name: auditaction; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.auditaction AS ENUM (
    'CREATE',
    'UPDATE',
    'DELETE',
    'READ',
    'LOGIN',
    'LOGOUT',
    'APPROVE',
    'REJECT',
    'EXPORT'
);


ALTER TYPE public.auditaction OWNER TO postgres;

--
-- Name: automationactiontype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.automationactiontype AS ENUM (
    'CREATE_WORKFLOW',
    'UPDATE_WORKFLOW',
    'SEND_NOTIFICATION',
    'SEND_EMAIL',
    'SEND_SMS',
    'UPDATE_RECORD',
    'WEBHOOK_CALL',
    'CUSTOM_SCRIPT'
);


ALTER TYPE public.automationactiontype OWNER TO postgres;

--
-- Name: automationstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.automationstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'PAUSED',
    'ERROR'
);


ALTER TYPE public.automationstatus OWNER TO postgres;

--
-- Name: automationtriggertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.automationtriggertype AS ENUM (
    'MANUAL',
    'SCHEDULED',
    'EVENT',
    'CONDITION',
    'WEBHOOK'
);


ALTER TYPE public.automationtriggertype OWNER TO postgres;

--
-- Name: bedstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bedstatus AS ENUM (
    'available',
    'occupied',
    'reserved'
);


ALTER TYPE public.bedstatus OWNER TO postgres;

--
-- Name: bonustype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.bonustype AS ENUM (
    'PERFORMANCE',
    'ATTENDANCE',
    'SEASONAL',
    'SPECIAL'
);


ALTER TYPE public.bonustype OWNER TO postgres;

--
-- Name: chatstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.chatstatus AS ENUM (
    'waiting',
    'active',
    'ended',
    'transferred'
);


ALTER TYPE public.chatstatus OWNER TO postgres;

--
-- Name: codstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.codstatus AS ENUM (
    'pending',
    'collected',
    'deposited',
    'reconciled'
);


ALTER TYPE public.codstatus OWNER TO postgres;

--
-- Name: courierstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.courierstatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'ON_LEAVE',
    'TERMINATED',
    'ONBOARDING',
    'SUSPENDED',
    'Active',
    'Not Active',
    'Resigned',
    'Onboarding',
    'Leave',
    'Processing',
    'Rejected',
    'Failed Onboarding',
    'RUN AWAY',
    'Suspended',
    'Pending Contract',
    'Resignation Requested',
    'Vacation'
);


ALTER TYPE public.courierstatus OWNER TO postgres;

--
-- Name: customerfeedbackstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.customerfeedbackstatus AS ENUM (
    'pending',
    'reviewed',
    'responded',
    'resolved',
    'escalated',
    'closed'
);


ALTER TYPE public.customerfeedbackstatus OWNER TO postgres;

--
-- Name: deliverystatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.deliverystatus AS ENUM (
    'pending',
    'in_transit',
    'delivered',
    'failed',
    'returned'
);


ALTER TYPE public.deliverystatus OWNER TO postgres;

--
-- Name: dispatchpriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dispatchpriority AS ENUM (
    'URGENT',
    'HIGH',
    'NORMAL',
    'LOW'
);


ALTER TYPE public.dispatchpriority OWNER TO postgres;

--
-- Name: dispatchstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.dispatchstatus AS ENUM (
    'PENDING',
    'ASSIGNED',
    'ACCEPTED',
    'REJECTED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.dispatchstatus OWNER TO postgres;

--
-- Name: documentcategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.documentcategory AS ENUM (
    'Procedures',
    'Policies',
    'Training',
    'Reports',
    'Templates',
    'Guidelines',
    'Other'
);


ALTER TYPE public.documentcategory OWNER TO postgres;

--
-- Name: documententity; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.documententity AS ENUM (
    'COURIER',
    'VEHICLE'
);


ALTER TYPE public.documententity OWNER TO postgres;

--
-- Name: documenttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.documenttype AS ENUM (
    'DRIVER_LICENSE',
    'VEHICLE_REGISTRATION',
    'INSURANCE',
    'MULKIYA',
    'IQAMA',
    'PASSPORT',
    'CONTRACT',
    'OTHER'
);


ALTER TYPE public.documenttype OWNER TO postgres;

--
-- Name: escalationlevel; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.escalationlevel AS ENUM (
    'none',
    'level_1',
    'level_2',
    'level_3',
    'management'
);


ALTER TYPE public.escalationlevel OWNER TO postgres;

--
-- Name: faultstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.faultstatus AS ENUM (
    'OUR_FAULT',
    'OTHER_PARTY',
    'SHARED',
    'NO_FAULT',
    'PENDING'
);


ALTER TYPE public.faultstatus OWNER TO postgres;

--
-- Name: feedbackcategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.feedbackcategory AS ENUM (
    'general',
    'feature_request',
    'bug_report',
    'complaint',
    'compliment',
    'suggestion'
);


ALTER TYPE public.feedbackcategory OWNER TO postgres;

--
-- Name: feedbacksentiment; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.feedbacksentiment AS ENUM (
    'positive',
    'neutral',
    'negative'
);


ALTER TYPE public.feedbacksentiment OWNER TO postgres;

--
-- Name: feedbackstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.feedbackstatus AS ENUM (
    'new',
    'reviewed',
    'in_progress',
    'completed',
    'dismissed'
);


ALTER TYPE public.feedbackstatus OWNER TO postgres;

--
-- Name: feedbacktype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.feedbacktype AS ENUM (
    'delivery',
    'courier',
    'service',
    'app',
    'support',
    'general'
);


ALTER TYPE public.feedbacktype OWNER TO postgres;

--
-- Name: fuelprovider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.fuelprovider AS ENUM (
    'ARAMCO',
    'ADNOC',
    'PETROL',
    'OTHER'
);


ALTER TYPE public.fuelprovider OWNER TO postgres;

--
-- Name: fueltype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.fueltype AS ENUM (
    'GASOLINE',
    'DIESEL',
    'ELECTRIC',
    'HYBRID'
);


ALTER TYPE public.fueltype OWNER TO postgres;

--
-- Name: handoverstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.handoverstatus AS ENUM (
    'PENDING',
    'APPROVED',
    'REJECTED',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.handoverstatus OWNER TO postgres;

--
-- Name: handovertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.handovertype AS ENUM (
    'SHIFT_START',
    'SHIFT_END',
    'VEHICLE_SWAP',
    'EMERGENCY',
    'MAINTENANCE'
);


ALTER TYPE public.handovertype OWNER TO postgres;

--
-- Name: incidentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.incidentstatus AS ENUM (
    'reported',
    'investigating',
    'resolved',
    'closed'
);


ALTER TYPE public.incidentstatus OWNER TO postgres;

--
-- Name: incidenttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.incidenttype AS ENUM (
    'accident',
    'theft',
    'damage',
    'violation',
    'other'
);


ALTER TYPE public.incidenttype OWNER TO postgres;

--
-- Name: inspectionstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.inspectionstatus AS ENUM (
    'PASSED',
    'FAILED',
    'CONDITIONAL',
    'PENDING'
);


ALTER TYPE public.inspectionstatus OWNER TO postgres;

--
-- Name: inspectiontype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.inspectiontype AS ENUM (
    'PRE_TRIP',
    'POST_TRIP',
    'PERIODIC',
    'SAFETY',
    'REGISTRATION',
    'ACCIDENT'
);


ALTER TYPE public.inspectiontype OWNER TO postgres;

--
-- Name: leavestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.leavestatus AS ENUM (
    'pending',
    'approved',
    'rejected',
    'cancelled'
);


ALTER TYPE public.leavestatus OWNER TO postgres;

--
-- Name: leavetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.leavetype AS ENUM (
    'annual',
    'sick',
    'emergency',
    'unpaid'
);


ALTER TYPE public.leavetype OWNER TO postgres;

--
-- Name: loanstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.loanstatus AS ENUM (
    'active',
    'completed',
    'cancelled'
);


ALTER TYPE public.loanstatus OWNER TO postgres;

--
-- Name: logtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.logtype AS ENUM (
    'DAILY_LOG',
    'FUEL_REFILL',
    'TRIP',
    'DELIVERY'
);


ALTER TYPE public.logtype OWNER TO postgres;

--
-- Name: maintenancestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.maintenancestatus AS ENUM (
    'SCHEDULED',
    'IN_PROGRESS',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.maintenancestatus OWNER TO postgres;

--
-- Name: maintenancetype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.maintenancetype AS ENUM (
    'ROUTINE',
    'PREVENTIVE',
    'CORRECTIVE',
    'BREAKDOWN',
    'UPGRADE'
);


ALTER TYPE public.maintenancetype OWNER TO postgres;

--
-- Name: organizationrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.organizationrole AS ENUM (
    'OWNER',
    'ADMIN',
    'MANAGER',
    'VIEWER'
);


ALTER TYPE public.organizationrole OWNER TO postgres;

--
-- Name: ownershiptype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ownershiptype AS ENUM (
    'OWNED',
    'LEASED',
    'RENTED'
);


ALTER TYPE public.ownershiptype OWNER TO postgres;

--
-- Name: paymentstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.paymentstatus AS ENUM (
    'PENDING',
    'APPROVED',
    'PAID'
);


ALTER TYPE public.paymentstatus OWNER TO postgres;

--
-- Name: projecttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.projecttype AS ENUM (
    'ECOMMERCE',
    'FOOD',
    'WAREHOUSE',
    'BARQ',
    'MIXED'
);


ALTER TYPE public.projecttype OWNER TO postgres;

--
-- Name: qualitymetrictype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.qualitymetrictype AS ENUM (
    'DELIVERY_QUALITY',
    'CUSTOMER_SATISFACTION',
    'VEHICLE_CONDITION',
    'COURIER_PERFORMANCE',
    'PACKAGE_HANDLING',
    'TIMELINESS',
    'COMPLIANCE'
);


ALTER TYPE public.qualitymetrictype OWNER TO postgres;

--
-- Name: queuepriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.queuepriority AS ENUM (
    'CRITICAL',
    'URGENT',
    'HIGH',
    'NORMAL',
    'LOW'
);


ALTER TYPE public.queuepriority OWNER TO postgres;

--
-- Name: queuestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.queuestatus AS ENUM (
    'QUEUED',
    'PROCESSING',
    'ASSIGNED',
    'COMPLETED',
    'EXPIRED',
    'CANCELLED'
);


ALTER TYPE public.queuestatus OWNER TO postgres;

--
-- Name: roomstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.roomstatus AS ENUM (
    'available',
    'occupied',
    'maintenance'
);


ALTER TYPE public.roomstatus OWNER TO postgres;

--
-- Name: routestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.routestatus AS ENUM (
    'planned',
    'assigned',
    'in_progress',
    'completed',
    'cancelled'
);


ALTER TYPE public.routestatus OWNER TO postgres;

--
-- Name: serviceprovider; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.serviceprovider AS ENUM (
    'IN_HOUSE',
    'AUTHORIZED_DEALER',
    'THIRD_PARTY'
);


ALTER TYPE public.serviceprovider OWNER TO postgres;

--
-- Name: slapriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.slapriority AS ENUM (
    'CRITICAL',
    'HIGH',
    'MEDIUM',
    'LOW'
);


ALTER TYPE public.slapriority OWNER TO postgres;

--
-- Name: slastatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.slastatus AS ENUM (
    'ACTIVE',
    'BREACHED',
    'AT_RISK',
    'MET',
    'EXPIRED'
);


ALTER TYPE public.slastatus OWNER TO postgres;

--
-- Name: slatype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.slatype AS ENUM (
    'DELIVERY_TIME',
    'RESPONSE_TIME',
    'PICKUP_TIME',
    'RESOLUTION_TIME',
    'UPTIME',
    'QUALITY_SCORE'
);


ALTER TYPE public.slatype OWNER TO postgres;

--
-- Name: sponsorshipstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.sponsorshipstatus AS ENUM (
    'AJEER',
    'INHOUSE',
    'TRIAL',
    'FREELANCER'
);


ALTER TYPE public.sponsorshipstatus OWNER TO postgres;

--
-- Name: subscriptionplan; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.subscriptionplan AS ENUM (
    'FREE',
    'BASIC',
    'PROFESSIONAL',
    'ENTERPRISE'
);


ALTER TYPE public.subscriptionplan OWNER TO postgres;

--
-- Name: subscriptionstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.subscriptionstatus AS ENUM (
    'TRIAL',
    'ACTIVE',
    'SUSPENDED',
    'CANCELLED'
);


ALTER TYPE public.subscriptionstatus OWNER TO postgres;

--
-- Name: ticketcategory; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketcategory AS ENUM (
    'hr',
    'vehicle',
    'accommodation',
    'finance',
    'operations',
    'it',
    'other'
);


ALTER TYPE public.ticketcategory OWNER TO postgres;

--
-- Name: ticketpriority; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketpriority AS ENUM (
    'low',
    'medium',
    'high',
    'urgent'
);


ALTER TYPE public.ticketpriority OWNER TO postgres;

--
-- Name: ticketstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ticketstatus AS ENUM (
    'open',
    'in_progress',
    'pending',
    'resolved',
    'closed'
);


ALTER TYPE public.ticketstatus OWNER TO postgres;

--
-- Name: triggereventtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.triggereventtype AS ENUM (
    'RECORD_CREATED',
    'RECORD_UPDATED',
    'RECORD_DELETED',
    'WORKFLOW_STARTED',
    'WORKFLOW_COMPLETED',
    'WORKFLOW_FAILED',
    'APPROVAL_REQUESTED',
    'APPROVAL_APPROVED',
    'APPROVAL_REJECTED',
    'SLA_WARNING',
    'SLA_BREACHED',
    'CUSTOM'
);


ALTER TYPE public.triggereventtype OWNER TO postgres;

--
-- Name: triggertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.triggertype AS ENUM (
    'MANUAL',
    'AUTOMATIC',
    'SCHEDULED',
    'EVENT_BASED',
    'API',
    'WEBHOOK'
);


ALTER TYPE public.triggertype OWNER TO postgres;

--
-- Name: vehiclecondition; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.vehiclecondition AS ENUM (
    'EXCELLENT',
    'GOOD',
    'FAIR',
    'POOR'
);


ALTER TYPE public.vehiclecondition OWNER TO postgres;

--
-- Name: vehiclestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.vehiclestatus AS ENUM (
    'ACTIVE',
    'MAINTENANCE',
    'INACTIVE',
    'RETIRED',
    'REPAIR',
    'Active Car',
    'Maintenance',
    'Needs Driver',
    'Returned',
    'BARQ STAFF',
    'New',
    'To Courier',
    'To Agency',
    'For Sale',
    'Sold',
    'Available'
);


ALTER TYPE public.vehiclestatus OWNER TO postgres;

--
-- Name: vehicletype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.vehicletype AS ENUM (
    'MOTORCYCLE',
    'CAR',
    'VAN',
    'TRUCK',
    'BICYCLE',
    'Sedan',
    'SUV',
    'Pickup',
    'Van'
);


ALTER TYPE public.vehicletype OWNER TO postgres;

--
-- Name: workflowstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.workflowstatus AS ENUM (
    'DRAFT',
    'IN_PROGRESS',
    'PENDING_APPROVAL',
    'APPROVED',
    'REJECTED',
    'COMPLETED',
    'CANCELLED'
);


ALTER TYPE public.workflowstatus OWNER TO postgres;

--
-- Name: zonestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.zonestatus AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'MAINTENANCE'
);


ALTER TYPE public.zonestatus OWNER TO postgres;

--
-- Name: audit_trigger_function(); Type: FUNCTION; Schema: barq; Owner: ramiz_new
--

CREATE FUNCTION barq.audit_trigger_function() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO barq.audit_logs (
        log_id,
        entity_type,
        entity_id,
        action,
        user_id,
        old_values,
        new_values
    ) VALUES (
        gen_random_uuid()::text,
        TG_TABLE_NAME,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.barq_id::TEXT
            ELSE NEW.barq_id::TEXT
        END,
        TG_OP,
        COALESCE(current_setting('app.current_user', true), 'system'),
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
    );

    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$;


ALTER FUNCTION barq.audit_trigger_function() OWNER TO ramiz_new;

--
-- Name: audit_trigger_vehicles(); Type: FUNCTION; Schema: barq; Owner: ramiz_new
--

CREATE FUNCTION barq.audit_trigger_vehicles() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    INSERT INTO barq.audit_logs (
        entity_type,
        entity_id,
        action,
        user_id,
        old_values,
        new_values
    ) VALUES (
        TG_TABLE_NAME,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.plate_number::TEXT
            ELSE NEW.plate_number::TEXT
        END,
        TG_OP,
        COALESCE(current_setting('app.current_user', true), 'system'),
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN row_to_json(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN row_to_json(NEW) ELSE NULL END
    );
    
    RETURN CASE
        WHEN TG_OP = 'DELETE' THEN OLD
        ELSE NEW
    END;
END;
$$;


ALTER FUNCTION barq.audit_trigger_vehicles() OWNER TO ramiz_new;

--
-- Name: refresh_courier_summary(); Type: FUNCTION; Schema: barq; Owner: ramiz_new
--

CREATE FUNCTION barq.refresh_courier_summary() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_active_courier_summary;
END;
$$;


ALTER FUNCTION barq.refresh_courier_summary() OWNER TO ramiz_new;

--
-- Name: update_updated_at_and_version(); Type: FUNCTION; Schema: barq; Owner: postgres
--

CREATE FUNCTION barq.update_updated_at_and_version() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at := CURRENT_TIMESTAMP;
    NEW.version := COALESCE(OLD.version, 0) + 1;
    RETURN NEW;
END;
$$;


ALTER FUNCTION barq.update_updated_at_and_version() OWNER TO postgres;

--
-- Name: FUNCTION update_updated_at_and_version(); Type: COMMENT; Schema: barq; Owner: postgres
--

COMMENT ON FUNCTION barq.update_updated_at_and_version() IS 'Fast trigger function for core tables that are guaranteed to have updated_at and version columns. Use this for high-traffic tables like couriers and vehicles.';


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: barq; Owner: ramiz_new
--

CREATE FUNCTION barq.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    has_version boolean;
    has_updated_at boolean;
BEGIN
    -- Check if updated_at column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = TG_TABLE_SCHEMA 
        AND table_name = TG_TABLE_NAME 
        AND column_name = 'updated_at'
    ) INTO has_updated_at;
    
    -- Check if version column exists
    SELECT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = TG_TABLE_SCHEMA 
        AND table_name = TG_TABLE_NAME 
        AND column_name = 'version'
    ) INTO has_version;
    
    -- Update updated_at if column exists
    IF has_updated_at THEN
        NEW.updated_at := CURRENT_TIMESTAMP;
    END IF;
    
    -- Bump version if column exists
    IF has_version THEN
        NEW.version := COALESCE(OLD.version, 0) + 1;
    END IF;
    
    RETURN NEW;
END;
$$;


ALTER FUNCTION barq.update_updated_at_column() OWNER TO ramiz_new;

--
-- Name: FUNCTION update_updated_at_column(); Type: COMMENT; Schema: barq; Owner: ramiz_new
--

COMMENT ON FUNCTION barq.update_updated_at_column() IS 'Defensive trigger function that updates updated_at and increments version columns if they exist. Safe to use on any table.';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.audit_logs (
    log_id character varying(36) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id character varying(100) NOT NULL,
    action character varying(50) NOT NULL,
    user_id character varying(255) NOT NULL,
    user_email character varying(255),
    old_values jsonb,
    new_values jsonb,
    ip_address inet,
    user_agent text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE barq.audit_logs OWNER TO ramiz_new;

--
-- Name: cdc_queue; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.cdc_queue (
    id integer NOT NULL,
    operation character varying(10) NOT NULL,
    table_name character varying(100) NOT NULL,
    data jsonb NOT NULL,
    processed boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    processed_at timestamp with time zone,
    CONSTRAINT cdc_operation_check CHECK (((operation)::text = ANY ((ARRAY['INSERT'::character varying, 'UPDATE'::character varying, 'DELETE'::character varying])::text[])))
);


ALTER TABLE barq.cdc_queue OWNER TO ramiz_new;

--
-- Name: TABLE cdc_queue; Type: COMMENT; Schema: barq; Owner: ramiz_new
--

COMMENT ON TABLE barq.cdc_queue IS 'Change Data Capture queue for tracking database changes. Operations: INSERT, UPDATE, DELETE.';


--
-- Name: COLUMN cdc_queue.operation; Type: COMMENT; Schema: barq; Owner: ramiz_new
--

COMMENT ON COLUMN barq.cdc_queue.operation IS 'Type of database operation: INSERT, UPDATE, or DELETE';


--
-- Name: COLUMN cdc_queue.processed; Type: COMMENT; Schema: barq; Owner: ramiz_new
--

COMMENT ON COLUMN barq.cdc_queue.processed IS 'Whether this CDC event has been processed by consumers';


--
-- Name: cdc_queue_id_seq; Type: SEQUENCE; Schema: barq; Owner: ramiz_new
--

CREATE SEQUENCE barq.cdc_queue_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE barq.cdc_queue_id_seq OWNER TO ramiz_new;

--
-- Name: cdc_queue_id_seq; Type: SEQUENCE OWNED BY; Schema: barq; Owner: ramiz_new
--

ALTER SEQUENCE barq.cdc_queue_id_seq OWNED BY barq.cdc_queue.id;


--
-- Name: couriers; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.couriers (
    barq_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    email character varying(255),
    phone character varying(20),
    city character varying(50),
    status public.courierstatus DEFAULT 'Onboarding'::public.courierstatus NOT NULL,
    employment_type character varying(50),
    sponsorship_status public.sponsorshipstatus,
    project character varying(100),
    join_date date,
    department character varying(50),
    nationality character varying(50),
    iqama_number character varying(50),
    iqama_expiry date,
    license_number character varying(50),
    license_expiry date,
    passport_number character varying(50),
    passport_expiry date,
    bank_account character varying(100),
    iban character varying(100),
    supervisor character varying(255),
    emergency_contact character varying(20),
    own_car boolean DEFAULT false,
    own_car_plate character varying(20),
    own_car_make character varying(50),
    own_car_model character varying(50),
    last_working_day date,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    version integer DEFAULT 0,
    is_deleted boolean DEFAULT false,
    CONSTRAINT chk_email CHECK (((email)::text ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'::text))
);


ALTER TABLE barq.couriers OWNER TO ramiz_new;

--
-- Name: leave_approvals; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.leave_approvals (
    approval_id character varying(36) NOT NULL,
    request_id character varying(36) NOT NULL,
    approver_id character varying(255) NOT NULL,
    approver_name character varying(255),
    approval_level character varying(50) NOT NULL,
    decision character varying(50),
    comments text,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_approval_level CHECK (((approval_level)::text = ANY ((ARRAY['Manager'::character varying, 'HR'::character varying, 'Final'::character varying])::text[]))),
    CONSTRAINT chk_decision CHECK (((decision)::text = ANY ((ARRAY['Approved'::character varying, 'Rejected'::character varying, 'Pending'::character varying])::text[])))
);


ALTER TABLE barq.leave_approvals OWNER TO ramiz_new;

--
-- Name: leave_requests; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.leave_requests (
    request_id character varying(36) NOT NULL,
    courier_id character varying(36) NOT NULL,
    leave_type character varying(50) NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    days_requested integer GENERATED ALWAYS AS (((end_date - start_date) + 1)) STORED,
    reason text,
    status character varying(50) DEFAULT 'Pending'::character varying NOT NULL,
    payroll_month character varying(20),
    manager_id character varying(36),
    hr_approver_id character varying(36),
    final_approver_id character varying(36),
    rejection_reason text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    submitted_by character varying(255),
    approved_at timestamp with time zone,
    rejected_at timestamp with time zone,
    version integer DEFAULT 0,
    CONSTRAINT chk_leave_status CHECK (((status)::text = ANY ((ARRAY['Pending'::character varying, 'Approved'::character varying, 'Rejected'::character varying, 'Cancelled'::character varying])::text[]))),
    CONSTRAINT chk_leave_type CHECK (((leave_type)::text = ANY ((ARRAY['Annual'::character varying, 'Sick'::character varying, 'Emergency'::character varying, 'Unpaid'::character varying, 'Other'::character varying, 'Personal'::character varying])::text[]))),
    CONSTRAINT leave_requests_check CHECK ((end_date >= start_date))
);


ALTER TABLE barq.leave_requests OWNER TO ramiz_new;

--
-- Name: vehicle_assignments; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.vehicle_assignments (
    assignment_id character varying(36) NOT NULL,
    vehicle_plate character varying(20) NOT NULL,
    courier_id character varying(36) NOT NULL,
    assigned_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    returned_date timestamp with time zone,
    odometer_start integer,
    odometer_end integer,
    fuel_consumed numeric(10,2),
    notes text,
    assignment_type character varying(50) DEFAULT 'Regular'::character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    CONSTRAINT chk_assignment_dates CHECK (((returned_date IS NULL) OR (returned_date >= assigned_date))),
    CONSTRAINT vehicle_assignments_check CHECK ((odometer_end >= odometer_start)),
    CONSTRAINT vehicle_assignments_fuel_consumed_check CHECK ((fuel_consumed >= (0)::numeric)),
    CONSTRAINT vehicle_assignments_odometer_start_check CHECK ((odometer_start >= 0))
);


ALTER TABLE barq.vehicle_assignments OWNER TO ramiz_new;

--
-- Name: vehicles; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.vehicles (
    plate_number character varying(20) NOT NULL,
    make character varying(50) NOT NULL,
    model character varying(50) NOT NULL,
    year integer,
    vehicle_type public.vehicletype,
    status public.vehiclestatus DEFAULT 'Available'::public.vehiclestatus NOT NULL,
    assigned_to character varying(36),
    assignment_date date,
    fuel_type character varying(20),
    capacity_kg integer,
    insurance_provider character varying(100),
    insurance_expiry date,
    registration_expiry date,
    last_maintenance date,
    next_maintenance date,
    odometer_reading integer,
    purchase_date date,
    purchase_cost numeric(10,2),
    department character varying(50),
    city character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    created_by character varying(255),
    version integer DEFAULT 0,
    is_deleted boolean DEFAULT false,
    CONSTRAINT vehicles_capacity_kg_check CHECK ((capacity_kg > 0)),
    CONSTRAINT vehicles_odometer_reading_check CHECK ((odometer_reading >= 0)),
    CONSTRAINT vehicles_purchase_cost_check CHECK ((purchase_cost >= (0)::numeric)),
    CONSTRAINT vehicles_year_check CHECK (((year >= 2000) AND ((year)::numeric <= (EXTRACT(year FROM CURRENT_DATE) + (1)::numeric))))
);


ALTER TABLE barq.vehicles OWNER TO ramiz_new;

--
-- Name: workflow_instances; Type: TABLE; Schema: barq; Owner: ramiz_new
--

CREATE TABLE barq.workflow_instances (
    instance_id character varying(36) NOT NULL,
    workflow_type character varying(100) NOT NULL,
    entity_type character varying(50) NOT NULL,
    entity_id character varying(100) NOT NULL,
    current_state character varying(50) NOT NULL,
    previous_state character varying(50),
    initiated_by character varying(255) NOT NULL,
    assigned_to character varying(255),
    priority character varying(20) DEFAULT 'Normal'::character varying,
    due_date timestamp with time zone,
    data jsonb DEFAULT '{}'::jsonb NOT NULL,
    metadata jsonb DEFAULT '{}'::jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    completed_at timestamp with time zone,
    version integer DEFAULT 0,
    CONSTRAINT chk_priority CHECK (((priority)::text = ANY ((ARRAY['Low'::character varying, 'Normal'::character varying, 'High'::character varying, 'Urgent'::character varying])::text[])))
);


ALTER TABLE barq.workflow_instances OWNER TO ramiz_new;

--
-- Name: accident_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.accident_logs (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    courier_id integer,
    accident_date date NOT NULL,
    accident_time time without time zone,
    accident_type character varying(20) NOT NULL,
    severity character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    location_description text NOT NULL,
    city character varying(100),
    latitude numeric(10,8),
    longitude numeric(11,8),
    street_address character varying(500),
    weather_conditions character varying(100),
    road_conditions character varying(100),
    visibility character varying(50),
    traffic_conditions character varying(100),
    fault_status character varying(20),
    our_vehicle_at_fault boolean,
    accident_description text NOT NULL,
    courier_statement text,
    witness_statements text,
    other_party_name character varying(200),
    other_party_phone character varying(20),
    other_party_insurance character varying(200),
    other_party_policy_number character varying(100),
    other_party_vehicle_plate character varying(20),
    other_party_vehicle_details text,
    any_injuries boolean,
    injury_details text,
    casualties_count integer,
    hospitalization_required boolean,
    hospital_name character varying(300),
    police_notified boolean,
    police_report_number character varying(100),
    police_station character varying(200),
    police_officer_name character varying(200),
    police_officer_badge character varying(50),
    vehicle_damage_description text,
    estimated_repair_cost numeric(10,2),
    actual_repair_cost numeric(10,2),
    vehicle_towed boolean,
    tow_company character varying(200),
    tow_cost numeric(10,2),
    insurance_claim_filed boolean,
    insurance_claim_number character varying(100),
    insurance_claim_amount numeric(10,2),
    insurance_approved_amount numeric(10,2),
    insurance_claim_status character varying(50),
    claim_filed_date date,
    claim_settlement_date date,
    repair_start_date date,
    repair_completion_date date,
    repair_shop_name character varying(300),
    repair_shop_location character varying(300),
    total_cost numeric(10,2),
    insurance_covered numeric(10,2),
    out_of_pocket_cost numeric(10,2),
    lost_revenue numeric(10,2),
    vehicle_downtime_days integer,
    vehicle_available_date date,
    investigated_by character varying(200),
    investigation_date date,
    investigation_findings text,
    corrective_actions text,
    courier_action_taken character varying(100),
    courier_notes text,
    accident_photos_json text,
    police_report_url character varying(500),
    insurance_documents_json text,
    repair_invoices_json text,
    requires_follow_up boolean,
    follow_up_date date,
    follow_up_notes text,
    reported_by character varying(200),
    reported_date timestamp without time zone,
    notes text,
    legal_action_required boolean,
    legal_case_number character varying(100),
    legal_status character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.accident_logs FORCE ROW LEVEL SECURITY;


ALTER TABLE public.accident_logs OWNER TO postgres;

--
-- Name: accident_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.accident_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.accident_logs_id_seq OWNER TO postgres;

--
-- Name: accident_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.accident_logs_id_seq OWNED BY public.accident_logs.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: allocations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.allocations (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    bed_id integer NOT NULL,
    allocation_date date NOT NULL,
    release_date date,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.allocations FORCE ROW LEVEL SECURITY;


ALTER TABLE public.allocations OWNER TO postgres;

--
-- Name: allocations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.allocations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.allocations_id_seq OWNER TO postgres;

--
-- Name: allocations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.allocations_id_seq OWNED BY public.allocations.id;


--
-- Name: api_keys; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.api_keys (
    name character varying(100) NOT NULL,
    key_prefix character varying(10) NOT NULL,
    key_hash character varying(255) NOT NULL,
    description text,
    user_id integer NOT NULL,
    status character varying(20) NOT NULL,
    expires_at timestamp without time zone,
    last_used_at timestamp without time zone,
    scopes json NOT NULL,
    ip_whitelist json,
    rate_limit_per_minute integer NOT NULL,
    rate_limit_per_hour integer NOT NULL,
    rate_limit_per_day integer NOT NULL,
    total_requests integer NOT NULL,
    last_request_ip character varying(45),
    extra_data json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.api_keys FORCE ROW LEVEL SECURITY;


ALTER TABLE public.api_keys OWNER TO postgres;

--
-- Name: api_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.api_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.api_keys_id_seq OWNER TO postgres;

--
-- Name: api_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.api_keys_id_seq OWNED BY public.api_keys.id;


--
-- Name: approval_chain_approvers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_chain_approvers (
    approval_chain_id integer NOT NULL,
    user_id integer NOT NULL,
    role_id integer,
    level integer NOT NULL,
    is_required boolean,
    "order" integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.approval_chain_approvers FORCE ROW LEVEL SECURITY;


ALTER TABLE public.approval_chain_approvers OWNER TO postgres;

--
-- Name: approval_chain_approvers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_chain_approvers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_chain_approvers_id_seq OWNER TO postgres;

--
-- Name: approval_chain_approvers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_chain_approvers_id_seq OWNED BY public.approval_chain_approvers.id;


--
-- Name: approval_chains; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_chains (
    name character varying NOT NULL,
    description text,
    workflow_template_id integer,
    levels integer NOT NULL,
    is_sequential boolean,
    allow_delegation boolean,
    auto_escalate boolean,
    escalation_hours integer,
    is_active boolean,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.approval_chains FORCE ROW LEVEL SECURITY;


ALTER TABLE public.approval_chains OWNER TO postgres;

--
-- Name: approval_chains_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_chains_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_chains_id_seq OWNER TO postgres;

--
-- Name: approval_chains_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_chains_id_seq OWNED BY public.approval_chains.id;


--
-- Name: approval_requests; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.approval_requests (
    workflow_instance_id integer NOT NULL,
    approval_chain_id integer NOT NULL,
    approver_id integer NOT NULL,
    delegated_to_id integer,
    level integer NOT NULL,
    status public.approvalstatus,
    comments text,
    approved_at timestamp without time zone,
    rejected_at timestamp without time zone,
    delegated_at timestamp without time zone,
    expires_at timestamp without time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.approval_requests FORCE ROW LEVEL SECURITY;


ALTER TABLE public.approval_requests OWNER TO postgres;

--
-- Name: approval_requests_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.approval_requests_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.approval_requests_id_seq OWNER TO postgres;

--
-- Name: approval_requests_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.approval_requests_id_seq OWNED BY public.approval_requests.id;


--
-- Name: assets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.assets (
    id integer NOT NULL,
    asset_type public.assettype NOT NULL,
    courier_id integer NOT NULL,
    issue_date date NOT NULL,
    return_date date,
    condition character varying DEFAULT 'good'::character varying NOT NULL,
    status public.assetstatus DEFAULT 'assigned'::public.assetstatus NOT NULL,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.assets FORCE ROW LEVEL SECURITY;


ALTER TABLE public.assets OWNER TO postgres;

--
-- Name: assets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.assets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assets_id_seq OWNER TO postgres;

--
-- Name: assets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.assets_id_seq OWNED BY public.assets.id;


--
-- Name: assignments; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.assignments (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    assignment_number character varying(100) NOT NULL,
    assignment_type character varying(50) NOT NULL,
    courier_id integer,
    vehicle_id integer,
    asset_id integer,
    zone_id integer,
    start_date date NOT NULL,
    end_date date,
    status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    is_active boolean DEFAULT true,
    is_permanent boolean DEFAULT false,
    assigned_by integer,
    assigned_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    terminated_by integer,
    terminated_date timestamp(6) without time zone,
    termination_reason text,
    location character varying(255),
    shift_type character varying(50),
    notes text,
    attachments_urls text[],
    metadata jsonb,
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp(6) without time zone
);


ALTER TABLE public.assignments OWNER TO ramiz_new;

--
-- Name: assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.assignments_id_seq OWNER TO ramiz_new;

--
-- Name: assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.assignments_id_seq OWNED BY public.assignments.id;


--
-- Name: attendance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attendance (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    date date NOT NULL,
    check_in time without time zone,
    check_out time without time zone,
    status public.attendancestatus NOT NULL,
    hours_worked integer DEFAULT 0 NOT NULL,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.attendance FORCE ROW LEVEL SECURITY;


ALTER TABLE public.attendance OWNER TO postgres;

--
-- Name: attendance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.attendance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.attendance_id_seq OWNER TO postgres;

--
-- Name: attendance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.attendance_id_seq OWNED BY public.attendance.id;


--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    user_id integer,
    username character varying(255),
    action public.auditaction NOT NULL,
    resource_type character varying(100) NOT NULL,
    resource_id integer,
    old_values json,
    new_values json,
    ip_address character varying(45),
    user_agent text,
    endpoint character varying(255),
    http_method character varying(10),
    extra_metadata json,
    description text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.audit_logs_id_seq OWNER TO postgres;

--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- Name: automation_execution_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.automation_execution_logs (
    automation_id integer NOT NULL,
    workflow_instance_id integer,
    started_at timestamp without time zone NOT NULL,
    completed_at timestamp without time zone,
    status character varying NOT NULL,
    trigger_data json,
    action_result json,
    error_message text,
    retry_count integer,
    execution_time_ms integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.automation_execution_logs FORCE ROW LEVEL SECURITY;


ALTER TABLE public.automation_execution_logs OWNER TO postgres;

--
-- Name: automation_execution_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.automation_execution_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.automation_execution_logs_id_seq OWNER TO postgres;

--
-- Name: automation_execution_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.automation_execution_logs_id_seq OWNED BY public.automation_execution_logs.id;


--
-- Name: backups; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.backups (
    name character varying(200) NOT NULL,
    description text,
    backup_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    error_message text,
    created_by_id integer,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    duration_seconds integer,
    size_bytes bigint,
    compressed_size_bytes bigint,
    record_count integer,
    table_count integer,
    storage_type character varying(20) NOT NULL,
    storage_path character varying(500),
    storage_bucket character varying(200),
    storage_key character varying(500),
    is_compressed boolean NOT NULL,
    compression_algorithm character varying(20),
    is_encrypted boolean NOT NULL,
    encryption_algorithm character varying(20),
    is_verified boolean NOT NULL,
    verified_at timestamp without time zone,
    checksum character varying(128),
    checksum_algorithm character varying(20),
    expires_at timestamp without time zone,
    is_pinned boolean NOT NULL,
    last_restored_at timestamp without time zone,
    restoration_count integer NOT NULL,
    last_restored_by_id integer,
    database_version character varying(50),
    application_version character varying(50),
    environment character varying(50),
    tags character varying(500),
    schedule_name character varying(100),
    is_scheduled boolean NOT NULL,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.backups FORCE ROW LEVEL SECURITY;


ALTER TABLE public.backups OWNER TO postgres;

--
-- Name: backups_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.backups_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.backups_id_seq OWNER TO postgres;

--
-- Name: backups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.backups_id_seq OWNED BY public.backups.id;


--
-- Name: beds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.beds (
    id integer NOT NULL,
    room_id integer NOT NULL,
    bed_number integer NOT NULL,
    status public.bedstatus DEFAULT 'available'::public.bedstatus NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.beds FORCE ROW LEVEL SECURITY;


ALTER TABLE public.beds OWNER TO postgres;

--
-- Name: beds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.beds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.beds_id_seq OWNER TO postgres;

--
-- Name: beds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.beds_id_seq OWNED BY public.beds.id;


--
-- Name: bonuses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.bonuses (
    courier_id integer NOT NULL,
    bonus_type public.bonustype NOT NULL,
    amount numeric(10,2) NOT NULL,
    bonus_date date NOT NULL,
    payment_status public.paymentstatus,
    approved_by integer,
    approval_date date,
    description character varying,
    notes character varying,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.bonuses FORCE ROW LEVEL SECURITY;


ALTER TABLE public.bonuses OWNER TO postgres;

--
-- Name: bonuses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.bonuses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.bonuses_id_seq OWNER TO postgres;

--
-- Name: bonuses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.bonuses_id_seq OWNED BY public.bonuses.id;


--
-- Name: buildings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.buildings (
    id integer NOT NULL,
    name character varying NOT NULL,
    address text NOT NULL,
    total_rooms integer DEFAULT 0 NOT NULL,
    total_capacity integer DEFAULT 0 NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.buildings FORCE ROW LEVEL SECURITY;


ALTER TABLE public.buildings OWNER TO postgres;

--
-- Name: buildings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.buildings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.buildings_id_seq OWNER TO postgres;

--
-- Name: buildings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.buildings_id_seq OWNED BY public.buildings.id;


--
-- Name: canned_responses; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.canned_responses (
    id integer NOT NULL,
    title character varying(100) NOT NULL,
    shortcut character varying(50),
    content text NOT NULL,
    category character varying(100) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_public boolean DEFAULT true NOT NULL,
    usage_count integer DEFAULT 0 NOT NULL,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.canned_responses FORCE ROW LEVEL SECURITY;


ALTER TABLE public.canned_responses OWNER TO postgres;

--
-- Name: canned_responses_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.canned_responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.canned_responses_id_seq OWNER TO postgres;

--
-- Name: canned_responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.canned_responses_id_seq OWNED BY public.canned_responses.id;


--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_messages (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    session_id integer NOT NULL,
    sender_id integer NOT NULL,
    message text NOT NULL,
    is_agent boolean NOT NULL,
    is_system boolean NOT NULL,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.chat_messages FORCE ROW LEVEL SECURITY;


ALTER TABLE public.chat_messages OWNER TO postgres;

--
-- Name: TABLE chat_messages; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.chat_messages IS 'Chat messages';


--
-- Name: COLUMN chat_messages.session_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_messages.session_id IS 'Chat session ID';


--
-- Name: COLUMN chat_messages.sender_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_messages.sender_id IS 'Message sender user ID';


--
-- Name: COLUMN chat_messages.message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_messages.message IS 'Message content';


--
-- Name: COLUMN chat_messages.is_agent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_messages.is_agent IS 'Is from agent';


--
-- Name: COLUMN chat_messages.is_system; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_messages.is_system IS 'Is system message';


--
-- Name: chat_messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_messages_id_seq OWNER TO postgres;

--
-- Name: chat_messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_messages_id_seq OWNED BY public.chat_messages.id;


--
-- Name: chat_sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_sessions (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    session_id character varying(50) NOT NULL,
    customer_id integer NOT NULL,
    agent_id integer,
    status public.chatstatus NOT NULL,
    started_at timestamp with time zone,
    ended_at timestamp with time zone,
    initial_message character varying(500),
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.chat_sessions FORCE ROW LEVEL SECURITY;


ALTER TABLE public.chat_sessions OWNER TO postgres;

--
-- Name: TABLE chat_sessions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.chat_sessions IS 'Live chat sessions';


--
-- Name: COLUMN chat_sessions.session_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.session_id IS 'Unique session ID';


--
-- Name: COLUMN chat_sessions.customer_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.customer_id IS 'Customer user ID';


--
-- Name: COLUMN chat_sessions.agent_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.agent_id IS 'Support agent user ID';


--
-- Name: COLUMN chat_sessions.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.status IS 'Session status';


--
-- Name: COLUMN chat_sessions.started_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.started_at IS 'When agent joined';


--
-- Name: COLUMN chat_sessions.ended_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.ended_at IS 'When session ended';


--
-- Name: COLUMN chat_sessions.initial_message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.chat_sessions.initial_message IS 'Initial customer message';


--
-- Name: chat_sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.chat_sessions_id_seq OWNER TO postgres;

--
-- Name: chat_sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_sessions_id_seq OWNED BY public.chat_sessions.id;


--
-- Name: cod_transactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cod_transactions (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    collection_date date NOT NULL,
    deposit_date date,
    status public.codstatus DEFAULT 'pending'::public.codstatus NOT NULL,
    reference_number character varying,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer
);


ALTER TABLE public.cod_transactions OWNER TO postgres;

--
-- Name: cod_transactions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cod_transactions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.cod_transactions_id_seq OWNER TO postgres;

--
-- Name: cod_transactions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cod_transactions_id_seq OWNED BY public.cod_transactions.id;


--
-- Name: courier_vehicle_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.courier_vehicle_assignments (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    vehicle_id integer NOT NULL,
    assignment_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    start_mileage integer,
    end_mileage integer,
    assigned_by character varying(200),
    assignment_reason text,
    termination_reason text,
    notes text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.courier_vehicle_assignments FORCE ROW LEVEL SECURITY;


ALTER TABLE public.courier_vehicle_assignments OWNER TO postgres;

--
-- Name: courier_vehicle_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.courier_vehicle_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.courier_vehicle_assignments_id_seq OWNER TO postgres;

--
-- Name: courier_vehicle_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.courier_vehicle_assignments_id_seq OWNED BY public.courier_vehicle_assignments.id;


--
-- Name: couriers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.couriers (
    id integer NOT NULL,
    barq_id character varying(50) NOT NULL,
    full_name character varying(200) NOT NULL,
    email character varying(255),
    mobile_number character varying(20) NOT NULL,
    employee_id character varying(50),
    status public.courierstatus NOT NULL,
    sponsorship_status public.sponsorshipstatus,
    project_type character varying(20),
    "position" character varying(100),
    city character varying(100),
    joining_date date,
    last_working_day date,
    date_of_birth date,
    national_id character varying(50),
    nationality character varying(100),
    iqama_number character varying(50),
    iqama_expiry_date date,
    passport_number character varying(50),
    passport_expiry_date date,
    license_number character varying(50),
    license_expiry_date date,
    license_type character varying(20),
    bank_account_number character varying(50),
    bank_name character varying(100),
    iban character varying(50),
    jahez_driver_id character varying(50),
    hunger_rider_id character varying(50),
    mrsool_courier_id character varying(50),
    current_vehicle_id integer,
    supervisor_name character varying(200),
    accommodation_building_id integer,
    accommodation_room_id integer,
    notes text,
    emergency_contact_name character varying(200),
    emergency_contact_phone character varying(20),
    performance_score numeric(5,2),
    total_deliveries integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    fms_asset_id integer,
    fms_driver_id integer,
    fms_last_sync character varying(50),
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.couriers FORCE ROW LEVEL SECURITY;


ALTER TABLE public.couriers OWNER TO postgres;

--
-- Name: couriers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.couriers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.couriers_id_seq OWNER TO postgres;

--
-- Name: couriers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.couriers_id_seq OWNED BY public.couriers.id;


--
-- Name: customer_feedbacks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_feedbacks (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    feedback_number character varying(50) NOT NULL,
    feedback_type public.feedbacktype NOT NULL,
    status public.customerfeedbackstatus DEFAULT 'pending'::public.customerfeedbackstatus NOT NULL,
    delivery_id integer,
    courier_id integer,
    order_number character varying(100),
    customer_name character varying(200),
    customer_email character varying(200),
    customer_phone character varying(50),
    is_verified_customer boolean DEFAULT false,
    overall_rating integer NOT NULL,
    delivery_speed_rating integer,
    courier_behavior_rating integer,
    package_condition_rating integer,
    communication_rating integer,
    feedback_title character varying(200),
    feedback_text text NOT NULL,
    sentiment public.feedbacksentiment,
    category character varying(100),
    tags text,
    is_complaint boolean DEFAULT false,
    is_compliment boolean DEFAULT false,
    response_text text,
    responded_by_id integer,
    responded_at timestamp without time zone,
    response_time_hours numeric(10,2),
    resolution_text text,
    resolved_by_id integer,
    resolved_at timestamp without time zone,
    resolution_satisfaction integer,
    is_escalated boolean DEFAULT false,
    escalated_at timestamp without time zone,
    escalated_to_id integer,
    escalation_reason text,
    compensation_amount numeric(10,2) DEFAULT 0.0,
    refund_amount numeric(10,2) DEFAULT 0.0,
    action_taken text,
    source character varying(50),
    device_type character varying(50),
    submitted_at timestamp without time zone NOT NULL,
    requires_followup boolean DEFAULT false,
    followup_date timestamp without time zone,
    followup_completed boolean DEFAULT false,
    followup_notes text,
    internal_notes text,
    priority character varying(20) DEFAULT 'normal'::character varying,
    organization_id integer NOT NULL
);


ALTER TABLE public.customer_feedbacks OWNER TO postgres;

--
-- Name: customer_feedbacks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customer_feedbacks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customer_feedbacks_id_seq OWNER TO postgres;

--
-- Name: customer_feedbacks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customer_feedbacks_id_seq OWNED BY public.customer_feedbacks.id;


--
-- Name: dashboards; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dashboards (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    widgets jsonb DEFAULT '[]'::jsonb NOT NULL,
    layout jsonb,
    user_id integer NOT NULL,
    is_default boolean DEFAULT false NOT NULL,
    is_shared boolean DEFAULT false NOT NULL,
    refresh_interval_seconds integer DEFAULT 300 NOT NULL,
    filters jsonb,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.dashboards FORCE ROW LEVEL SECURITY;


ALTER TABLE public.dashboards OWNER TO postgres;

--
-- Name: dashboards_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dashboards_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dashboards_id_seq OWNER TO postgres;

--
-- Name: dashboards_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dashboards_id_seq OWNED BY public.dashboards.id;


--
-- Name: deliveries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.deliveries (
    id integer NOT NULL,
    tracking_number character varying NOT NULL,
    courier_id integer,
    pickup_address text NOT NULL,
    delivery_address text NOT NULL,
    status public.deliverystatus DEFAULT 'pending'::public.deliverystatus NOT NULL,
    pickup_time timestamp without time zone,
    delivery_time timestamp without time zone,
    cod_amount integer DEFAULT 0 NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.deliveries FORCE ROW LEVEL SECURITY;


ALTER TABLE public.deliveries OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.deliveries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.deliveries_id_seq OWNER TO postgres;

--
-- Name: deliveries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.deliveries_id_seq OWNED BY public.deliveries.id;


--
-- Name: dispatch_assignments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dispatch_assignments (
    assignment_number character varying(50) NOT NULL,
    status public.dispatchstatus NOT NULL,
    priority public.dispatchpriority,
    delivery_id integer NOT NULL,
    courier_id integer,
    zone_id integer,
    created_at_time timestamp without time zone NOT NULL,
    assigned_at timestamp without time zone,
    accepted_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    assignment_algorithm character varying(50),
    distance_to_pickup_km numeric(10,2),
    estimated_time_minutes integer,
    courier_current_load integer,
    courier_max_capacity integer,
    courier_rating numeric(3,2),
    rejection_reason text,
    rejected_at timestamp without time zone,
    rejection_count integer,
    is_reassignment boolean,
    previous_courier_id integer,
    reassignment_reason text,
    actual_completion_time_minutes integer,
    performance_variance integer,
    assigned_by_id integer,
    assignment_notes text,
    last_location_update timestamp without time zone,
    current_latitude numeric(10,8),
    current_longitude numeric(11,8),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.dispatch_assignments FORCE ROW LEVEL SECURITY;


ALTER TABLE public.dispatch_assignments OWNER TO postgres;

--
-- Name: COLUMN dispatch_assignments.assignment_algorithm; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.assignment_algorithm IS 'nearest, load_balanced, priority_based, manual';


--
-- Name: COLUMN dispatch_assignments.distance_to_pickup_km; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.distance_to_pickup_km IS 'Distance from courier to pickup';


--
-- Name: COLUMN dispatch_assignments.estimated_time_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.estimated_time_minutes IS 'Estimated completion time';


--
-- Name: COLUMN dispatch_assignments.courier_current_load; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.courier_current_load IS 'Number of active deliveries';


--
-- Name: COLUMN dispatch_assignments.courier_rating; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.courier_rating IS 'Courier rating at assignment time';


--
-- Name: COLUMN dispatch_assignments.rejection_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.rejection_count IS 'Number of times rejected';


--
-- Name: COLUMN dispatch_assignments.performance_variance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.dispatch_assignments.performance_variance IS 'Difference from estimated time';


--
-- Name: dispatch_assignments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatch_assignments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatch_assignments_id_seq OWNER TO postgres;

--
-- Name: dispatch_assignments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatch_assignments_id_seq OWNED BY public.dispatch_assignments.id;


--
-- Name: dispatch_rules; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dispatch_rules (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    organization_id integer NOT NULL,
    rule_code character varying(50) NOT NULL,
    rule_name character varying(200) NOT NULL,
    description text,
    priority integer,
    is_active boolean,
    conditions json NOT NULL,
    actions json NOT NULL,
    algorithm character varying(50),
    max_distance_km numeric(10,2),
    max_courier_load integer,
    min_courier_rating numeric(3,2),
    zone_ids text,
    applies_to_all_zones boolean,
    time_start character varying(8),
    time_end character varying(8),
    days_of_week character varying(20),
    times_triggered integer,
    successful_assignments integer,
    failed_assignments integer,
    created_by_id integer
);


ALTER TABLE public.dispatch_rules OWNER TO postgres;

--
-- Name: dispatch_rules_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dispatch_rules_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dispatch_rules_id_seq OWNER TO postgres;

--
-- Name: dispatch_rules_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dispatch_rules_id_seq OWNED BY public.dispatch_rules.id;


--
-- Name: documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.documents (
    id integer NOT NULL,
    entity_type public.documententity NOT NULL,
    entity_id integer NOT NULL,
    document_type public.documenttype NOT NULL,
    document_number character varying(100),
    document_name character varying(200) NOT NULL,
    file_url character varying(500) NOT NULL,
    file_type character varying(50),
    file_size integer,
    issue_date date,
    expiry_date date,
    issuing_authority character varying(200),
    notes character varying(500),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.documents FORCE ROW LEVEL SECURITY;


ALTER TABLE public.documents OWNER TO postgres;

--
-- Name: documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.documents_id_seq OWNER TO postgres;

--
-- Name: documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.documents_id_seq OWNED BY public.documents.id;


--
-- Name: driver_orders; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.driver_orders (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    courier_id integer,
    platform character varying(50),
    platform_order_id character varying(100),
    platform_driver_id character varying(50),
    order_number character varying(100) NOT NULL,
    order_date timestamp(6) without time zone NOT NULL,
    delivery_date timestamp(6) without time zone,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    order_type character varying(50),
    pickup_address text,
    delivery_address text,
    customer_name character varying(255),
    customer_phone character varying(20),
    distance_km numeric(8,2),
    delivery_time_minutes integer,
    delivery_fee numeric(10,2),
    cod_amount numeric(10,2),
    incentive_amount numeric(10,2),
    total_earnings numeric(10,2),
    rating numeric(3,2),
    feedback text,
    notes text,
    raw_data jsonb,
    sync_date timestamp(6) without time zone,
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp(6) without time zone
);


ALTER TABLE public.driver_orders OWNER TO ramiz_new;

--
-- Name: driver_orders_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.driver_orders_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.driver_orders_id_seq OWNER TO ramiz_new;

--
-- Name: driver_orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.driver_orders_id_seq OWNED BY public.driver_orders.id;


--
-- Name: faqs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.faqs (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    question character varying(500) NOT NULL,
    answer text NOT NULL,
    category character varying(100) NOT NULL,
    "order" integer NOT NULL,
    is_active boolean NOT NULL,
    view_count integer NOT NULL,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.faqs FORCE ROW LEVEL SECURITY;


ALTER TABLE public.faqs OWNER TO postgres;

--
-- Name: TABLE faqs; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.faqs IS 'Frequently asked questions';


--
-- Name: COLUMN faqs.question; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs.question IS 'FAQ question';


--
-- Name: COLUMN faqs.answer; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs.answer IS 'FAQ answer (Markdown)';


--
-- Name: COLUMN faqs.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs.category IS 'FAQ category';


--
-- Name: COLUMN faqs."order"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs."order" IS 'Display order';


--
-- Name: COLUMN faqs.is_active; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs.is_active IS 'Active status';


--
-- Name: COLUMN faqs.view_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.faqs.view_count IS 'View count';


--
-- Name: faqs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.faqs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.faqs_id_seq OWNER TO postgres;

--
-- Name: faqs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.faqs_id_seq OWNED BY public.faqs.id;


--
-- Name: feedback_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feedback_templates (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    template_code character varying(50) NOT NULL,
    template_name character varying(200) NOT NULL,
    template_type public.feedbacktype NOT NULL,
    subject character varying(200),
    body text NOT NULL,
    sentiment_type public.feedbacksentiment,
    is_active boolean DEFAULT true,
    usage_count integer DEFAULT 0,
    created_by_id integer,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.feedback_templates FORCE ROW LEVEL SECURITY;


ALTER TABLE public.feedback_templates OWNER TO postgres;

--
-- Name: feedback_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feedback_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feedback_templates_id_seq OWNER TO postgres;

--
-- Name: feedback_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feedback_templates_id_seq OWNED BY public.feedback_templates.id;


--
-- Name: feedbacks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.feedbacks (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    user_id integer,
    subject character varying(255) NOT NULL,
    message text NOT NULL,
    category public.feedbackcategory NOT NULL,
    rating integer,
    status public.feedbackstatus NOT NULL,
    response text,
    responded_by integer,
    organization_id integer
);


ALTER TABLE public.feedbacks OWNER TO postgres;

--
-- Name: TABLE feedbacks; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.feedbacks IS 'Customer feedback';


--
-- Name: COLUMN feedbacks.user_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.user_id IS 'User who submitted feedback';


--
-- Name: COLUMN feedbacks.subject; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.subject IS 'Feedback subject';


--
-- Name: COLUMN feedbacks.message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.message IS 'Feedback message';


--
-- Name: COLUMN feedbacks.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.category IS 'Feedback category';


--
-- Name: COLUMN feedbacks.rating; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.rating IS 'Rating 1-5 stars';


--
-- Name: COLUMN feedbacks.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.status IS 'Processing status';


--
-- Name: COLUMN feedbacks.response; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.response IS 'Response to feedback';


--
-- Name: COLUMN feedbacks.responded_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.feedbacks.responded_by IS 'User who responded';


--
-- Name: feedbacks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.feedbacks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.feedbacks_id_seq OWNER TO postgres;

--
-- Name: feedbacks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.feedbacks_id_seq OWNED BY public.feedbacks.id;


--
-- Name: fuel_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.fuel_logs (
    vehicle_id integer NOT NULL,
    courier_id integer,
    fuel_date date NOT NULL,
    odometer_reading numeric(10,2) NOT NULL,
    fuel_quantity numeric(10,2) NOT NULL,
    fuel_cost numeric(10,2) NOT NULL,
    cost_per_liter numeric(10,2) NOT NULL,
    fuel_station character varying(200),
    fuel_type character varying(50),
    receipt_number character varying(100),
    receipt_image_url character varying(500),
    notes character varying(500),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.fuel_logs FORCE ROW LEVEL SECURITY;


ALTER TABLE public.fuel_logs OWNER TO postgres;

--
-- Name: fuel_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.fuel_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.fuel_logs_id_seq OWNER TO postgres;

--
-- Name: fuel_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.fuel_logs_id_seq OWNED BY public.fuel_logs.id;


--
-- Name: handovers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.handovers (
    handover_number character varying(50) NOT NULL,
    handover_type public.handovertype NOT NULL,
    status public.handoverstatus NOT NULL,
    from_courier_id integer NOT NULL,
    to_courier_id integer NOT NULL,
    vehicle_id integer,
    vehicle_mileage_start integer,
    vehicle_fuel_level numeric(5,2),
    vehicle_condition text,
    pending_deliveries_count integer,
    pending_cod_amount numeric(10,2),
    scheduled_at timestamp without time zone,
    started_at timestamp without time zone,
    completed_at timestamp without time zone,
    from_courier_signature character varying(500),
    to_courier_signature character varying(500),
    witness_id integer,
    approved_by_id integer,
    approved_at timestamp without time zone,
    rejection_reason text,
    photos text,
    notes text,
    checklist_completed text,
    discrepancies_reported text,
    discrepancy_resolved character varying(20),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.handovers FORCE ROW LEVEL SECURITY;


ALTER TABLE public.handovers OWNER TO postgres;

--
-- Name: COLUMN handovers.handover_number; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.handover_number IS 'Unique handover ID';


--
-- Name: COLUMN handovers.vehicle_mileage_start; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.vehicle_mileage_start IS 'Odometer reading at handover';


--
-- Name: COLUMN handovers.vehicle_fuel_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.vehicle_fuel_level IS 'Fuel level percentage 0-100';


--
-- Name: COLUMN handovers.vehicle_condition; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.vehicle_condition IS 'Vehicle condition notes';


--
-- Name: COLUMN handovers.pending_cod_amount; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.pending_cod_amount IS 'COD amount being transferred';


--
-- Name: COLUMN handovers.scheduled_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.scheduled_at IS 'Planned handover time';


--
-- Name: COLUMN handovers.from_courier_signature; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.from_courier_signature IS 'Digital signature or URL';


--
-- Name: COLUMN handovers.to_courier_signature; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.to_courier_signature IS 'Digital signature or URL';


--
-- Name: COLUMN handovers.witness_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.witness_id IS 'Supervisor/witness';


--
-- Name: COLUMN handovers.photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.photos IS 'Comma-separated photo URLs';


--
-- Name: COLUMN handovers.checklist_completed; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.checklist_completed IS 'JSON array of completed checklist items';


--
-- Name: COLUMN handovers.discrepancies_reported; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.discrepancies_reported IS 'Issues found during handover';


--
-- Name: COLUMN handovers.discrepancy_resolved; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.handovers.discrepancy_resolved IS 'pending, resolved, escalated';


--
-- Name: handovers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.handovers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.handovers_id_seq OWNER TO postgres;

--
-- Name: handovers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.handovers_id_seq OWNED BY public.handovers.id;


--
-- Name: incidents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.incidents (
    id integer NOT NULL,
    incident_type public.incidenttype NOT NULL,
    courier_id integer,
    vehicle_id integer,
    incident_date date NOT NULL,
    description text NOT NULL,
    status public.incidentstatus DEFAULT 'reported'::public.incidentstatus NOT NULL,
    resolution text,
    cost integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.incidents FORCE ROW LEVEL SECURITY;


ALTER TABLE public.incidents OWNER TO postgres;

--
-- Name: incidents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.incidents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.incidents_id_seq OWNER TO postgres;

--
-- Name: incidents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.incidents_id_seq OWNED BY public.incidents.id;


--
-- Name: integrations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.integrations (
    name character varying(100) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    integration_type character varying(50) NOT NULL,
    status character varying(20) NOT NULL,
    is_enabled boolean NOT NULL,
    config json NOT NULL,
    credentials json,
    base_url character varying(500),
    webhook_url character varying(500),
    callback_url character varying(500),
    oauth_client_id character varying(255),
    oauth_client_secret character varying(255),
    oauth_access_token text,
    oauth_refresh_token text,
    oauth_token_expires_at timestamp without time zone,
    last_health_check timestamp without time zone,
    last_error text,
    last_error_at timestamp without time zone,
    error_count integer NOT NULL,
    success_count integer NOT NULL,
    rate_limit_per_minute integer,
    rate_limit_per_hour integer,
    rate_limit_per_day integer,
    version character varying(20),
    extra_data json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.integrations FORCE ROW LEVEL SECURITY;


ALTER TABLE public.integrations OWNER TO postgres;

--
-- Name: integrations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.integrations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.integrations_id_seq OWNER TO postgres;

--
-- Name: integrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.integrations_id_seq OWNED BY public.integrations.id;


--
-- Name: kb_articles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kb_articles (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    slug character varying(255) NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    summary character varying(500),
    category character varying(100) NOT NULL,
    tags text,
    status public.articlestatus NOT NULL,
    version integer NOT NULL,
    author_id integer NOT NULL,
    view_count integer NOT NULL,
    helpful_count integer NOT NULL,
    not_helpful_count integer NOT NULL,
    meta_description character varying(255),
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.kb_articles FORCE ROW LEVEL SECURITY;


ALTER TABLE public.kb_articles OWNER TO postgres;

--
-- Name: TABLE kb_articles; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.kb_articles IS 'Knowledge base articles';


--
-- Name: COLUMN kb_articles.slug; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.slug IS 'URL-friendly slug';


--
-- Name: COLUMN kb_articles.title; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.title IS 'Article title';


--
-- Name: COLUMN kb_articles.content; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.content IS 'Article content (Markdown)';


--
-- Name: COLUMN kb_articles.summary; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.summary IS 'Short summary';


--
-- Name: COLUMN kb_articles.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.category IS 'Article category';


--
-- Name: COLUMN kb_articles.tags; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.tags IS 'Comma-separated tags';


--
-- Name: COLUMN kb_articles.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.status IS 'Publication status';


--
-- Name: COLUMN kb_articles.version; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.version IS 'Article version';


--
-- Name: COLUMN kb_articles.author_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.author_id IS 'Article author';


--
-- Name: COLUMN kb_articles.view_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.view_count IS 'View count';


--
-- Name: COLUMN kb_articles.helpful_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.helpful_count IS 'Helpful votes';


--
-- Name: COLUMN kb_articles.not_helpful_count; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.not_helpful_count IS 'Not helpful votes';


--
-- Name: COLUMN kb_articles.meta_description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.kb_articles.meta_description IS 'SEO meta description';


--
-- Name: kb_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kb_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kb_articles_id_seq OWNER TO postgres;

--
-- Name: kb_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kb_articles_id_seq OWNED BY public.kb_articles.id;


--
-- Name: kb_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kb_categories (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    slug character varying(100) NOT NULL,
    description text,
    parent_id integer,
    icon character varying(50),
    "order" integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    is_public boolean DEFAULT true NOT NULL,
    article_count integer DEFAULT 0 NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.kb_categories FORCE ROW LEVEL SECURITY;


ALTER TABLE public.kb_categories OWNER TO postgres;

--
-- Name: kb_categories_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kb_categories_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kb_categories_id_seq OWNER TO postgres;

--
-- Name: kb_categories_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kb_categories_id_seq OWNED BY public.kb_categories.id;


--
-- Name: kpis; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.kpis (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(100) NOT NULL,
    description text,
    category character varying(100) NOT NULL,
    current_value numeric(20,4),
    previous_value numeric(20,4),
    target_value numeric(20,4),
    warning_threshold numeric(20,4),
    critical_threshold numeric(20,4),
    trend character varying(10),
    trend_percentage numeric(10,2),
    period character varying(20) NOT NULL,
    period_start timestamp with time zone,
    period_end timestamp with time zone,
    calculation_formula text,
    unit character varying(50),
    is_active boolean DEFAULT true NOT NULL,
    historical_data jsonb,
    last_calculated_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.kpis FORCE ROW LEVEL SECURITY;


ALTER TABLE public.kpis OWNER TO postgres;

--
-- Name: kpis_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.kpis_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kpis_id_seq OWNER TO postgres;

--
-- Name: kpis_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.kpis_id_seq OWNED BY public.kpis.id;


--
-- Name: leaves; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.leaves (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    leave_type public.leavetype NOT NULL,
    start_date date NOT NULL,
    end_date date NOT NULL,
    days integer NOT NULL,
    status public.leavestatus DEFAULT 'pending'::public.leavestatus NOT NULL,
    reason text,
    approved_by integer,
    approved_at date,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.leaves FORCE ROW LEVEL SECURITY;


ALTER TABLE public.leaves OWNER TO postgres;

--
-- Name: leaves_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.leaves_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.leaves_id_seq OWNER TO postgres;

--
-- Name: leaves_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.leaves_id_seq OWNED BY public.leaves.id;


--
-- Name: loans; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.loans (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    amount numeric(10,2) NOT NULL,
    outstanding_balance numeric(10,2) NOT NULL,
    monthly_deduction numeric(10,2) NOT NULL,
    start_date date NOT NULL,
    end_date date,
    status public.loanstatus DEFAULT 'active'::public.loanstatus NOT NULL,
    approved_by integer,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.loans FORCE ROW LEVEL SECURITY;


ALTER TABLE public.loans OWNER TO postgres;

--
-- Name: loans_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.loans_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.loans_id_seq OWNER TO postgres;

--
-- Name: loans_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.loans_id_seq OWNED BY public.loans.id;


--
-- Name: metric_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metric_snapshots (
    id integer NOT NULL,
    metric_name character varying(100) NOT NULL,
    metric_type character varying(50) NOT NULL,
    value numeric(20,4) NOT NULL,
    dimensions jsonb,
    "timestamp" timestamp with time zone NOT NULL,
    tags jsonb,
    source character varying(100),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.metric_snapshots FORCE ROW LEVEL SECURITY;


ALTER TABLE public.metric_snapshots OWNER TO postgres;

--
-- Name: metric_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metric_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.metric_snapshots_id_seq OWNER TO postgres;

--
-- Name: metric_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metric_snapshots_id_seq OWNED BY public.metric_snapshots.id;


--
-- Name: notification_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification_settings (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    organization_id integer NOT NULL,
    setting_code character varying(50) NOT NULL,
    setting_name character varying(200) NOT NULL,
    event_type character varying(100) NOT NULL,
    notify_email boolean,
    notify_sms boolean,
    notify_push boolean,
    notify_in_app boolean,
    notify_webhook boolean,
    notify_roles text,
    notify_user_ids text,
    webhook_url character varying(500),
    cooldown_minutes integer,
    batch_delay_minutes integer,
    email_template character varying(100),
    sms_template character varying(100),
    is_active boolean
);


ALTER TABLE public.notification_settings OWNER TO postgres;

--
-- Name: notification_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notification_settings_id_seq OWNER TO postgres;

--
-- Name: notification_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_settings_id_seq OWNED BY public.notification_settings.id;


--
-- Name: notifications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notifications (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    user_id integer,
    courier_id integer,
    notification_type character varying(50) NOT NULL,
    title character varying(255) NOT NULL,
    message text NOT NULL,
    category character varying(50),
    entity_type character varying(50),
    entity_id integer,
    entity_reference character varying(255),
    action_url text,
    action_label character varying(100),
    is_read boolean DEFAULT false,
    read_at timestamp without time zone,
    is_archived boolean DEFAULT false,
    channels jsonb DEFAULT '["in_app"]'::jsonb,
    sent_at timestamp without time zone,
    email_sent boolean DEFAULT false,
    sms_sent boolean DEFAULT false,
    push_sent boolean DEFAULT false,
    priority character varying(20) DEFAULT 'normal'::character varying,
    expires_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    created_by character varying(255)
);


ALTER TABLE public.notifications OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notifications_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.notifications_id_seq OWNER TO postgres;

--
-- Name: notifications_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notifications_id_seq OWNED BY public.notifications.id;


--
-- Name: operations_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.operations_documents (
    id integer NOT NULL,
    doc_number character varying(50),
    doc_name character varying(255) NOT NULL,
    category public.documentcategory DEFAULT 'Other'::public.documentcategory NOT NULL,
    file_name character varying(255),
    file_url character varying(500) NOT NULL,
    file_type character varying(50),
    file_size integer DEFAULT 0,
    version character varying(20) DEFAULT '1.0'::character varying,
    description text,
    is_public character varying(10) DEFAULT 'false'::character varying,
    department character varying(100),
    uploaded_by character varying(200),
    uploader_email character varying(200),
    uploaded_by_id integer,
    view_count integer DEFAULT 0,
    download_count integer DEFAULT 0,
    tags character varying(500),
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.operations_documents FORCE ROW LEVEL SECURITY;


ALTER TABLE public.operations_documents OWNER TO postgres;

--
-- Name: operations_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.operations_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.operations_documents_id_seq OWNER TO postgres;

--
-- Name: operations_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.operations_documents_id_seq OWNED BY public.operations_documents.id;


--
-- Name: operations_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.operations_settings (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    organization_id integer NOT NULL,
    setting_key character varying(100) NOT NULL,
    setting_name character varying(200) NOT NULL,
    setting_group character varying(100) NOT NULL,
    description text,
    value_type character varying(20) NOT NULL,
    string_value text,
    number_value numeric(20,4),
    boolean_value boolean,
    json_value json,
    min_value numeric(20,4),
    max_value numeric(20,4),
    allowed_values text,
    is_active boolean,
    is_system boolean,
    is_readonly boolean,
    last_modified_by_id integer,
    last_modified_at timestamp without time zone
);


ALTER TABLE public.operations_settings OWNER TO postgres;

--
-- Name: operations_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.operations_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.operations_settings_id_seq OWNER TO postgres;

--
-- Name: operations_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.operations_settings_id_seq OWNED BY public.operations_settings.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.orders (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    order_number character varying(100) NOT NULL,
    courier_id integer,
    vehicle_id integer,
    customer_name character varying(255),
    customer_phone character varying(20),
    pickup_address text,
    delivery_address text,
    pickup_latitude numeric(10,8),
    pickup_longitude numeric(11,8),
    delivery_latitude numeric(10,8),
    delivery_longitude numeric(11,8),
    order_date timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    scheduled_date timestamp(6) without time zone,
    pickup_time timestamp(6) without time zone,
    delivery_time timestamp(6) without time zone,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    priority character varying(20) DEFAULT 'normal'::character varying,
    order_type character varying(50),
    payment_method character varying(50),
    cod_amount numeric(10,2),
    delivery_fee numeric(10,2),
    total_amount numeric(10,2),
    distance_km numeric(8,2),
    notes text,
    special_instructions text,
    proof_of_delivery_url text,
    customer_signature_url text,
    rating numeric(3,2),
    customer_feedback text,
    created_by integer,
    assigned_at timestamp(6) without time zone,
    completed_at timestamp(6) without time zone,
    cancelled_at timestamp(6) without time zone,
    cancellation_reason text,
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp(6) without time zone
);


ALTER TABLE public.orders OWNER TO ramiz_new;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.orders_id_seq OWNER TO ramiz_new;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: organization_users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organization_users (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    user_id integer NOT NULL,
    role public.organizationrole DEFAULT 'VIEWER'::public.organizationrole NOT NULL,
    permissions json,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.organization_users OWNER TO postgres;

--
-- Name: organization_users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organization_users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organization_users_id_seq OWNER TO postgres;

--
-- Name: organization_users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organization_users_id_seq OWNED BY public.organization_users.id;


--
-- Name: organizations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organizations (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(100) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    subscription_plan public.subscriptionplan DEFAULT 'FREE'::public.subscriptionplan NOT NULL,
    subscription_status public.subscriptionstatus DEFAULT 'TRIAL'::public.subscriptionstatus NOT NULL,
    max_users integer DEFAULT 5 NOT NULL,
    max_couriers integer DEFAULT 10 NOT NULL,
    max_vehicles integer DEFAULT 10 NOT NULL,
    trial_ends_at timestamp with time zone,
    settings json,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.organizations OWNER TO postgres;

--
-- Name: organizations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organizations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organizations_id_seq OWNER TO postgres;

--
-- Name: organizations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organizations_id_seq OWNED BY public.organizations.id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_reset_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token_hash character varying(256) NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean NOT NULL,
    used_at timestamp with time zone,
    ip_address character varying(45),
    user_agent character varying(500)
);


ALTER TABLE public.password_reset_tokens OWNER TO postgres;

--
-- Name: COLUMN password_reset_tokens.token_hash; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.token_hash IS 'SHA-256 hash of the reset token';


--
-- Name: COLUMN password_reset_tokens.expires_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.expires_at IS 'Token expiration timestamp';


--
-- Name: COLUMN password_reset_tokens.used; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.used IS 'Whether the token has been used';


--
-- Name: COLUMN password_reset_tokens.used_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.used_at IS 'Timestamp when token was used';


--
-- Name: COLUMN password_reset_tokens.ip_address; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.ip_address IS 'IP address of requester (IPv6 compatible)';


--
-- Name: COLUMN password_reset_tokens.user_agent; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.password_reset_tokens.user_agent IS 'User agent of requester';


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.password_reset_tokens_id_seq OWNER TO postgres;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_reset_tokens_id_seq OWNED BY public.password_reset_tokens.id;


--
-- Name: performance_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.performance_data (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    date date NOT NULL,
    orders_completed integer DEFAULT 0 NOT NULL,
    orders_failed integer DEFAULT 0 NOT NULL,
    on_time_deliveries integer DEFAULT 0 NOT NULL,
    late_deliveries integer DEFAULT 0 NOT NULL,
    distance_covered_km numeric(10,2) DEFAULT 0.0 NOT NULL,
    revenue_generated numeric(12,2) DEFAULT 0.0 NOT NULL,
    cod_collected numeric(12,2) DEFAULT 0.0 NOT NULL,
    average_rating numeric(3,2) DEFAULT 0.0 NOT NULL,
    working_hours numeric(5,2) DEFAULT 0.0 NOT NULL,
    efficiency_score numeric(5,2) DEFAULT 0.0 NOT NULL,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.performance_data FORCE ROW LEVEL SECURITY;


ALTER TABLE public.performance_data OWNER TO postgres;

--
-- Name: performance_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.performance_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.performance_data_id_seq OWNER TO postgres;

--
-- Name: performance_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.performance_data_id_seq OWNED BY public.performance_data.id;


--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    name character varying(100) NOT NULL,
    resource character varying(50) NOT NULL,
    action character varying(20) NOT NULL,
    description text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.permissions_id_seq OWNER TO postgres;

--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.permissions_id_seq OWNED BY public.permissions.id;


--
-- Name: priority_queue_entries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.priority_queue_entries (
    queue_number character varying(50) NOT NULL,
    priority public.queuepriority NOT NULL,
    status public.queuestatus NOT NULL,
    delivery_id integer NOT NULL,
    base_priority_score integer NOT NULL,
    time_factor_score integer,
    customer_tier_score integer,
    sla_factor_score integer,
    total_priority_score integer NOT NULL,
    sla_deadline timestamp without time zone NOT NULL,
    sla_buffer_minutes integer,
    warning_threshold timestamp without time zone,
    customer_tier character varying(20),
    is_vip_customer boolean,
    customer_special_instructions text,
    queued_at timestamp without time zone NOT NULL,
    assigned_at timestamp without time zone,
    processing_started_at timestamp without time zone,
    completed_at timestamp without time zone,
    expired_at timestamp without time zone,
    queue_position integer,
    estimated_wait_time_minutes integer,
    required_zone_id integer,
    required_vehicle_type character varying(50),
    required_skills text,
    preferred_courier_id integer,
    excluded_courier_ids text,
    min_courier_rating numeric(3,2),
    delivery_window_start timestamp without time zone,
    delivery_window_end timestamp without time zone,
    max_assignment_attempts integer,
    assignment_attempts integer,
    is_escalated boolean,
    escalated_at timestamp without time zone,
    escalation_reason text,
    escalated_to_id integer,
    time_in_queue_minutes integer,
    was_sla_met boolean,
    sla_breach_minutes integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.priority_queue_entries FORCE ROW LEVEL SECURITY;


ALTER TABLE public.priority_queue_entries OWNER TO postgres;

--
-- Name: COLUMN priority_queue_entries.base_priority_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.base_priority_score IS 'Base score 1-100';


--
-- Name: COLUMN priority_queue_entries.time_factor_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.time_factor_score IS 'Urgency-based score';


--
-- Name: COLUMN priority_queue_entries.customer_tier_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.customer_tier_score IS 'Customer priority score';


--
-- Name: COLUMN priority_queue_entries.sla_factor_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.sla_factor_score IS 'SLA compliance score';


--
-- Name: COLUMN priority_queue_entries.total_priority_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.total_priority_score IS 'Composite priority score';


--
-- Name: COLUMN priority_queue_entries.sla_deadline; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.sla_deadline IS 'Must be delivered by this time';


--
-- Name: COLUMN priority_queue_entries.sla_buffer_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.sla_buffer_minutes IS 'Buffer time before deadline';


--
-- Name: COLUMN priority_queue_entries.warning_threshold; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.warning_threshold IS 'Time to trigger warning';


--
-- Name: COLUMN priority_queue_entries.customer_tier; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.customer_tier IS 'premium, vip, standard, basic';


--
-- Name: COLUMN priority_queue_entries.queue_position; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.queue_position IS 'Position in queue (1=first)';


--
-- Name: COLUMN priority_queue_entries.estimated_wait_time_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.estimated_wait_time_minutes IS 'Estimated time until assignment';


--
-- Name: COLUMN priority_queue_entries.required_vehicle_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.required_vehicle_type IS 'bike, car, van';


--
-- Name: COLUMN priority_queue_entries.required_skills; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.required_skills IS 'JSON array of required courier skills';


--
-- Name: COLUMN priority_queue_entries.excluded_courier_ids; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.excluded_courier_ids IS 'JSON array of excluded courier IDs';


--
-- Name: COLUMN priority_queue_entries.min_courier_rating; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.min_courier_rating IS 'Minimum courier rating required';


--
-- Name: COLUMN priority_queue_entries.delivery_window_start; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.delivery_window_start IS 'Earliest acceptable delivery time';


--
-- Name: COLUMN priority_queue_entries.delivery_window_end; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.delivery_window_end IS 'Latest acceptable delivery time';


--
-- Name: COLUMN priority_queue_entries.time_in_queue_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.time_in_queue_minutes IS 'Total time spent in queue';


--
-- Name: COLUMN priority_queue_entries.sla_breach_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.priority_queue_entries.sla_breach_minutes IS 'Minutes past SLA deadline';


--
-- Name: priority_queue_entries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.priority_queue_entries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.priority_queue_entries_id_seq OWNER TO postgres;

--
-- Name: priority_queue_entries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.priority_queue_entries_id_seq OWNED BY public.priority_queue_entries.id;


--
-- Name: quality_inspections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quality_inspections (
    inspection_number character varying(50) NOT NULL,
    inspection_type public.qualitymetrictype NOT NULL,
    status public.inspectionstatus,
    courier_id integer,
    vehicle_id integer,
    delivery_id integer,
    scheduled_date date NOT NULL,
    inspection_date timestamp without time zone,
    completed_date timestamp without time zone,
    inspector_id integer,
    inspector_notes text,
    overall_score numeric(5,2),
    passed boolean,
    findings text,
    violations_count integer,
    recommendations text,
    requires_followup boolean,
    followup_date date,
    followup_completed boolean,
    corrective_actions text,
    actions_completed boolean,
    completion_verified_by integer,
    photos text,
    attachments text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.quality_inspections FORCE ROW LEVEL SECURITY;


ALTER TABLE public.quality_inspections OWNER TO postgres;

--
-- Name: COLUMN quality_inspections.overall_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_inspections.overall_score IS 'Overall quality score 0-100';


--
-- Name: COLUMN quality_inspections.findings; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_inspections.findings IS 'JSON array of inspection findings';


--
-- Name: COLUMN quality_inspections.corrective_actions; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_inspections.corrective_actions IS 'Required corrective actions';


--
-- Name: COLUMN quality_inspections.photos; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_inspections.photos IS 'Comma-separated photo URLs';


--
-- Name: COLUMN quality_inspections.attachments; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_inspections.attachments IS 'Comma-separated document URLs';


--
-- Name: quality_inspections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quality_inspections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quality_inspections_id_seq OWNER TO postgres;

--
-- Name: quality_inspections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quality_inspections_id_seq OWNED BY public.quality_inspections.id;


--
-- Name: quality_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.quality_metrics (
    metric_code character varying(50) NOT NULL,
    metric_name character varying(200) NOT NULL,
    metric_type public.qualitymetrictype NOT NULL,
    description text,
    target_value numeric(10,2) NOT NULL,
    unit_of_measure character varying(50),
    min_acceptable numeric(10,2),
    max_acceptable numeric(10,2),
    weight numeric(5,2),
    is_critical boolean,
    is_active boolean,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.quality_metrics FORCE ROW LEVEL SECURITY;


ALTER TABLE public.quality_metrics OWNER TO postgres;

--
-- Name: COLUMN quality_metrics.target_value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.target_value IS 'Target/threshold value';


--
-- Name: COLUMN quality_metrics.unit_of_measure; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.unit_of_measure IS '%, minutes, count, etc.';


--
-- Name: COLUMN quality_metrics.min_acceptable; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.min_acceptable IS 'Minimum acceptable value';


--
-- Name: COLUMN quality_metrics.max_acceptable; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.max_acceptable IS 'Maximum acceptable value';


--
-- Name: COLUMN quality_metrics.weight; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.weight IS 'Weight in overall quality score';


--
-- Name: COLUMN quality_metrics.is_critical; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.quality_metrics.is_critical IS 'Critical quality metric';


--
-- Name: quality_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.quality_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.quality_metrics_id_seq OWNER TO postgres;

--
-- Name: quality_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.quality_metrics_id_seq OWNED BY public.quality_metrics.id;


--
-- Name: reports; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.reports (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    report_type character varying(50) NOT NULL,
    status character varying(20) DEFAULT 'PENDING'::character varying NOT NULL,
    format character varying(20) DEFAULT 'PDF'::character varying NOT NULL,
    parameters jsonb,
    generated_at timestamp with time zone,
    scheduled_at timestamp with time zone,
    file_path character varying(500),
    file_size_bytes integer,
    generated_by_user_id integer,
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.reports FORCE ROW LEVEL SECURITY;


ALTER TABLE public.reports OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.reports_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.reports_id_seq OWNER TO postgres;

--
-- Name: reports_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.reports_id_seq OWNED BY public.reports.id;


--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    name character varying(50) NOT NULL,
    display_name character varying(100) NOT NULL,
    description text,
    is_system_role boolean,
    is_active boolean,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO postgres;

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: rooms; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.rooms (
    id integer NOT NULL,
    building_id integer NOT NULL,
    room_number character varying NOT NULL,
    capacity integer NOT NULL,
    occupied integer DEFAULT 0 NOT NULL,
    status public.roomstatus DEFAULT 'available'::public.roomstatus NOT NULL,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.rooms FORCE ROW LEVEL SECURITY;


ALTER TABLE public.rooms OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.rooms_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.rooms_id_seq OWNER TO postgres;

--
-- Name: rooms_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.rooms_id_seq OWNED BY public.rooms.id;


--
-- Name: routes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.routes (
    id integer NOT NULL,
    route_name character varying NOT NULL,
    courier_id integer,
    date date NOT NULL,
    waypoints json,
    total_distance integer,
    estimated_time integer,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    route_number character varying(50),
    status public.routestatus DEFAULT 'planned'::public.routestatus,
    zone_id integer,
    scheduled_start_time timestamp without time zone,
    scheduled_end_time timestamp without time zone,
    actual_start_time timestamp without time zone,
    actual_end_time timestamp without time zone,
    start_location character varying(500),
    start_latitude numeric(10,8),
    start_longitude numeric(11,8),
    end_location character varying(500),
    end_latitude numeric(10,8),
    end_longitude numeric(11,8),
    total_stops integer DEFAULT 0,
    actual_distance_km numeric(10,2),
    actual_duration_minutes integer,
    is_optimized boolean DEFAULT false,
    optimization_algorithm character varying(50),
    optimization_score numeric(5,2),
    total_deliveries integer DEFAULT 0,
    completed_deliveries integer DEFAULT 0,
    failed_deliveries integer DEFAULT 0,
    avg_time_per_stop_minutes numeric(10,2),
    distance_variance_km numeric(10,2),
    time_variance_minutes integer,
    special_instructions text,
    internal_notes text,
    created_by_id integer,
    assigned_by_id integer,
    assigned_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.routes FORCE ROW LEVEL SECURITY;


ALTER TABLE public.routes OWNER TO postgres;

--
-- Name: routes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.routes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.routes_id_seq OWNER TO postgres;

--
-- Name: routes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.routes_id_seq OWNED BY public.routes.id;


--
-- Name: salaries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.salaries (
    id integer NOT NULL,
    courier_id integer NOT NULL,
    month integer NOT NULL,
    year integer NOT NULL,
    base_salary numeric(10,2) NOT NULL,
    allowances numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    deductions numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    loan_deduction numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    gosi_employee numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    gross_salary numeric(10,2) NOT NULL,
    net_salary numeric(10,2) NOT NULL,
    payment_date date,
    notes character varying,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.salaries FORCE ROW LEVEL SECURITY;


ALTER TABLE public.salaries OWNER TO postgres;

--
-- Name: salaries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.salaries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.salaries_id_seq OWNER TO postgres;

--
-- Name: salaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.salaries_id_seq OWNED BY public.salaries.id;


--
-- Name: sla_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_definitions (
    sla_code character varying(50) NOT NULL,
    sla_name character varying(200) NOT NULL,
    sla_type public.slatype NOT NULL,
    description text,
    target_value numeric(10,2) NOT NULL,
    unit_of_measure character varying(50),
    warning_threshold numeric(10,2),
    critical_threshold numeric(10,2),
    priority public.slapriority,
    applies_to_zone_id integer,
    applies_to_service_type character varying(50),
    applies_to_customer_tier character varying(50),
    penalty_per_breach numeric(10,2),
    escalation_required boolean,
    measurement_period character varying(50),
    calculation_method text,
    is_active boolean,
    effective_from timestamp without time zone,
    effective_until timestamp without time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.sla_definitions FORCE ROW LEVEL SECURITY;


ALTER TABLE public.sla_definitions OWNER TO postgres;

--
-- Name: COLUMN sla_definitions.target_value; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.target_value IS 'Target value to meet';


--
-- Name: COLUMN sla_definitions.unit_of_measure; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.unit_of_measure IS 'minutes, hours, %, count';


--
-- Name: COLUMN sla_definitions.warning_threshold; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.warning_threshold IS 'Warning level (e.g., 80% of target)';


--
-- Name: COLUMN sla_definitions.critical_threshold; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.critical_threshold IS 'Critical level';


--
-- Name: COLUMN sla_definitions.applies_to_service_type; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.applies_to_service_type IS 'express, standard, economy';


--
-- Name: COLUMN sla_definitions.applies_to_customer_tier; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.applies_to_customer_tier IS 'premium, standard, basic';


--
-- Name: COLUMN sla_definitions.penalty_per_breach; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.penalty_per_breach IS 'Financial penalty';


--
-- Name: COLUMN sla_definitions.measurement_period; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.measurement_period IS 'daily, weekly, monthly';


--
-- Name: COLUMN sla_definitions.calculation_method; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_definitions.calculation_method IS 'How to calculate compliance';


--
-- Name: sla_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sla_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sla_definitions_id_seq OWNER TO postgres;

--
-- Name: sla_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sla_definitions_id_seq OWNED BY public.sla_definitions.id;


--
-- Name: sla_events; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_events (
    sla_instance_id integer NOT NULL,
    event_type character varying NOT NULL,
    event_time timestamp without time zone NOT NULL,
    triggered_by_id integer,
    details json,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.sla_events FORCE ROW LEVEL SECURITY;


ALTER TABLE public.sla_events OWNER TO postgres;

--
-- Name: sla_events_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sla_events_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sla_events_id_seq OWNER TO postgres;

--
-- Name: sla_events_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sla_events_id_seq OWNED BY public.sla_events.id;


--
-- Name: sla_thresholds; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_thresholds (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    organization_id integer NOT NULL,
    threshold_code character varying(50) NOT NULL,
    threshold_name character varying(200) NOT NULL,
    description text,
    sla_type character varying(50) NOT NULL,
    service_type character varying(50),
    target_minutes integer NOT NULL,
    warning_minutes integer NOT NULL,
    critical_minutes integer NOT NULL,
    zone_id integer,
    applies_to_all_zones boolean,
    penalty_amount numeric(10,2),
    escalation_required boolean,
    is_active boolean
);


ALTER TABLE public.sla_thresholds OWNER TO postgres;

--
-- Name: sla_thresholds_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sla_thresholds_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sla_thresholds_id_seq OWNER TO postgres;

--
-- Name: sla_thresholds_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sla_thresholds_id_seq OWNED BY public.sla_thresholds.id;


--
-- Name: sla_tracking; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sla_tracking (
    sla_definition_id integer NOT NULL,
    tracking_number character varying(50) NOT NULL,
    delivery_id integer,
    route_id integer,
    courier_id integer,
    incident_id integer,
    start_time timestamp without time zone NOT NULL,
    target_completion_time timestamp without time zone NOT NULL,
    warning_time timestamp without time zone,
    actual_completion_time timestamp without time zone,
    status public.slastatus,
    target_value numeric(10,2) NOT NULL,
    actual_value numeric(10,2),
    variance numeric(10,2),
    variance_percentage numeric(5,2),
    is_breached boolean,
    breach_time timestamp without time zone,
    breach_duration_minutes integer,
    breach_severity character varying(20),
    customer_notified boolean,
    notification_sent_at timestamp without time zone,
    penalty_applied numeric(10,2),
    breach_reason text,
    corrective_action text,
    resolution_notes text,
    escalated boolean,
    escalated_to_id integer,
    escalated_at timestamp without time zone,
    compliance_score numeric(5,2),
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.sla_tracking FORCE ROW LEVEL SECURITY;


ALTER TABLE public.sla_tracking OWNER TO postgres;

--
-- Name: COLUMN sla_tracking.warning_time; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.warning_time IS 'When warning threshold is reached';


--
-- Name: COLUMN sla_tracking.variance; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.variance IS 'Difference from target';


--
-- Name: COLUMN sla_tracking.variance_percentage; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.variance_percentage IS 'Percentage variance';


--
-- Name: COLUMN sla_tracking.breach_duration_minutes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.breach_duration_minutes IS 'How long breached';


--
-- Name: COLUMN sla_tracking.breach_severity; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.breach_severity IS 'minor, major, critical';


--
-- Name: COLUMN sla_tracking.breach_reason; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.breach_reason IS 'Reason for SLA breach';


--
-- Name: COLUMN sla_tracking.compliance_score; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.sla_tracking.compliance_score IS 'Compliance percentage 0-100';


--
-- Name: sla_tracking_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sla_tracking_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sla_tracking_id_seq OWNER TO postgres;

--
-- Name: sla_tracking_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sla_tracking_id_seq OWNED BY public.sla_tracking.id;


--
-- Name: sub_projects; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.sub_projects (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    project_code character varying(100) NOT NULL,
    project_name character varying(255) NOT NULL,
    project_name_ar character varying(255),
    description text,
    project_type character varying(50),
    status character varying(50) DEFAULT 'active'::character varying NOT NULL,
    start_date date,
    end_date date,
    budget numeric(12,2),
    spent_amount numeric(12,2) DEFAULT 0,
    city character varying(100),
    location character varying(255),
    manager_id integer,
    client_name character varying(255),
    client_contact character varying(100),
    contract_url text,
    total_couriers integer DEFAULT 0,
    total_vehicles integer DEFAULT 0,
    performance_metrics jsonb,
    settings jsonb,
    tags text[],
    notes text,
    created_by integer,
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp(6) without time zone
);


ALTER TABLE public.sub_projects OWNER TO ramiz_new;

--
-- Name: sub_projects_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.sub_projects_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sub_projects_id_seq OWNER TO ramiz_new;

--
-- Name: sub_projects_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.sub_projects_id_seq OWNED BY public.sub_projects.id;


--
-- Name: system_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.system_settings (
    key character varying(100) NOT NULL,
    name character varying(200) NOT NULL,
    description text,
    category character varying(50) NOT NULL,
    setting_type character varying(20) NOT NULL,
    value text,
    default_value text,
    json_value json,
    is_sensitive boolean NOT NULL,
    is_editable boolean NOT NULL,
    is_public boolean NOT NULL,
    validation_regex character varying(500),
    allowed_values json,
    min_value character varying(100),
    max_value character varying(100),
    help_text text,
    example_value text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.system_settings FORCE ROW LEVEL SECURITY;


ALTER TABLE public.system_settings OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.system_settings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.system_settings_id_seq OWNER TO postgres;

--
-- Name: system_settings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.system_settings_id_seq OWNED BY public.system_settings.id;


--
-- Name: tasks; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.tasks (
    id integer NOT NULL,
    organization_id integer NOT NULL,
    task_number character varying(100) NOT NULL,
    title character varying(255) NOT NULL,
    description text,
    task_type character varying(50) NOT NULL,
    priority character varying(20) DEFAULT 'medium'::character varying NOT NULL,
    status character varying(50) DEFAULT 'pending'::character varying NOT NULL,
    assigned_to integer,
    assigned_by integer,
    courier_id integer,
    vehicle_id integer,
    related_entity_type character varying(50),
    related_entity_id integer,
    due_date timestamp(6) without time zone,
    scheduled_date timestamp(6) without time zone,
    started_at timestamp(6) without time zone,
    completed_at timestamp(6) without time zone,
    completion_notes text,
    location character varying(255),
    latitude numeric(10,8),
    longitude numeric(11,8),
    estimated_duration integer,
    actual_duration integer,
    attachments_urls text[],
    tags text[],
    is_recurring boolean DEFAULT false,
    recurrence_pattern character varying(100),
    parent_task_id integer,
    created_by integer,
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    deleted_at timestamp(6) without time zone
);


ALTER TABLE public.tasks OWNER TO ramiz_new;

--
-- Name: tasks_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.tasks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tasks_id_seq OWNER TO ramiz_new;

--
-- Name: tasks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.tasks_id_seq OWNED BY public.tasks.id;


--
-- Name: ticket_attachments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_attachments (
    id integer NOT NULL,
    ticket_id integer NOT NULL,
    reply_id integer,
    uploaded_by integer NOT NULL,
    filename character varying(255) NOT NULL,
    file_path character varying(500) NOT NULL,
    file_type character varying(100) NOT NULL,
    file_size bigint NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.ticket_attachments FORCE ROW LEVEL SECURITY;


ALTER TABLE public.ticket_attachments OWNER TO postgres;

--
-- Name: ticket_attachments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ticket_attachments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_attachments_id_seq OWNER TO postgres;

--
-- Name: ticket_attachments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ticket_attachments_id_seq OWNED BY public.ticket_attachments.id;


--
-- Name: ticket_replies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_replies (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    ticket_id integer NOT NULL,
    user_id integer NOT NULL,
    message text NOT NULL,
    is_internal boolean,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.ticket_replies FORCE ROW LEVEL SECURITY;


ALTER TABLE public.ticket_replies OWNER TO postgres;

--
-- Name: TABLE ticket_replies; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public.ticket_replies IS 'Ticket replies for threaded conversations';


--
-- Name: COLUMN ticket_replies.message; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.ticket_replies.message IS 'Reply message content';


--
-- Name: COLUMN ticket_replies.is_internal; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.ticket_replies.is_internal IS 'Whether this is an internal note';


--
-- Name: ticket_replies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ticket_replies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_replies_id_seq OWNER TO postgres;

--
-- Name: ticket_replies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ticket_replies_id_seq OWNED BY public.ticket_replies.id;


--
-- Name: ticket_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.ticket_templates (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    default_subject character varying(255),
    default_description text,
    default_category public.ticketcategory,
    default_priority public.ticketpriority,
    default_department character varying(100),
    default_tags text,
    default_custom_fields json,
    sla_hours integer,
    is_active boolean DEFAULT true NOT NULL,
    is_public boolean DEFAULT true NOT NULL,
    created_by integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.ticket_templates FORCE ROW LEVEL SECURITY;


ALTER TABLE public.ticket_templates OWNER TO postgres;

--
-- Name: ticket_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.ticket_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.ticket_templates_id_seq OWNER TO postgres;

--
-- Name: ticket_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.ticket_templates_id_seq OWNED BY public.ticket_templates.id;


--
-- Name: tickets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tickets (
    id integer NOT NULL,
    ticket_id character varying(50) NOT NULL,
    courier_id integer,
    created_by integer NOT NULL,
    assigned_to integer,
    category public.ticketcategory NOT NULL,
    priority public.ticketpriority DEFAULT 'medium'::public.ticketpriority NOT NULL,
    status public.ticketstatus DEFAULT 'open'::public.ticketstatus NOT NULL,
    subject character varying(255) NOT NULL,
    description text NOT NULL,
    resolution text,
    resolved_at timestamp with time zone,
    closed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    sla_due_at timestamp with time zone,
    first_response_at timestamp with time zone,
    sla_breached boolean DEFAULT false NOT NULL,
    escalation_level public.escalationlevel DEFAULT 'none'::public.escalationlevel NOT NULL,
    escalated_at timestamp with time zone,
    escalated_by integer,
    escalation_reason text,
    merged_into_id integer,
    is_merged boolean DEFAULT false NOT NULL,
    template_id integer,
    tags text,
    custom_fields json,
    contact_email character varying(255),
    contact_phone character varying(50),
    department character varying(100),
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.tickets FORCE ROW LEVEL SECURITY;


ALTER TABLE public.tickets OWNER TO postgres;

--
-- Name: COLUMN tickets.ticket_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.ticket_id IS 'Unique ticket identifier (e.g., TKT-20250106-001)';


--
-- Name: COLUMN tickets.courier_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.courier_id IS 'Related courier (nullable for non-courier issues)';


--
-- Name: COLUMN tickets.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.created_by IS 'User who created the ticket';


--
-- Name: COLUMN tickets.assigned_to; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.assigned_to IS 'User assigned to handle the ticket';


--
-- Name: COLUMN tickets.category; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.category IS 'Ticket category for routing';


--
-- Name: COLUMN tickets.priority; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.priority IS 'Ticket priority level';


--
-- Name: COLUMN tickets.status; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.status IS 'Current ticket status';


--
-- Name: COLUMN tickets.subject; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.subject IS 'Ticket subject/title';


--
-- Name: COLUMN tickets.description; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.description IS 'Detailed description of the issue';


--
-- Name: COLUMN tickets.resolution; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.resolution IS 'Resolution details when ticket is resolved';


--
-- Name: COLUMN tickets.resolved_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.resolved_at IS 'When ticket was resolved';


--
-- Name: COLUMN tickets.closed_at; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.tickets.closed_at IS 'When ticket was closed';


--
-- Name: tickets_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tickets_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tickets_id_seq OWNER TO postgres;

--
-- Name: tickets_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tickets_id_seq OWNED BY public.tickets.id;


--
-- Name: trigger_executions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trigger_executions (
    trigger_id integer NOT NULL,
    workflow_instance_id integer,
    triggered_at timestamp without time zone NOT NULL,
    trigger_data json,
    status character varying NOT NULL,
    workflow_created boolean,
    error_message text,
    execution_time_ms integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.trigger_executions FORCE ROW LEVEL SECURITY;


ALTER TABLE public.trigger_executions OWNER TO postgres;

--
-- Name: trigger_executions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trigger_executions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trigger_executions_id_seq OWNER TO postgres;

--
-- Name: trigger_executions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trigger_executions_id_seq OWNED BY public.trigger_executions.id;


--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    hashed_password character varying,
    full_name character varying,
    is_active boolean,
    is_superuser boolean,
    role character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    google_id character varying,
    picture character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: vehicle_data; Type: TABLE; Schema: public; Owner: ramiz_new
--

CREATE TABLE public.vehicle_data (
    id bigint NOT NULL,
    organization_id integer NOT NULL,
    vehicle_id integer NOT NULL,
    courier_id integer,
    data_type character varying(50) NOT NULL,
    "timestamp" timestamp(6) without time zone NOT NULL,
    latitude numeric(10,8),
    longitude numeric(11,8),
    speed numeric(6,2),
    heading numeric(6,2),
    altitude numeric(8,2),
    odometer integer,
    fuel_level numeric(5,2),
    engine_status character varying(20),
    battery_voltage numeric(5,2),
    coolant_temp numeric(5,2),
    rpm integer,
    ignition_status boolean,
    door_status character varying(50),
    ac_status boolean,
    harsh_acceleration boolean DEFAULT false,
    harsh_braking boolean DEFAULT false,
    harsh_cornering boolean DEFAULT false,
    over_speeding boolean DEFAULT false,
    idle_time integer,
    driving_time integer,
    gps_signal_quality integer,
    gsm_signal_quality integer,
    event_type character varying(50),
    event_data jsonb,
    raw_data jsonb,
    device_id character varying(100),
    imei character varying(50),
    created_at timestamp(6) without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


ALTER TABLE public.vehicle_data OWNER TO ramiz_new;

--
-- Name: vehicle_data_id_seq; Type: SEQUENCE; Schema: public; Owner: ramiz_new
--

CREATE SEQUENCE public.vehicle_data_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_data_id_seq OWNER TO ramiz_new;

--
-- Name: vehicle_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ramiz_new
--

ALTER SEQUENCE public.vehicle_data_id_seq OWNED BY public.vehicle_data.id;


--
-- Name: vehicle_inspections; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle_inspections (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    inspector_id integer,
    inspection_type character varying(20) NOT NULL,
    inspection_date date NOT NULL,
    inspection_time timestamp without time zone,
    status character varying(20) NOT NULL,
    overall_condition character varying(20),
    mileage_at_inspection numeric(10,2),
    engine_condition boolean,
    engine_oil_level boolean,
    coolant_level boolean,
    battery_condition boolean,
    transmission boolean,
    headlights boolean,
    taillights boolean,
    indicators boolean,
    brake_lights boolean,
    horn boolean,
    dashboard_lights boolean,
    brake_pads_front boolean,
    brake_pads_rear boolean,
    brake_fluid_level boolean,
    handbrake boolean,
    tire_front_left boolean,
    tire_front_right boolean,
    tire_rear_left boolean,
    tire_rear_right boolean,
    spare_tire boolean,
    tire_pressure_ok boolean,
    body_condition boolean,
    windshield boolean,
    mirrors boolean,
    wipers boolean,
    doors boolean,
    windows boolean,
    seats boolean,
    seatbelts boolean,
    air_conditioning boolean,
    steering boolean,
    first_aid_kit boolean,
    fire_extinguisher boolean,
    warning_triangle boolean,
    jack_and_tools boolean,
    registration_document boolean,
    insurance_document boolean,
    issues_found text,
    critical_issues text,
    recommendations text,
    required_repairs text,
    requires_immediate_repair boolean,
    requires_follow_up boolean,
    follow_up_date date,
    repairs_completed boolean,
    repairs_completion_date date,
    inspector_name character varying(200),
    inspector_signature character varying(500),
    inspector_comments text,
    weather_during_inspection character varying(100),
    location character varying(300),
    notes text,
    inspection_report_url character varying(500),
    photos_json text,
    inspection_score integer,
    total_checks integer,
    passed_checks integer,
    failed_checks integer,
    meets_safety_standards boolean,
    roadworthy boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);


ALTER TABLE public.vehicle_inspections OWNER TO postgres;

--
-- Name: vehicle_inspections_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_inspections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_inspections_id_seq OWNER TO postgres;

--
-- Name: vehicle_inspections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_inspections_id_seq OWNED BY public.vehicle_inspections.id;


--
-- Name: vehicle_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle_logs (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    courier_id integer,
    log_type character varying(20) NOT NULL,
    log_date date NOT NULL,
    log_time time without time zone,
    start_mileage numeric(10,2),
    end_mileage numeric(10,2),
    distance_covered numeric(10,2),
    start_location character varying(300),
    end_location character varying(300),
    route_description text,
    fuel_refilled numeric(8,2),
    fuel_cost numeric(10,2),
    fuel_provider character varying(20),
    fuel_station_location character varying(300),
    fuel_receipt_number character varying(100),
    number_of_deliveries integer,
    number_of_orders integer,
    revenue_generated numeric(10,2),
    vehicle_condition character varying(50),
    issues_reported text,
    has_issues boolean,
    start_time timestamp without time zone,
    end_time timestamp without time zone,
    working_hours numeric(5,2),
    weather_conditions character varying(100),
    traffic_conditions character varying(100),
    notes text,
    recorded_by character varying(200),
    receipt_image_url character varying(500),
    log_photo_urls text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.vehicle_logs FORCE ROW LEVEL SECURITY;


ALTER TABLE public.vehicle_logs OWNER TO postgres;

--
-- Name: vehicle_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_logs_id_seq OWNER TO postgres;

--
-- Name: vehicle_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_logs_id_seq OWNED BY public.vehicle_logs.id;


--
-- Name: vehicle_maintenance; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicle_maintenance (
    id integer NOT NULL,
    vehicle_id integer NOT NULL,
    maintenance_type character varying(20) NOT NULL,
    status character varying(20) NOT NULL,
    service_provider character varying(20),
    scheduled_date date,
    start_date date,
    completion_date date,
    mileage_at_service numeric(10,2),
    service_description text NOT NULL,
    work_performed text,
    parts_replaced text,
    parts_list_json text,
    service_center_name character varying(300),
    service_center_location character varying(300),
    technician_name character varying(200),
    technician_phone character varying(20),
    labor_cost numeric(10,2),
    parts_cost numeric(10,2),
    total_cost numeric(10,2) NOT NULL,
    tax_amount numeric(10,2),
    discount_amount numeric(10,2),
    payment_method character varying(50),
    invoice_number character varying(100),
    invoice_date date,
    payment_status character varying(50),
    has_warranty boolean,
    warranty_expiry_date date,
    warranty_details text,
    next_service_date date,
    next_service_mileage numeric(10,2),
    quality_rating integer,
    approved_by character varying(200),
    approval_date date,
    issues_found text,
    recommendations text,
    notes text,
    invoice_image_url character varying(500),
    report_file_url character varying(500),
    photos_json text,
    vehicle_downtime_hours numeric(6,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.vehicle_maintenance FORCE ROW LEVEL SECURITY;


ALTER TABLE public.vehicle_maintenance OWNER TO postgres;

--
-- Name: vehicle_maintenance_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicle_maintenance_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicle_maintenance_id_seq OWNER TO postgres;

--
-- Name: vehicle_maintenance_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicle_maintenance_id_seq OWNED BY public.vehicle_maintenance.id;


--
-- Name: vehicles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.vehicles (
    id integer NOT NULL,
    plate_number character varying(20) NOT NULL,
    vehicle_type character varying(20) NOT NULL,
    make character varying(100) NOT NULL,
    model character varying(100) NOT NULL,
    year integer NOT NULL,
    color character varying(50),
    status character varying(20) NOT NULL,
    ownership_type character varying(20),
    registration_number character varying(50),
    registration_expiry_date date,
    insurance_company character varying(200),
    insurance_policy_number character varying(100),
    insurance_expiry_date date,
    vin_number character varying(50),
    engine_number character varying(50),
    engine_capacity character varying(20),
    transmission character varying(20),
    fuel_type character varying(20),
    current_mileage numeric(10,2),
    fuel_capacity numeric(5,2),
    purchase_price numeric(10,2),
    purchase_date date,
    monthly_lease_cost numeric(10,2),
    depreciation_rate numeric(5,2),
    last_service_date date,
    last_service_mileage numeric(10,2),
    next_service_due_date date,
    next_service_due_mileage numeric(10,2),
    gps_device_id character varying(100),
    gps_device_imei character varying(50),
    is_gps_active boolean,
    assigned_to_city character varying(100),
    assigned_to_project character varying(100),
    notes text,
    is_pool_vehicle boolean,
    total_trips integer,
    total_distance numeric(10,2),
    avg_fuel_consumption numeric(5,2),
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    fms_asset_id integer,
    fms_tracking_unit_id integer,
    fms_last_sync character varying(50),
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.vehicles FORCE ROW LEVEL SECURITY;


ALTER TABLE public.vehicles OWNER TO postgres;

--
-- Name: vehicles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.vehicles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.vehicles_id_seq OWNER TO postgres;

--
-- Name: vehicles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.vehicles_id_seq OWNED BY public.vehicles.id;


--
-- Name: workflow_automations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_automations (
    name character varying NOT NULL,
    description text,
    workflow_template_id integer,
    trigger_type public.automationtriggertype NOT NULL,
    trigger_config json,
    conditions json,
    condition_logic character varying,
    action_type public.automationactiontype NOT NULL,
    action_config json,
    is_active boolean,
    run_order integer,
    max_retries integer,
    retry_delay integer,
    timeout integer,
    schedule_cron character varying,
    schedule_timezone character varying,
    last_run_at timestamp without time zone,
    next_run_at timestamp without time zone,
    status public.automationstatus,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_automations FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_automations OWNER TO postgres;

--
-- Name: workflow_automations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_automations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_automations_id_seq OWNER TO postgres;

--
-- Name: workflow_automations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_automations_id_seq OWNED BY public.workflow_automations.id;


--
-- Name: workflow_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_instances (
    id integer NOT NULL,
    template_id integer NOT NULL,
    initiated_by integer NOT NULL,
    status public.workflowstatus DEFAULT 'DRAFT'::public.workflowstatus NOT NULL,
    current_step integer DEFAULT 0 NOT NULL,
    data json,
    started_at date,
    completed_at date,
    notes text,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_instances FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_instances OWNER TO postgres;

--
-- Name: workflow_instances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_instances_id_seq OWNER TO postgres;

--
-- Name: workflow_instances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_instances_id_seq OWNED BY public.workflow_instances.id;


--
-- Name: workflow_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_metrics (
    workflow_template_id integer NOT NULL,
    date date NOT NULL,
    total_instances integer,
    completed_instances integer,
    rejected_instances integer,
    cancelled_instances integer,
    in_progress_instances integer,
    avg_completion_time double precision,
    min_completion_time double precision,
    max_completion_time double precision,
    median_completion_time double precision,
    avg_steps_completed double precision,
    total_steps_executed integer,
    avg_approval_time double precision,
    total_approvals integer,
    total_rejections integer,
    sla_met_count integer,
    sla_breached_count integer,
    avg_sla_compliance double precision,
    bottleneck_steps json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_metrics FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_metrics OWNER TO postgres;

--
-- Name: workflow_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_metrics_id_seq OWNER TO postgres;

--
-- Name: workflow_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_metrics_id_seq OWNED BY public.workflow_metrics.id;


--
-- Name: workflow_performance_snapshots; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_performance_snapshots (
    workflow_template_id integer,
    snapshot_time timestamp without time zone NOT NULL,
    active_instances integer,
    pending_approvals integer,
    overdue_instances integer,
    sla_at_risk integer,
    completed_last_24h integer,
    avg_completion_time_24h double precision,
    success_rate_24h double precision,
    throughput_per_hour double precision,
    estimated_completion_time double precision,
    critical_alerts integer,
    warning_alerts integer,
    details json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_performance_snapshots FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_performance_snapshots OWNER TO postgres;

--
-- Name: workflow_performance_snapshots_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_performance_snapshots_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_performance_snapshots_id_seq OWNER TO postgres;

--
-- Name: workflow_performance_snapshots_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_performance_snapshots_id_seq OWNED BY public.workflow_performance_snapshots.id;


--
-- Name: workflow_sla_instances; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_sla_instances (
    workflow_instance_id integer NOT NULL,
    sla_id integer NOT NULL,
    status public.slastatus,
    started_at timestamp without time zone NOT NULL,
    response_due_at timestamp without time zone,
    resolution_due_at timestamp without time zone NOT NULL,
    warning_at timestamp without time zone,
    first_response_at timestamp without time zone,
    resolved_at timestamp without time zone,
    breached_at timestamp without time zone,
    paused_at timestamp without time zone,
    pause_duration integer,
    response_time_minutes integer,
    resolution_time_minutes integer,
    breach_time_minutes integer,
    warning_sent boolean,
    escalation_sent boolean,
    escalation_level integer,
    notes text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_sla_instances FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_sla_instances OWNER TO postgres;

--
-- Name: workflow_sla_instances_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_sla_instances_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_sla_instances_id_seq OWNER TO postgres;

--
-- Name: workflow_sla_instances_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_sla_instances_id_seq OWNED BY public.workflow_sla_instances.id;


--
-- Name: workflow_slas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_slas (
    name character varying NOT NULL,
    description text,
    workflow_template_id integer,
    priority public.slapriority,
    response_time integer,
    resolution_time integer NOT NULL,
    warning_threshold integer,
    use_business_hours boolean,
    business_hours_start character varying,
    business_hours_end character varying,
    business_days json,
    escalate_on_warning boolean,
    escalate_on_breach boolean,
    escalation_chain json,
    is_active boolean,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_slas FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_slas OWNER TO postgres;

--
-- Name: workflow_slas_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_slas_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_slas_id_seq OWNER TO postgres;

--
-- Name: workflow_slas_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_slas_id_seq OWNED BY public.workflow_slas.id;


--
-- Name: workflow_step_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_step_metrics (
    workflow_template_id integer NOT NULL,
    step_index integer NOT NULL,
    step_name character varying NOT NULL,
    date date NOT NULL,
    total_executions integer,
    successful_executions integer,
    failed_executions integer,
    skipped_executions integer,
    avg_execution_time double precision,
    min_execution_time double precision,
    max_execution_time double precision,
    avg_wait_time double precision,
    max_wait_time double precision,
    error_rate double precision,
    common_errors json,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_step_metrics FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_step_metrics OWNER TO postgres;

--
-- Name: workflow_step_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_step_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_step_metrics_id_seq OWNER TO postgres;

--
-- Name: workflow_step_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_step_metrics_id_seq OWNED BY public.workflow_step_metrics.id;


--
-- Name: workflow_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_templates (
    id integer NOT NULL,
    name character varying NOT NULL,
    description text,
    steps json NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    category character varying,
    estimated_duration integer,
    created_at timestamp without time zone DEFAULT now() NOT NULL,
    updated_at timestamp without time zone,
    version integer DEFAULT 1,
    parent_template_id integer,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_templates FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_templates OWNER TO postgres;

--
-- Name: workflow_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_templates_id_seq OWNER TO postgres;

--
-- Name: workflow_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_templates_id_seq OWNED BY public.workflow_templates.id;


--
-- Name: workflow_triggers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_triggers (
    name character varying NOT NULL,
    description text,
    workflow_template_id integer NOT NULL,
    trigger_type public.triggertype NOT NULL,
    event_type public.triggereventtype,
    entity_type character varying,
    field_conditions json,
    schedule_cron character varying,
    schedule_timezone character varying,
    conditions json,
    condition_logic character varying,
    is_active boolean,
    priority integer,
    deduplicate boolean,
    deduplicate_key character varying,
    deduplicate_window integer,
    rate_limit integer,
    rate_limit_window integer,
    webhook_url character varying,
    webhook_secret character varying,
    last_triggered_at timestamp without time zone,
    next_trigger_at timestamp without time zone,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_triggers FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_triggers OWNER TO postgres;

--
-- Name: workflow_triggers_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_triggers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_triggers_id_seq OWNER TO postgres;

--
-- Name: workflow_triggers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_triggers_id_seq OWNED BY public.workflow_triggers.id;


--
-- Name: workflow_user_metrics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.workflow_user_metrics (
    user_id integer NOT NULL,
    workflow_template_id integer,
    date date NOT NULL,
    workflows_initiated integer,
    approvals_completed integer,
    approvals_pending integer,
    avg_approval_time double precision,
    approval_rate double precision,
    tasks_completed integer,
    avg_task_completion_time double precision,
    on_time_completion_rate double precision,
    overdue_tasks integer,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.workflow_user_metrics FORCE ROW LEVEL SECURITY;


ALTER TABLE public.workflow_user_metrics OWNER TO postgres;

--
-- Name: workflow_user_metrics_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.workflow_user_metrics_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.workflow_user_metrics_id_seq OWNER TO postgres;

--
-- Name: workflow_user_metrics_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.workflow_user_metrics_id_seq OWNED BY public.workflow_user_metrics.id;


--
-- Name: zone_defaults; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zone_defaults (
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    organization_id integer NOT NULL,
    default_code character varying(50) NOT NULL,
    default_name character varying(200) NOT NULL,
    description text,
    default_max_couriers integer,
    default_priority_level integer,
    default_service_fee numeric(10,2),
    default_peak_multiplier numeric(5,2),
    default_minimum_order numeric(10,2),
    default_delivery_time_minutes integer,
    default_sla_target_minutes integer,
    operating_start character varying(8),
    operating_end character varying(8),
    is_active boolean,
    is_default boolean
);


ALTER TABLE public.zone_defaults OWNER TO postgres;

--
-- Name: zone_defaults_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zone_defaults_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zone_defaults_id_seq OWNER TO postgres;

--
-- Name: zone_defaults_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zone_defaults_id_seq OWNED BY public.zone_defaults.id;


--
-- Name: zones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.zones (
    zone_code character varying(50) NOT NULL,
    zone_name character varying(200) NOT NULL,
    description text,
    city character varying(100) NOT NULL,
    district character varying(100),
    postal_code character varying(20),
    boundaries json,
    center_latitude double precision,
    center_longitude double precision,
    coverage_area_km2 double precision,
    estimated_population integer,
    business_density character varying(20),
    status public.zonestatus NOT NULL,
    priority_level integer,
    max_couriers integer,
    current_couriers integer,
    avg_delivery_time_minutes double precision,
    total_deliveries_completed integer,
    success_rate double precision,
    service_fee double precision,
    peak_hour_multiplier double precision,
    minimum_order_value double precision,
    notes text,
    special_instructions text,
    id integer NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    organization_id integer NOT NULL
);

ALTER TABLE ONLY public.zones FORCE ROW LEVEL SECURITY;


ALTER TABLE public.zones OWNER TO postgres;

--
-- Name: COLUMN zones.zone_code; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.zone_code IS 'Unique zone identifier';


--
-- Name: COLUMN zones.boundaries; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.boundaries IS 'GeoJSON polygon defining zone boundaries';


--
-- Name: COLUMN zones.coverage_area_km2; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.coverage_area_km2 IS 'Area in square kilometers';


--
-- Name: COLUMN zones.business_density; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.business_density IS 'low, medium, high';


--
-- Name: COLUMN zones.priority_level; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.priority_level IS '1=lowest, 5=highest';


--
-- Name: COLUMN zones.max_couriers; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.max_couriers IS 'Maximum couriers allowed in zone';


--
-- Name: COLUMN zones.current_couriers; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.current_couriers IS 'Current active couriers';


--
-- Name: COLUMN zones.success_rate; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.success_rate IS 'Percentage 0-100';


--
-- Name: COLUMN zones.service_fee; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.zones.service_fee IS 'Base service fee for zone';


--
-- Name: zones_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.zones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.zones_id_seq OWNER TO postgres;

--
-- Name: zones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.zones_id_seq OWNED BY public.zones.id;


--
-- Name: cdc_queue id; Type: DEFAULT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.cdc_queue ALTER COLUMN id SET DEFAULT nextval('barq.cdc_queue_id_seq'::regclass);


--
-- Name: accident_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accident_logs ALTER COLUMN id SET DEFAULT nextval('public.accident_logs_id_seq'::regclass);


--
-- Name: allocations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allocations ALTER COLUMN id SET DEFAULT nextval('public.allocations_id_seq'::regclass);


--
-- Name: api_keys id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_keys ALTER COLUMN id SET DEFAULT nextval('public.api_keys_id_seq'::regclass);


--
-- Name: approval_chain_approvers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers ALTER COLUMN id SET DEFAULT nextval('public.approval_chain_approvers_id_seq'::regclass);


--
-- Name: approval_chains id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chains ALTER COLUMN id SET DEFAULT nextval('public.approval_chains_id_seq'::regclass);


--
-- Name: approval_requests id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests ALTER COLUMN id SET DEFAULT nextval('public.approval_requests_id_seq'::regclass);


--
-- Name: assets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets ALTER COLUMN id SET DEFAULT nextval('public.assets_id_seq'::regclass);


--
-- Name: assignments id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments ALTER COLUMN id SET DEFAULT nextval('public.assignments_id_seq'::regclass);


--
-- Name: attendance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance ALTER COLUMN id SET DEFAULT nextval('public.attendance_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- Name: automation_execution_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_execution_logs ALTER COLUMN id SET DEFAULT nextval('public.automation_execution_logs_id_seq'::regclass);


--
-- Name: backups id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups ALTER COLUMN id SET DEFAULT nextval('public.backups_id_seq'::regclass);


--
-- Name: beds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds ALTER COLUMN id SET DEFAULT nextval('public.beds_id_seq'::regclass);


--
-- Name: bonuses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bonuses ALTER COLUMN id SET DEFAULT nextval('public.bonuses_id_seq'::regclass);


--
-- Name: buildings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.buildings ALTER COLUMN id SET DEFAULT nextval('public.buildings_id_seq'::regclass);


--
-- Name: canned_responses id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canned_responses ALTER COLUMN id SET DEFAULT nextval('public.canned_responses_id_seq'::regclass);


--
-- Name: chat_messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages ALTER COLUMN id SET DEFAULT nextval('public.chat_messages_id_seq'::regclass);


--
-- Name: chat_sessions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions ALTER COLUMN id SET DEFAULT nextval('public.chat_sessions_id_seq'::regclass);


--
-- Name: cod_transactions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cod_transactions ALTER COLUMN id SET DEFAULT nextval('public.cod_transactions_id_seq'::regclass);


--
-- Name: courier_vehicle_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courier_vehicle_assignments ALTER COLUMN id SET DEFAULT nextval('public.courier_vehicle_assignments_id_seq'::regclass);


--
-- Name: couriers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers ALTER COLUMN id SET DEFAULT nextval('public.couriers_id_seq'::regclass);


--
-- Name: customer_feedbacks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks ALTER COLUMN id SET DEFAULT nextval('public.customer_feedbacks_id_seq'::regclass);


--
-- Name: dashboards id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboards ALTER COLUMN id SET DEFAULT nextval('public.dashboards_id_seq'::regclass);


--
-- Name: deliveries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries ALTER COLUMN id SET DEFAULT nextval('public.deliveries_id_seq'::regclass);


--
-- Name: dispatch_assignments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments ALTER COLUMN id SET DEFAULT nextval('public.dispatch_assignments_id_seq'::regclass);


--
-- Name: dispatch_rules id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_rules ALTER COLUMN id SET DEFAULT nextval('public.dispatch_rules_id_seq'::regclass);


--
-- Name: documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents ALTER COLUMN id SET DEFAULT nextval('public.documents_id_seq'::regclass);


--
-- Name: driver_orders id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.driver_orders ALTER COLUMN id SET DEFAULT nextval('public.driver_orders_id_seq'::regclass);


--
-- Name: faqs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faqs ALTER COLUMN id SET DEFAULT nextval('public.faqs_id_seq'::regclass);


--
-- Name: feedback_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_templates ALTER COLUMN id SET DEFAULT nextval('public.feedback_templates_id_seq'::regclass);


--
-- Name: feedbacks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedbacks ALTER COLUMN id SET DEFAULT nextval('public.feedbacks_id_seq'::regclass);


--
-- Name: fuel_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_logs ALTER COLUMN id SET DEFAULT nextval('public.fuel_logs_id_seq'::regclass);


--
-- Name: handovers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers ALTER COLUMN id SET DEFAULT nextval('public.handovers_id_seq'::regclass);


--
-- Name: incidents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents ALTER COLUMN id SET DEFAULT nextval('public.incidents_id_seq'::regclass);


--
-- Name: integrations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integrations ALTER COLUMN id SET DEFAULT nextval('public.integrations_id_seq'::regclass);


--
-- Name: kb_articles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_articles ALTER COLUMN id SET DEFAULT nextval('public.kb_articles_id_seq'::regclass);


--
-- Name: kb_categories id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_categories ALTER COLUMN id SET DEFAULT nextval('public.kb_categories_id_seq'::regclass);


--
-- Name: kpis id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpis ALTER COLUMN id SET DEFAULT nextval('public.kpis_id_seq'::regclass);


--
-- Name: leaves id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leaves ALTER COLUMN id SET DEFAULT nextval('public.leaves_id_seq'::regclass);


--
-- Name: loans id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans ALTER COLUMN id SET DEFAULT nextval('public.loans_id_seq'::regclass);


--
-- Name: metric_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_snapshots ALTER COLUMN id SET DEFAULT nextval('public.metric_snapshots_id_seq'::regclass);


--
-- Name: notification_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_settings ALTER COLUMN id SET DEFAULT nextval('public.notification_settings_id_seq'::regclass);


--
-- Name: notifications id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications ALTER COLUMN id SET DEFAULT nextval('public.notifications_id_seq'::regclass);


--
-- Name: operations_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_documents ALTER COLUMN id SET DEFAULT nextval('public.operations_documents_id_seq'::regclass);


--
-- Name: operations_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_settings ALTER COLUMN id SET DEFAULT nextval('public.operations_settings_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: organization_users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_users ALTER COLUMN id SET DEFAULT nextval('public.organization_users_id_seq'::regclass);


--
-- Name: organizations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations ALTER COLUMN id SET DEFAULT nextval('public.organizations_id_seq'::regclass);


--
-- Name: password_reset_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.password_reset_tokens_id_seq'::regclass);


--
-- Name: performance_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_data ALTER COLUMN id SET DEFAULT nextval('public.performance_data_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions ALTER COLUMN id SET DEFAULT nextval('public.permissions_id_seq'::regclass);


--
-- Name: priority_queue_entries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries ALTER COLUMN id SET DEFAULT nextval('public.priority_queue_entries_id_seq'::regclass);


--
-- Name: quality_inspections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections ALTER COLUMN id SET DEFAULT nextval('public.quality_inspections_id_seq'::regclass);


--
-- Name: quality_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_metrics ALTER COLUMN id SET DEFAULT nextval('public.quality_metrics_id_seq'::regclass);


--
-- Name: reports id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports ALTER COLUMN id SET DEFAULT nextval('public.reports_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: rooms id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms ALTER COLUMN id SET DEFAULT nextval('public.rooms_id_seq'::regclass);


--
-- Name: routes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes ALTER COLUMN id SET DEFAULT nextval('public.routes_id_seq'::regclass);


--
-- Name: salaries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries ALTER COLUMN id SET DEFAULT nextval('public.salaries_id_seq'::regclass);


--
-- Name: sla_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_definitions ALTER COLUMN id SET DEFAULT nextval('public.sla_definitions_id_seq'::regclass);


--
-- Name: sla_events id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_events ALTER COLUMN id SET DEFAULT nextval('public.sla_events_id_seq'::regclass);


--
-- Name: sla_thresholds id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_thresholds ALTER COLUMN id SET DEFAULT nextval('public.sla_thresholds_id_seq'::regclass);


--
-- Name: sla_tracking id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking ALTER COLUMN id SET DEFAULT nextval('public.sla_tracking_id_seq'::regclass);


--
-- Name: sub_projects id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects ALTER COLUMN id SET DEFAULT nextval('public.sub_projects_id_seq'::regclass);


--
-- Name: system_settings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings ALTER COLUMN id SET DEFAULT nextval('public.system_settings_id_seq'::regclass);


--
-- Name: tasks id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks ALTER COLUMN id SET DEFAULT nextval('public.tasks_id_seq'::regclass);


--
-- Name: ticket_attachments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments ALTER COLUMN id SET DEFAULT nextval('public.ticket_attachments_id_seq'::regclass);


--
-- Name: ticket_replies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_replies ALTER COLUMN id SET DEFAULT nextval('public.ticket_replies_id_seq'::regclass);


--
-- Name: ticket_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_templates ALTER COLUMN id SET DEFAULT nextval('public.ticket_templates_id_seq'::regclass);


--
-- Name: tickets id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets ALTER COLUMN id SET DEFAULT nextval('public.tickets_id_seq'::regclass);


--
-- Name: trigger_executions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trigger_executions ALTER COLUMN id SET DEFAULT nextval('public.trigger_executions_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: vehicle_data id; Type: DEFAULT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.vehicle_data ALTER COLUMN id SET DEFAULT nextval('public.vehicle_data_id_seq'::regclass);


--
-- Name: vehicle_inspections id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_inspections ALTER COLUMN id SET DEFAULT nextval('public.vehicle_inspections_id_seq'::regclass);


--
-- Name: vehicle_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_logs ALTER COLUMN id SET DEFAULT nextval('public.vehicle_logs_id_seq'::regclass);


--
-- Name: vehicle_maintenance id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_maintenance ALTER COLUMN id SET DEFAULT nextval('public.vehicle_maintenance_id_seq'::regclass);


--
-- Name: vehicles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles ALTER COLUMN id SET DEFAULT nextval('public.vehicles_id_seq'::regclass);


--
-- Name: workflow_automations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations ALTER COLUMN id SET DEFAULT nextval('public.workflow_automations_id_seq'::regclass);


--
-- Name: workflow_instances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances ALTER COLUMN id SET DEFAULT nextval('public.workflow_instances_id_seq'::regclass);


--
-- Name: workflow_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_metrics ALTER COLUMN id SET DEFAULT nextval('public.workflow_metrics_id_seq'::regclass);


--
-- Name: workflow_performance_snapshots id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_performance_snapshots ALTER COLUMN id SET DEFAULT nextval('public.workflow_performance_snapshots_id_seq'::regclass);


--
-- Name: workflow_sla_instances id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_sla_instances ALTER COLUMN id SET DEFAULT nextval('public.workflow_sla_instances_id_seq'::regclass);


--
-- Name: workflow_slas id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_slas ALTER COLUMN id SET DEFAULT nextval('public.workflow_slas_id_seq'::regclass);


--
-- Name: workflow_step_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_step_metrics ALTER COLUMN id SET DEFAULT nextval('public.workflow_step_metrics_id_seq'::regclass);


--
-- Name: workflow_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_templates ALTER COLUMN id SET DEFAULT nextval('public.workflow_templates_id_seq'::regclass);


--
-- Name: workflow_triggers id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_triggers ALTER COLUMN id SET DEFAULT nextval('public.workflow_triggers_id_seq'::regclass);


--
-- Name: workflow_user_metrics id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_user_metrics ALTER COLUMN id SET DEFAULT nextval('public.workflow_user_metrics_id_seq'::regclass);


--
-- Name: zone_defaults id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_defaults ALTER COLUMN id SET DEFAULT nextval('public.zone_defaults_id_seq'::regclass);


--
-- Name: zones id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones ALTER COLUMN id SET DEFAULT nextval('public.zones_id_seq'::regclass);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (log_id);


--
-- Name: cdc_queue cdc_queue_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.cdc_queue
    ADD CONSTRAINT cdc_queue_pkey PRIMARY KEY (id);


--
-- Name: couriers couriers_email_key; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.couriers
    ADD CONSTRAINT couriers_email_key UNIQUE (email);


--
-- Name: couriers couriers_iqama_number_key; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.couriers
    ADD CONSTRAINT couriers_iqama_number_key UNIQUE (iqama_number);


--
-- Name: couriers couriers_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.couriers
    ADD CONSTRAINT couriers_pkey PRIMARY KEY (barq_id);


--
-- Name: leave_approvals leave_approvals_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.leave_approvals
    ADD CONSTRAINT leave_approvals_pkey PRIMARY KEY (approval_id);


--
-- Name: leave_requests leave_requests_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.leave_requests
    ADD CONSTRAINT leave_requests_pkey PRIMARY KEY (request_id);


--
-- Name: vehicle_assignments vehicle_assignments_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicle_assignments
    ADD CONSTRAINT vehicle_assignments_pkey PRIMARY KEY (assignment_id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (plate_number);


--
-- Name: workflow_instances workflow_instances_pkey; Type: CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.workflow_instances
    ADD CONSTRAINT workflow_instances_pkey PRIMARY KEY (instance_id);


--
-- Name: accident_logs accident_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accident_logs
    ADD CONSTRAINT accident_logs_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: allocations allocations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allocations
    ADD CONSTRAINT allocations_pkey PRIMARY KEY (id);


--
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- Name: approval_chain_approvers approval_chain_approvers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers
    ADD CONSTRAINT approval_chain_approvers_pkey PRIMARY KEY (id);


--
-- Name: approval_chains approval_chains_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chains
    ADD CONSTRAINT approval_chains_pkey PRIMARY KEY (id);


--
-- Name: approval_requests approval_requests_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_pkey PRIMARY KEY (id);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (id);


--
-- Name: assignments assignments_assignment_number_key; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_assignment_number_key UNIQUE (assignment_number);


--
-- Name: assignments assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT assignments_pkey PRIMARY KEY (id);


--
-- Name: attendance attendance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: automation_execution_logs automation_execution_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_execution_logs
    ADD CONSTRAINT automation_execution_logs_pkey PRIMARY KEY (id);


--
-- Name: backups backups_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT backups_pkey PRIMARY KEY (id);


--
-- Name: beds beds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT beds_pkey PRIMARY KEY (id);


--
-- Name: bonuses bonuses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bonuses
    ADD CONSTRAINT bonuses_pkey PRIMARY KEY (id);


--
-- Name: buildings buildings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.buildings
    ADD CONSTRAINT buildings_pkey PRIMARY KEY (id);


--
-- Name: canned_responses canned_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canned_responses
    ADD CONSTRAINT canned_responses_pkey PRIMARY KEY (id);


--
-- Name: canned_responses canned_responses_shortcut_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canned_responses
    ADD CONSTRAINT canned_responses_shortcut_key UNIQUE (shortcut);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_session_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_session_id_key UNIQUE (session_id);


--
-- Name: cod_transactions cod_transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cod_transactions
    ADD CONSTRAINT cod_transactions_pkey PRIMARY KEY (id);


--
-- Name: courier_vehicle_assignments courier_vehicle_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courier_vehicle_assignments
    ADD CONSTRAINT courier_vehicle_assignments_pkey PRIMARY KEY (id);


--
-- Name: couriers couriers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers
    ADD CONSTRAINT couriers_pkey PRIMARY KEY (id);


--
-- Name: customer_feedbacks customer_feedbacks_feedback_number_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_feedback_number_key UNIQUE (feedback_number);


--
-- Name: customer_feedbacks customer_feedbacks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_pkey PRIMARY KEY (id);


--
-- Name: dashboards dashboards_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_pkey PRIMARY KEY (id);


--
-- Name: deliveries deliveries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_pkey PRIMARY KEY (id);


--
-- Name: dispatch_assignments dispatch_assignments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_pkey PRIMARY KEY (id);


--
-- Name: dispatch_rules dispatch_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_rules
    ADD CONSTRAINT dispatch_rules_pkey PRIMARY KEY (id);


--
-- Name: documents documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT documents_pkey PRIMARY KEY (id);


--
-- Name: driver_orders driver_orders_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.driver_orders
    ADD CONSTRAINT driver_orders_pkey PRIMARY KEY (id);


--
-- Name: faqs faqs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT faqs_pkey PRIMARY KEY (id);


--
-- Name: feedback_templates feedback_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_templates
    ADD CONSTRAINT feedback_templates_pkey PRIMARY KEY (id);


--
-- Name: feedback_templates feedback_templates_template_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_templates
    ADD CONSTRAINT feedback_templates_template_code_key UNIQUE (template_code);


--
-- Name: feedbacks feedbacks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_pkey PRIMARY KEY (id);


--
-- Name: fuel_logs fuel_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_logs
    ADD CONSTRAINT fuel_logs_pkey PRIMARY KEY (id);


--
-- Name: handovers handovers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: integrations integrations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT integrations_pkey PRIMARY KEY (id);


--
-- Name: kb_articles kb_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_articles
    ADD CONSTRAINT kb_articles_pkey PRIMARY KEY (id);


--
-- Name: kb_articles kb_articles_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_articles
    ADD CONSTRAINT kb_articles_slug_key UNIQUE (slug);


--
-- Name: kb_categories kb_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_categories
    ADD CONSTRAINT kb_categories_pkey PRIMARY KEY (id);


--
-- Name: kb_categories kb_categories_slug_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_categories
    ADD CONSTRAINT kb_categories_slug_key UNIQUE (slug);


--
-- Name: kpis kpis_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpis
    ADD CONSTRAINT kpis_code_key UNIQUE (code);


--
-- Name: kpis kpis_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpis
    ADD CONSTRAINT kpis_pkey PRIMARY KEY (id);


--
-- Name: leaves leaves_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT leaves_pkey PRIMARY KEY (id);


--
-- Name: loans loans_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_pkey PRIMARY KEY (id);


--
-- Name: metric_snapshots metric_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_snapshots
    ADD CONSTRAINT metric_snapshots_pkey PRIMARY KEY (id);


--
-- Name: notification_settings notification_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_settings
    ADD CONSTRAINT notification_settings_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: operations_documents operations_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_documents
    ADD CONSTRAINT operations_documents_pkey PRIMARY KEY (id);


--
-- Name: operations_settings operations_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_settings
    ADD CONSTRAINT operations_settings_pkey PRIMARY KEY (id);


--
-- Name: orders orders_order_number_key; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_order_number_key UNIQUE (order_number);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: organization_users organization_users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_users
    ADD CONSTRAINT organization_users_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_token_hash_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_token_hash_key UNIQUE (token_hash);


--
-- Name: performance_data performance_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_data
    ADD CONSTRAINT performance_data_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: priority_queue_entries priority_queue_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT priority_queue_entries_pkey PRIMARY KEY (id);


--
-- Name: quality_inspections quality_inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_pkey PRIMARY KEY (id);


--
-- Name: quality_metrics quality_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_metrics
    ADD CONSTRAINT quality_metrics_pkey PRIMARY KEY (id);


--
-- Name: reports reports_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: rooms rooms_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_pkey PRIMARY KEY (id);


--
-- Name: routes routes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (id);


--
-- Name: salaries salaries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries
    ADD CONSTRAINT salaries_pkey PRIMARY KEY (id);


--
-- Name: sla_definitions sla_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_definitions
    ADD CONSTRAINT sla_definitions_pkey PRIMARY KEY (id);


--
-- Name: sla_events sla_events_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_events
    ADD CONSTRAINT sla_events_pkey PRIMARY KEY (id);


--
-- Name: sla_thresholds sla_thresholds_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_thresholds
    ADD CONSTRAINT sla_thresholds_pkey PRIMARY KEY (id);


--
-- Name: sla_tracking sla_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_pkey PRIMARY KEY (id);


--
-- Name: sub_projects sub_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects
    ADD CONSTRAINT sub_projects_pkey PRIMARY KEY (id);


--
-- Name: sub_projects sub_projects_project_code_key; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects
    ADD CONSTRAINT sub_projects_project_code_key UNIQUE (project_code);


--
-- Name: system_settings system_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT system_settings_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_pkey PRIMARY KEY (id);


--
-- Name: tasks tasks_task_number_key; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT tasks_task_number_key UNIQUE (task_number);


--
-- Name: ticket_attachments ticket_attachments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_pkey PRIMARY KEY (id);


--
-- Name: ticket_replies ticket_replies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_replies
    ADD CONSTRAINT ticket_replies_pkey PRIMARY KEY (id);


--
-- Name: ticket_templates ticket_templates_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_templates
    ADD CONSTRAINT ticket_templates_name_key UNIQUE (name);


--
-- Name: ticket_templates ticket_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_templates
    ADD CONSTRAINT ticket_templates_pkey PRIMARY KEY (id);


--
-- Name: tickets tickets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_pkey PRIMARY KEY (id);


--
-- Name: tickets tickets_ticket_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_ticket_id_key UNIQUE (ticket_id);


--
-- Name: trigger_executions trigger_executions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trigger_executions
    ADD CONSTRAINT trigger_executions_pkey PRIMARY KEY (id);


--
-- Name: attendance uq_attendance_courier_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT uq_attendance_courier_date UNIQUE (courier_id, date, organization_id);


--
-- Name: beds uq_bed_room_number; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT uq_bed_room_number UNIQUE (room_id, bed_number);


--
-- Name: deliveries uq_delivery_tracking_number; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT uq_delivery_tracking_number UNIQUE (tracking_number);


--
-- Name: driver_orders uq_driver_order_platform; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.driver_orders
    ADD CONSTRAINT uq_driver_order_platform UNIQUE (platform, platform_order_id, organization_id);


--
-- Name: organization_users uq_organization_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_users
    ADD CONSTRAINT uq_organization_user UNIQUE (organization_id, user_id);


--
-- Name: performance_data uq_performance_courier_date; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_data
    ADD CONSTRAINT uq_performance_courier_date UNIQUE (courier_id, date);


--
-- Name: rooms uq_room_building_number; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT uq_room_building_number UNIQUE (building_id, room_number);


--
-- Name: salaries uq_salary_courier_month_year; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries
    ADD CONSTRAINT uq_salary_courier_month_year UNIQUE (courier_id, month, year);


--
-- Name: salaries uq_salary_courier_period; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries
    ADD CONSTRAINT uq_salary_courier_period UNIQUE (courier_id, year, month, organization_id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vehicle_data vehicle_data_pkey; Type: CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.vehicle_data
    ADD CONSTRAINT vehicle_data_pkey PRIMARY KEY (id);


--
-- Name: vehicle_inspections vehicle_inspections_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT vehicle_inspections_pkey PRIMARY KEY (id);


--
-- Name: vehicle_logs vehicle_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_logs
    ADD CONSTRAINT vehicle_logs_pkey PRIMARY KEY (id);


--
-- Name: vehicle_maintenance vehicle_maintenance_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_maintenance
    ADD CONSTRAINT vehicle_maintenance_pkey PRIMARY KEY (id);


--
-- Name: vehicles vehicles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT vehicles_pkey PRIMARY KEY (id);


--
-- Name: workflow_automations workflow_automations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT workflow_automations_pkey PRIMARY KEY (id);


--
-- Name: workflow_instances workflow_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_pkey PRIMARY KEY (id);


--
-- Name: workflow_metrics workflow_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_metrics
    ADD CONSTRAINT workflow_metrics_pkey PRIMARY KEY (id);


--
-- Name: workflow_performance_snapshots workflow_performance_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_performance_snapshots
    ADD CONSTRAINT workflow_performance_snapshots_pkey PRIMARY KEY (id);


--
-- Name: workflow_sla_instances workflow_sla_instances_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_sla_instances
    ADD CONSTRAINT workflow_sla_instances_pkey PRIMARY KEY (id);


--
-- Name: workflow_slas workflow_slas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_slas
    ADD CONSTRAINT workflow_slas_pkey PRIMARY KEY (id);


--
-- Name: workflow_step_metrics workflow_step_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_step_metrics
    ADD CONSTRAINT workflow_step_metrics_pkey PRIMARY KEY (id);


--
-- Name: workflow_templates workflow_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_templates
    ADD CONSTRAINT workflow_templates_pkey PRIMARY KEY (id);


--
-- Name: workflow_triggers workflow_triggers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_triggers
    ADD CONSTRAINT workflow_triggers_pkey PRIMARY KEY (id);


--
-- Name: workflow_user_metrics workflow_user_metrics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_user_metrics
    ADD CONSTRAINT workflow_user_metrics_pkey PRIMARY KEY (id);


--
-- Name: zone_defaults zone_defaults_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_defaults
    ADD CONSTRAINT zone_defaults_pkey PRIMARY KEY (id);


--
-- Name: zones zones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (id);


--
-- Name: idx_assignment_active; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_assignment_active ON barq.vehicle_assignments USING btree (returned_date) WHERE (returned_date IS NULL);


--
-- Name: idx_assignment_courier; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_assignment_courier ON barq.vehicle_assignments USING btree (courier_id);


--
-- Name: idx_assignment_dates; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_assignment_dates ON barq.vehicle_assignments USING btree (assigned_date DESC);


--
-- Name: idx_assignment_vehicle; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_assignment_vehicle ON barq.vehicle_assignments USING btree (vehicle_plate);


--
-- Name: idx_audit_action; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_audit_action ON barq.audit_logs USING btree (action);


--
-- Name: idx_audit_created; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_audit_created ON barq.audit_logs USING btree (created_at DESC);


--
-- Name: idx_audit_entity; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_audit_entity ON barq.audit_logs USING btree (entity_type, entity_id);


--
-- Name: idx_audit_user; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_audit_user ON barq.audit_logs USING btree (user_id);


--
-- Name: idx_cdc_queue_unprocessed; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_cdc_queue_unprocessed ON barq.cdc_queue USING btree (created_at) WHERE (processed = false);


--
-- Name: idx_courier_city; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_city ON barq.couriers USING btree (city) WHERE (is_deleted = false);


--
-- Name: idx_courier_composite; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_composite ON barq.couriers USING btree (status, city, department) WHERE (is_deleted = false);


--
-- Name: idx_courier_department; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_department ON barq.couriers USING btree (department) WHERE (is_deleted = false);


--
-- Name: idx_courier_email; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_email ON barq.couriers USING btree (email) WHERE (is_deleted = false);


--
-- Name: idx_courier_iqama; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_iqama ON barq.couriers USING btree (iqama_number) WHERE (is_deleted = false);


--
-- Name: idx_courier_join_date; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_join_date ON barq.couriers USING btree (join_date DESC);


--
-- Name: idx_courier_phone; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_phone ON barq.couriers USING btree (phone) WHERE (is_deleted = false);


--
-- Name: idx_courier_status; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_courier_status ON barq.couriers USING btree (status) WHERE (is_deleted = false);


--
-- Name: idx_leave_approval_approver; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_approval_approver ON barq.leave_approvals USING btree (approver_id);


--
-- Name: idx_leave_approval_request; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_approval_request ON barq.leave_approvals USING btree (request_id);


--
-- Name: idx_leave_courier; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_courier ON barq.leave_requests USING btree (courier_id);


--
-- Name: idx_leave_created; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_created ON barq.leave_requests USING btree (created_at DESC);


--
-- Name: idx_leave_dates; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_dates ON barq.leave_requests USING btree (start_date, end_date);


--
-- Name: idx_leave_payroll; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_payroll ON barq.leave_requests USING btree (payroll_month);


--
-- Name: idx_leave_status; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_leave_status ON barq.leave_requests USING btree (status);


--
-- Name: idx_vehicle_assigned; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_assigned ON barq.vehicles USING btree (assigned_to) WHERE (is_deleted = false);


--
-- Name: idx_vehicle_city; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_city ON barq.vehicles USING btree (city) WHERE (is_deleted = false);


--
-- Name: idx_vehicle_expiry; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_expiry ON barq.vehicles USING btree (insurance_expiry, registration_expiry);


--
-- Name: idx_vehicle_maintenance; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_maintenance ON barq.vehicles USING btree (next_maintenance) WHERE (is_deleted = false);


--
-- Name: idx_vehicle_status; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_status ON barq.vehicles USING btree (status) WHERE (is_deleted = false);


--
-- Name: idx_vehicle_type; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_type ON barq.vehicles USING btree (vehicle_type) WHERE (is_deleted = false);


--
-- Name: idx_workflow_assigned; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_assigned ON barq.workflow_instances USING btree (assigned_to) WHERE ((current_state)::text <> 'Completed'::text);


--
-- Name: idx_workflow_created; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_created ON barq.workflow_instances USING btree (created_at DESC);


--
-- Name: idx_workflow_data; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_data ON barq.workflow_instances USING gin (data);


--
-- Name: idx_workflow_entity; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_entity ON barq.workflow_instances USING btree (entity_type, entity_id);


--
-- Name: idx_workflow_state; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_state ON barq.workflow_instances USING btree (current_state);


--
-- Name: idx_workflow_type; Type: INDEX; Schema: barq; Owner: ramiz_new
--

CREATE INDEX idx_workflow_type ON barq.workflow_instances USING btree (workflow_type);


--
-- Name: idx_accident_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_accident_logs_created_at ON public.accident_logs USING btree (created_at);


--
-- Name: idx_assignments_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_active ON public.courier_vehicle_assignments USING btree (courier_id, vehicle_id, start_date) WHERE (((status)::text = 'active'::text) AND (end_date IS NULL));


--
-- Name: idx_assignments_courier; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_courier ON public.assignments USING btree (courier_id);


--
-- Name: idx_assignments_courier_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_courier_dates ON public.courier_vehicle_assignments USING btree (courier_id, start_date, end_date);


--
-- Name: idx_assignments_number; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_number ON public.assignments USING btree (assignment_number);


--
-- Name: idx_assignments_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_org_status ON public.courier_vehicle_assignments USING btree (organization_id, status);


--
-- Name: idx_assignments_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_organization ON public.assignments USING btree (organization_id);


--
-- Name: idx_assignments_start_date; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_start_date ON public.assignments USING btree (start_date);


--
-- Name: idx_assignments_status; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_status ON public.assignments USING btree (status);


--
-- Name: idx_assignments_type; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_type ON public.assignments USING btree (assignment_type);


--
-- Name: idx_assignments_vehicle; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_assignments_vehicle ON public.assignments USING btree (vehicle_id);


--
-- Name: idx_assignments_vehicle_dates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_assignments_vehicle_dates ON public.courier_vehicle_assignments USING btree (vehicle_id, start_date, end_date);


--
-- Name: idx_attendance_absent; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_absent ON public.attendance USING btree (courier_id, date) WHERE (status = 'absent'::public.attendancestatus);


--
-- Name: idx_attendance_courier_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_courier_date ON public.attendance USING btree (courier_id, date);


--
-- Name: idx_attendance_date_brin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_date_brin ON public.attendance USING brin (date, created_at);


--
-- Name: idx_attendance_org_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_attendance_org_date ON public.attendance USING btree (organization_id, date, status);


--
-- Name: idx_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: idx_bonuses_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_bonuses_created_at ON public.bonuses USING btree (created_at);


--
-- Name: idx_cod_collection_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cod_collection_date ON public.cod_transactions USING btree (collection_date, status);


--
-- Name: idx_cod_courier_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cod_courier_status ON public.cod_transactions USING btree (courier_id, status, collection_date);


--
-- Name: idx_cod_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cod_org_status ON public.cod_transactions USING btree (organization_id, status, collection_date);


--
-- Name: idx_cod_pending; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cod_pending ON public.cod_transactions USING btree (courier_id, collection_date DESC) WHERE (status = 'pending'::public.codstatus);


--
-- Name: idx_couriers_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_active ON public.couriers USING btree (organization_id, joining_date DESC) WHERE (status = 'ACTIVE'::public.courierstatus);


--
-- Name: idx_couriers_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_created_at ON public.couriers USING btree (created_at);


--
-- Name: idx_couriers_fms_asset; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_fms_asset ON public.couriers USING btree (fms_asset_id) WHERE (fms_asset_id IS NOT NULL);


--
-- Name: idx_couriers_iqama_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_iqama_expiry ON public.couriers USING btree (iqama_expiry_date) WHERE (iqama_expiry_date IS NOT NULL);


--
-- Name: idx_couriers_license_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_license_expiry ON public.couriers USING btree (license_expiry_date) WHERE (license_expiry_date IS NOT NULL);


--
-- Name: idx_couriers_no_vehicle; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_no_vehicle ON public.couriers USING btree (organization_id, id) WHERE ((current_vehicle_id IS NULL) AND (status = 'ACTIVE'::public.courierstatus));


--
-- Name: idx_couriers_org_city_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_org_city_status ON public.couriers USING btree (organization_id, city, status);


--
-- Name: idx_couriers_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_couriers_org_status ON public.couriers USING btree (organization_id, status);


--
-- Name: idx_customer_feedbacks_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_category ON public.customer_feedbacks USING btree (category);


--
-- Name: idx_customer_feedbacks_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_courier_id ON public.customer_feedbacks USING btree (courier_id);


--
-- Name: idx_customer_feedbacks_delivery_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_delivery_id ON public.customer_feedbacks USING btree (delivery_id);


--
-- Name: idx_customer_feedbacks_feedback_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_feedback_number ON public.customer_feedbacks USING btree (feedback_number);


--
-- Name: idx_customer_feedbacks_feedback_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_feedback_type ON public.customer_feedbacks USING btree (feedback_type);


--
-- Name: idx_customer_feedbacks_is_complaint; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_is_complaint ON public.customer_feedbacks USING btree (is_complaint);


--
-- Name: idx_customer_feedbacks_is_compliment; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_is_compliment ON public.customer_feedbacks USING btree (is_compliment);


--
-- Name: idx_customer_feedbacks_is_escalated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_is_escalated ON public.customer_feedbacks USING btree (is_escalated);


--
-- Name: idx_customer_feedbacks_order_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_order_number ON public.customer_feedbacks USING btree (order_number);


--
-- Name: idx_customer_feedbacks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_customer_feedbacks_status ON public.customer_feedbacks USING btree (status);


--
-- Name: idx_dashboard_shared; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dashboard_shared ON public.dashboards USING btree (is_shared, created_at);


--
-- Name: idx_dashboard_user_default; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dashboard_user_default ON public.dashboards USING btree (user_id, is_default);


--
-- Name: idx_deliveries_cod; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_cod ON public.deliveries USING btree (courier_id, status, cod_amount) WHERE (cod_amount > 0);


--
-- Name: idx_deliveries_courier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_courier ON public.deliveries USING btree (courier_id);


--
-- Name: idx_deliveries_courier_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_courier_status ON public.deliveries USING btree (courier_id, status, created_at);


--
-- Name: idx_deliveries_delivery_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_delivery_time ON public.deliveries USING btree (delivery_time) WHERE (delivery_time IS NOT NULL);


--
-- Name: idx_deliveries_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_org_status ON public.deliveries USING btree (organization_id, status, created_at);


--
-- Name: idx_deliveries_pending; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_pending ON public.deliveries USING btree (organization_id, courier_id, created_at DESC) WHERE (status = 'pending'::public.deliverystatus);


--
-- Name: idx_deliveries_pickup_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_deliveries_pickup_time ON public.deliveries USING btree (pickup_time) WHERE (pickup_time IS NOT NULL);


--
-- Name: idx_deliveries_tracking; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_deliveries_tracking ON public.deliveries USING btree (tracking_number text_pattern_ops);


--
-- Name: idx_dimensions_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_dimensions_gin ON public.metric_snapshots USING gin (dimensions);


--
-- Name: idx_driver_orders_courier; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_driver_orders_courier ON public.driver_orders USING btree (courier_id);


--
-- Name: idx_driver_orders_date; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_driver_orders_date ON public.driver_orders USING btree (order_date);


--
-- Name: idx_driver_orders_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_driver_orders_organization ON public.driver_orders USING btree (organization_id);


--
-- Name: idx_driver_orders_platform; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_driver_orders_platform ON public.driver_orders USING btree (platform, platform_driver_id);


--
-- Name: idx_driver_orders_status; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_driver_orders_status ON public.driver_orders USING btree (status);


--
-- Name: idx_feedback_templates_template_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_templates_template_code ON public.feedback_templates USING btree (template_code);


--
-- Name: idx_feedback_templates_template_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_feedback_templates_template_type ON public.feedback_templates USING btree (template_type);


--
-- Name: idx_fuel_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_fuel_logs_created_at ON public.fuel_logs USING btree (created_at);


--
-- Name: idx_kpi_category_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_kpi_category_active ON public.kpis USING btree (category, is_active);


--
-- Name: idx_leaves_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leaves_created_at ON public.leaves USING btree (created_at);


--
-- Name: idx_loans_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_loans_created_at ON public.loans USING btree (created_at);


--
-- Name: idx_metric_name_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_metric_name_timestamp ON public.metric_snapshots USING btree (metric_name, "timestamp");


--
-- Name: idx_notifications_courier; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_courier ON public.notifications USING btree (courier_id);


--
-- Name: idx_notifications_created; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_created ON public.notifications USING btree (created_at DESC);


--
-- Name: idx_notifications_org; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_org ON public.notifications USING btree (organization_id);


--
-- Name: idx_notifications_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_notifications_user ON public.notifications USING btree (user_id);


--
-- Name: idx_orders_courier; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_courier ON public.orders USING btree (courier_id);


--
-- Name: idx_orders_created; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_created ON public.orders USING btree (created_at);


--
-- Name: idx_orders_date; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_date ON public.orders USING btree (order_date);


--
-- Name: idx_orders_number; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_number ON public.orders USING btree (order_number);


--
-- Name: idx_orders_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_organization ON public.orders USING btree (organization_id);


--
-- Name: idx_orders_status; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_orders_status ON public.orders USING btree (status);


--
-- Name: idx_report_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_type_status ON public.reports USING btree (report_type, status);


--
-- Name: idx_report_user; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_report_user ON public.reports USING btree (generated_by_user_id, generated_at);


--
-- Name: idx_salaries_courier_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_salaries_courier_period ON public.salaries USING btree (courier_id, year, month);


--
-- Name: idx_salaries_org_period; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_salaries_org_period ON public.salaries USING btree (organization_id, year, month);


--
-- Name: idx_salaries_payment_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_salaries_payment_date ON public.salaries USING btree (payment_date) WHERE (payment_date IS NOT NULL);


--
-- Name: idx_salaries_unique_month; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_salaries_unique_month ON public.salaries USING btree (courier_id, year, month);


--
-- Name: idx_sub_projects_code; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_sub_projects_code ON public.sub_projects USING btree (project_code);


--
-- Name: idx_sub_projects_created; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_sub_projects_created ON public.sub_projects USING btree (created_at);


--
-- Name: idx_sub_projects_manager; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_sub_projects_manager ON public.sub_projects USING btree (manager_id);


--
-- Name: idx_sub_projects_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_sub_projects_organization ON public.sub_projects USING btree (organization_id);


--
-- Name: idx_sub_projects_status; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_sub_projects_status ON public.sub_projects USING btree (status);


--
-- Name: idx_tags_gin; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tags_gin ON public.metric_snapshots USING gin (tags);


--
-- Name: idx_task_assigned; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_assigned ON public.tasks USING btree (assigned_to);


--
-- Name: idx_task_courier; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_courier ON public.tasks USING btree (courier_id);


--
-- Name: idx_task_created; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_created ON public.tasks USING btree (created_at);


--
-- Name: idx_task_due_date; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_due_date ON public.tasks USING btree (due_date);


--
-- Name: idx_task_number; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_number ON public.tasks USING btree (task_number);


--
-- Name: idx_task_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_organization ON public.tasks USING btree (organization_id);


--
-- Name: idx_task_status; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_task_status ON public.tasks USING btree (status);


--
-- Name: idx_tickets_assigned; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_assigned ON public.tickets USING btree (assigned_to, status) WHERE (assigned_to IS NOT NULL);


--
-- Name: idx_tickets_open; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_open ON public.tickets USING btree (organization_id, priority, created_at DESC) WHERE (status = ANY (ARRAY['open'::public.ticketstatus, 'in_progress'::public.ticketstatus]));


--
-- Name: idx_tickets_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_tickets_org_status ON public.tickets USING btree (organization_id, status, created_at);


--
-- Name: idx_vehicle_data_courier; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_courier ON public.vehicle_data USING btree (courier_id);


--
-- Name: idx_vehicle_data_device; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_device ON public.vehicle_data USING btree (device_id);


--
-- Name: idx_vehicle_data_organization; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_organization ON public.vehicle_data USING btree (organization_id);


--
-- Name: idx_vehicle_data_timestamp; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_timestamp ON public.vehicle_data USING btree ("timestamp");


--
-- Name: idx_vehicle_data_type; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_type ON public.vehicle_data USING btree (data_type);


--
-- Name: idx_vehicle_data_vehicle; Type: INDEX; Schema: public; Owner: ramiz_new
--

CREATE INDEX idx_vehicle_data_vehicle ON public.vehicle_data USING btree (vehicle_id);


--
-- Name: idx_vehicle_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicle_logs_created_at ON public.vehicle_logs USING btree (created_at);


--
-- Name: idx_vehicles_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_active ON public.vehicles USING btree (organization_id, vehicle_type) WHERE ((status)::text = 'ACTIVE'::text);


--
-- Name: idx_vehicles_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_city ON public.vehicles USING btree (assigned_to_city, status) WHERE (assigned_to_city IS NOT NULL);


--
-- Name: idx_vehicles_insurance_expiry; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_insurance_expiry ON public.vehicles USING btree (insurance_expiry_date) WHERE (insurance_expiry_date IS NOT NULL);


--
-- Name: idx_vehicles_next_service; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_next_service ON public.vehicles USING btree (next_service_due_date) WHERE ((next_service_due_date IS NOT NULL) AND ((status)::text = 'ACTIVE'::text));


--
-- Name: idx_vehicles_org_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_org_status ON public.vehicles USING btree (organization_id, status);


--
-- Name: idx_vehicles_org_type_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_vehicles_org_type_status ON public.vehicles USING btree (organization_id, vehicle_type, status);


--
-- Name: idx_workflow_instances_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_workflow_instances_created_at ON public.workflow_instances USING btree (created_at);


--
-- Name: ix_accident_logs_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accident_logs_organization_id ON public.accident_logs USING btree (organization_id);


--
-- Name: ix_accidents_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_city ON public.accident_logs USING btree (city);


--
-- Name: ix_accidents_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_courier_id ON public.accident_logs USING btree (courier_id);


--
-- Name: ix_accidents_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_date ON public.accident_logs USING btree (accident_date);


--
-- Name: ix_accidents_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_id ON public.accident_logs USING btree (id);


--
-- Name: ix_accidents_severity; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_severity ON public.accident_logs USING btree (severity);


--
-- Name: ix_accidents_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_status ON public.accident_logs USING btree (status);


--
-- Name: ix_accidents_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_accidents_vehicle_id ON public.accident_logs USING btree (vehicle_id);


--
-- Name: ix_allocations_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocations_active ON public.allocations USING btree (courier_id, release_date);


--
-- Name: ix_allocations_allocation_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocations_allocation_date ON public.allocations USING btree (allocation_date);


--
-- Name: ix_allocations_bed_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocations_bed_id ON public.allocations USING btree (bed_id);


--
-- Name: ix_allocations_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocations_courier_id ON public.allocations USING btree (courier_id);


--
-- Name: ix_allocations_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_allocations_organization_id ON public.allocations USING btree (organization_id);


--
-- Name: ix_api_keys_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_api_keys_id ON public.api_keys USING btree (id);


--
-- Name: ix_api_keys_key_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_api_keys_key_hash ON public.api_keys USING btree (key_hash);


--
-- Name: ix_api_keys_key_prefix; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_api_keys_key_prefix ON public.api_keys USING btree (key_prefix);


--
-- Name: ix_api_keys_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_api_keys_organization_id ON public.api_keys USING btree (organization_id);


--
-- Name: ix_approval_chain_approvers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_chain_approvers_id ON public.approval_chain_approvers USING btree (id);


--
-- Name: ix_approval_chain_approvers_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_chain_approvers_organization_id ON public.approval_chain_approvers USING btree (organization_id);


--
-- Name: ix_approval_chains_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_chains_id ON public.approval_chains USING btree (id);


--
-- Name: ix_approval_chains_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_chains_organization_id ON public.approval_chains USING btree (organization_id);


--
-- Name: ix_approval_requests_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_requests_id ON public.approval_requests USING btree (id);


--
-- Name: ix_approval_requests_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_approval_requests_organization_id ON public.approval_requests USING btree (organization_id);


--
-- Name: ix_assets_asset_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assets_asset_type ON public.assets USING btree (asset_type);


--
-- Name: ix_assets_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assets_courier_id ON public.assets USING btree (courier_id);


--
-- Name: ix_assets_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assets_organization_id ON public.assets USING btree (organization_id);


--
-- Name: ix_assets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assets_status ON public.assets USING btree (status);


--
-- Name: ix_assignments_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assignments_courier_id ON public.courier_vehicle_assignments USING btree (courier_id);


--
-- Name: ix_assignments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assignments_id ON public.courier_vehicle_assignments USING btree (id);


--
-- Name: ix_assignments_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assignments_start_date ON public.courier_vehicle_assignments USING btree (start_date);


--
-- Name: ix_assignments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assignments_status ON public.courier_vehicle_assignments USING btree (status);


--
-- Name: ix_assignments_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_assignments_vehicle_id ON public.courier_vehicle_assignments USING btree (vehicle_id);


--
-- Name: ix_attendance_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_courier_id ON public.attendance USING btree (courier_id);


--
-- Name: ix_attendance_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_date ON public.attendance USING btree (date);


--
-- Name: ix_attendance_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_organization_id ON public.attendance USING btree (organization_id);


--
-- Name: ix_attendance_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_attendance_status ON public.attendance USING btree (status);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- Name: ix_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_id ON public.audit_logs USING btree (resource_id);


--
-- Name: ix_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_type ON public.audit_logs USING btree (resource_type);


--
-- Name: ix_automation_execution_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_automation_execution_logs_id ON public.automation_execution_logs USING btree (id);


--
-- Name: ix_automation_execution_logs_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_automation_execution_logs_organization_id ON public.automation_execution_logs USING btree (organization_id);


--
-- Name: ix_backups_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_backups_id ON public.backups USING btree (id);


--
-- Name: ix_backups_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_backups_organization_id ON public.backups USING btree (organization_id);


--
-- Name: ix_beds_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_beds_organization_id ON public.beds USING btree (organization_id);


--
-- Name: ix_beds_room_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_beds_room_id ON public.beds USING btree (room_id);


--
-- Name: ix_beds_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_beds_status ON public.beds USING btree (status);


--
-- Name: ix_bonuses_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bonuses_id ON public.bonuses USING btree (id);


--
-- Name: ix_bonuses_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_bonuses_organization_id ON public.bonuses USING btree (organization_id);


--
-- Name: ix_buildings_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_buildings_name ON public.buildings USING btree (name);


--
-- Name: ix_buildings_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_buildings_organization_id ON public.buildings USING btree (organization_id);


--
-- Name: ix_canned_responses_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_canned_responses_category ON public.canned_responses USING btree (category);


--
-- Name: ix_canned_responses_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_canned_responses_id ON public.canned_responses USING btree (id);


--
-- Name: ix_canned_responses_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_canned_responses_is_active ON public.canned_responses USING btree (is_active);


--
-- Name: ix_canned_responses_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_canned_responses_organization_id ON public.canned_responses USING btree (organization_id);


--
-- Name: ix_chat_messages_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_messages_organization_id ON public.chat_messages USING btree (organization_id);


--
-- Name: ix_chat_messages_sender_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_messages_sender_id ON public.chat_messages USING btree (sender_id);


--
-- Name: ix_chat_messages_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_messages_session_id ON public.chat_messages USING btree (session_id);


--
-- Name: ix_chat_sessions_agent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_agent_id ON public.chat_sessions USING btree (agent_id);


--
-- Name: ix_chat_sessions_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_customer_id ON public.chat_sessions USING btree (customer_id);


--
-- Name: ix_chat_sessions_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_organization_id ON public.chat_sessions USING btree (organization_id);


--
-- Name: ix_chat_sessions_session_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_chat_sessions_session_id ON public.chat_sessions USING btree (session_id);


--
-- Name: ix_chat_sessions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_sessions_status ON public.chat_sessions USING btree (status);


--
-- Name: ix_cod_transactions_collection_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cod_transactions_collection_date ON public.cod_transactions USING btree (collection_date);


--
-- Name: ix_cod_transactions_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cod_transactions_courier_id ON public.cod_transactions USING btree (courier_id);


--
-- Name: ix_cod_transactions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cod_transactions_status ON public.cod_transactions USING btree (status);


--
-- Name: ix_courier_vehicle_assignments_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_courier_vehicle_assignments_organization_id ON public.courier_vehicle_assignments USING btree (organization_id);


--
-- Name: ix_couriers_barq_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_couriers_barq_id ON public.couriers USING btree (barq_id);


--
-- Name: ix_couriers_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_couriers_city ON public.couriers USING btree (city);


--
-- Name: ix_couriers_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_couriers_email ON public.couriers USING btree (email);


--
-- Name: ix_couriers_fms_asset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_couriers_fms_asset_id ON public.couriers USING btree (fms_asset_id);


--
-- Name: ix_couriers_full_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_couriers_full_name ON public.couriers USING btree (full_name);


--
-- Name: ix_couriers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_couriers_id ON public.couriers USING btree (id);


--
-- Name: ix_couriers_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_couriers_organization_id ON public.couriers USING btree (organization_id);


--
-- Name: ix_couriers_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_couriers_status ON public.couriers USING btree (status);


--
-- Name: ix_customer_feedbacks_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_customer_feedbacks_organization_id ON public.customer_feedbacks USING btree (organization_id);


--
-- Name: ix_dashboards_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dashboards_id ON public.dashboards USING btree (id);


--
-- Name: ix_dashboards_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dashboards_organization_id ON public.dashboards USING btree (organization_id);


--
-- Name: ix_dashboards_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dashboards_user_id ON public.dashboards USING btree (user_id);


--
-- Name: ix_deliveries_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deliveries_courier_id ON public.deliveries USING btree (courier_id);


--
-- Name: ix_deliveries_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deliveries_created_at ON public.deliveries USING btree (created_at);


--
-- Name: ix_deliveries_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deliveries_organization_id ON public.deliveries USING btree (organization_id);


--
-- Name: ix_deliveries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deliveries_status ON public.deliveries USING btree (status);


--
-- Name: ix_deliveries_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_deliveries_tracking_number ON public.deliveries USING btree (tracking_number);


--
-- Name: ix_dispatch_assignments_assignment_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_dispatch_assignments_assignment_number ON public.dispatch_assignments USING btree (assignment_number);


--
-- Name: ix_dispatch_assignments_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_courier_id ON public.dispatch_assignments USING btree (courier_id);


--
-- Name: ix_dispatch_assignments_delivery_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_delivery_id ON public.dispatch_assignments USING btree (delivery_id);


--
-- Name: ix_dispatch_assignments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_id ON public.dispatch_assignments USING btree (id);


--
-- Name: ix_dispatch_assignments_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_organization_id ON public.dispatch_assignments USING btree (organization_id);


--
-- Name: ix_dispatch_assignments_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_priority ON public.dispatch_assignments USING btree (priority);


--
-- Name: ix_dispatch_assignments_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_status ON public.dispatch_assignments USING btree (status);


--
-- Name: ix_dispatch_assignments_zone_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_assignments_zone_id ON public.dispatch_assignments USING btree (zone_id);


--
-- Name: ix_dispatch_rules_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_rules_is_active ON public.dispatch_rules USING btree (is_active);


--
-- Name: ix_dispatch_rules_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_rules_organization_id ON public.dispatch_rules USING btree (organization_id);


--
-- Name: ix_dispatch_rules_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_rules_priority ON public.dispatch_rules USING btree (priority);


--
-- Name: ix_dispatch_rules_rule_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_dispatch_rules_rule_code ON public.dispatch_rules USING btree (rule_code);


--
-- Name: ix_documents_document_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_document_type ON public.documents USING btree (document_type);


--
-- Name: ix_documents_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_entity_id ON public.documents USING btree (entity_id);


--
-- Name: ix_documents_entity_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_entity_type ON public.documents USING btree (entity_type);


--
-- Name: ix_documents_entity_type_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_entity_type_entity_id ON public.documents USING btree (entity_type, entity_id);


--
-- Name: ix_documents_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_id ON public.documents USING btree (id);


--
-- Name: ix_documents_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_documents_organization_id ON public.documents USING btree (organization_id);


--
-- Name: ix_faqs_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_faqs_category ON public.faqs USING btree (category);


--
-- Name: ix_faqs_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_faqs_is_active ON public.faqs USING btree (is_active);


--
-- Name: ix_faqs_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_faqs_organization_id ON public.faqs USING btree (organization_id);


--
-- Name: ix_faqs_question; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_faqs_question ON public.faqs USING btree (question);


--
-- Name: ix_feedback_templates_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_feedback_templates_organization_id ON public.feedback_templates USING btree (organization_id);


--
-- Name: ix_feedbacks_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_feedbacks_category ON public.feedbacks USING btree (category);


--
-- Name: ix_feedbacks_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_feedbacks_organization_id ON public.feedbacks USING btree (organization_id);


--
-- Name: ix_feedbacks_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_feedbacks_status ON public.feedbacks USING btree (status);


--
-- Name: ix_feedbacks_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_feedbacks_user_id ON public.feedbacks USING btree (user_id);


--
-- Name: ix_fuel_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fuel_logs_id ON public.fuel_logs USING btree (id);


--
-- Name: ix_fuel_logs_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_fuel_logs_organization_id ON public.fuel_logs USING btree (organization_id);


--
-- Name: ix_handovers_from_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_from_courier_id ON public.handovers USING btree (from_courier_id);


--
-- Name: ix_handovers_handover_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_handovers_handover_number ON public.handovers USING btree (handover_number);


--
-- Name: ix_handovers_handover_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_handover_type ON public.handovers USING btree (handover_type);


--
-- Name: ix_handovers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_id ON public.handovers USING btree (id);


--
-- Name: ix_handovers_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_organization_id ON public.handovers USING btree (organization_id);


--
-- Name: ix_handovers_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_status ON public.handovers USING btree (status);


--
-- Name: ix_handovers_to_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_to_courier_id ON public.handovers USING btree (to_courier_id);


--
-- Name: ix_handovers_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_handovers_vehicle_id ON public.handovers USING btree (vehicle_id);


--
-- Name: ix_incidents_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_courier_id ON public.incidents USING btree (courier_id);


--
-- Name: ix_incidents_incident_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_incident_date ON public.incidents USING btree (incident_date);


--
-- Name: ix_incidents_incident_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_incident_type ON public.incidents USING btree (incident_type);


--
-- Name: ix_incidents_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_organization_id ON public.incidents USING btree (organization_id);


--
-- Name: ix_incidents_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_status ON public.incidents USING btree (status);


--
-- Name: ix_incidents_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_incidents_vehicle_id ON public.incidents USING btree (vehicle_id);


--
-- Name: ix_inspections_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inspections_date ON public.vehicle_inspections USING btree (inspection_date);


--
-- Name: ix_inspections_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inspections_id ON public.vehicle_inspections USING btree (id);


--
-- Name: ix_inspections_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inspections_status ON public.vehicle_inspections USING btree (status);


--
-- Name: ix_inspections_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inspections_type ON public.vehicle_inspections USING btree (inspection_type);


--
-- Name: ix_inspections_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_inspections_vehicle_id ON public.vehicle_inspections USING btree (vehicle_id);


--
-- Name: ix_integrations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_integrations_id ON public.integrations USING btree (id);


--
-- Name: ix_integrations_integration_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_integrations_integration_type ON public.integrations USING btree (integration_type);


--
-- Name: ix_integrations_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_integrations_name ON public.integrations USING btree (name);


--
-- Name: ix_integrations_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_integrations_organization_id ON public.integrations USING btree (organization_id);


--
-- Name: ix_kb_articles_author_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_articles_author_id ON public.kb_articles USING btree (author_id);


--
-- Name: ix_kb_articles_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_articles_category ON public.kb_articles USING btree (category);


--
-- Name: ix_kb_articles_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_articles_organization_id ON public.kb_articles USING btree (organization_id);


--
-- Name: ix_kb_articles_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_kb_articles_slug ON public.kb_articles USING btree (slug);


--
-- Name: ix_kb_articles_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_articles_status ON public.kb_articles USING btree (status);


--
-- Name: ix_kb_articles_title; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_articles_title ON public.kb_articles USING btree (title);


--
-- Name: ix_kb_categories_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_categories_id ON public.kb_categories USING btree (id);


--
-- Name: ix_kb_categories_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_categories_is_active ON public.kb_categories USING btree (is_active);


--
-- Name: ix_kb_categories_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_categories_name ON public.kb_categories USING btree (name);


--
-- Name: ix_kb_categories_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_categories_organization_id ON public.kb_categories USING btree (organization_id);


--
-- Name: ix_kb_categories_parent_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kb_categories_parent_id ON public.kb_categories USING btree (parent_id);


--
-- Name: ix_kpis_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kpis_category ON public.kpis USING btree (category);


--
-- Name: ix_kpis_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kpis_code ON public.kpis USING btree (code);


--
-- Name: ix_kpis_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kpis_id ON public.kpis USING btree (id);


--
-- Name: ix_kpis_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kpis_is_active ON public.kpis USING btree (is_active);


--
-- Name: ix_kpis_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_kpis_organization_id ON public.kpis USING btree (organization_id);


--
-- Name: ix_leaves_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leaves_courier_id ON public.leaves USING btree (courier_id);


--
-- Name: ix_leaves_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leaves_organization_id ON public.leaves USING btree (organization_id);


--
-- Name: ix_leaves_start_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leaves_start_date ON public.leaves USING btree (start_date);


--
-- Name: ix_leaves_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_leaves_status ON public.leaves USING btree (status);


--
-- Name: ix_loans_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loans_courier_id ON public.loans USING btree (courier_id);


--
-- Name: ix_loans_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loans_organization_id ON public.loans USING btree (organization_id);


--
-- Name: ix_loans_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_loans_status ON public.loans USING btree (status);


--
-- Name: ix_maintenance_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_id ON public.vehicle_maintenance USING btree (id);


--
-- Name: ix_maintenance_scheduled_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_scheduled_date ON public.vehicle_maintenance USING btree (scheduled_date);


--
-- Name: ix_maintenance_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_status ON public.vehicle_maintenance USING btree (status);


--
-- Name: ix_maintenance_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_type ON public.vehicle_maintenance USING btree (maintenance_type);


--
-- Name: ix_maintenance_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_maintenance_vehicle_id ON public.vehicle_maintenance USING btree (vehicle_id);


--
-- Name: ix_metric_snapshots_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_snapshots_id ON public.metric_snapshots USING btree (id);


--
-- Name: ix_metric_snapshots_metric_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_snapshots_metric_name ON public.metric_snapshots USING btree (metric_name);


--
-- Name: ix_metric_snapshots_metric_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_snapshots_metric_type ON public.metric_snapshots USING btree (metric_type);


--
-- Name: ix_metric_snapshots_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_snapshots_organization_id ON public.metric_snapshots USING btree (organization_id);


--
-- Name: ix_metric_snapshots_timestamp; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_metric_snapshots_timestamp ON public.metric_snapshots USING btree ("timestamp");


--
-- Name: ix_notification_settings_event_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_settings_event_type ON public.notification_settings USING btree (event_type);


--
-- Name: ix_notification_settings_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_settings_organization_id ON public.notification_settings USING btree (organization_id);


--
-- Name: ix_notification_settings_setting_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_notification_settings_setting_code ON public.notification_settings USING btree (setting_code);


--
-- Name: ix_operations_documents_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_documents_category ON public.operations_documents USING btree (category);


--
-- Name: ix_operations_documents_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_documents_created_at ON public.operations_documents USING btree (created_at);


--
-- Name: ix_operations_documents_doc_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_operations_documents_doc_number ON public.operations_documents USING btree (doc_number);


--
-- Name: ix_operations_documents_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_documents_organization_id ON public.operations_documents USING btree (organization_id);


--
-- Name: ix_operations_settings_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_settings_organization_id ON public.operations_settings USING btree (organization_id);


--
-- Name: ix_operations_settings_setting_group; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_settings_setting_group ON public.operations_settings USING btree (setting_group);


--
-- Name: ix_operations_settings_setting_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_operations_settings_setting_key ON public.operations_settings USING btree (setting_key);


--
-- Name: ix_organization_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organization_users_id ON public.organization_users USING btree (id);


--
-- Name: ix_organization_users_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organization_users_is_active ON public.organization_users USING btree (is_active);


--
-- Name: ix_organization_users_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organization_users_organization_id ON public.organization_users USING btree (organization_id);


--
-- Name: ix_organization_users_role; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organization_users_role ON public.organization_users USING btree (role);


--
-- Name: ix_organization_users_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organization_users_user_id ON public.organization_users USING btree (user_id);


--
-- Name: ix_organizations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_id ON public.organizations USING btree (id);


--
-- Name: ix_organizations_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_is_active ON public.organizations USING btree (is_active);


--
-- Name: ix_organizations_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_organizations_name ON public.organizations USING btree (name);


--
-- Name: ix_organizations_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_organizations_slug ON public.organizations USING btree (slug);


--
-- Name: ix_organizations_subscription_plan; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_subscription_plan ON public.organizations USING btree (subscription_plan);


--
-- Name: ix_organizations_subscription_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_organizations_subscription_status ON public.organizations USING btree (subscription_status);


--
-- Name: ix_password_reset_tokens_expires_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_expires_at ON public.password_reset_tokens USING btree (expires_at);


--
-- Name: ix_password_reset_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_id ON public.password_reset_tokens USING btree (id);


--
-- Name: ix_password_reset_tokens_token_hash; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash ON public.password_reset_tokens USING btree (token_hash);


--
-- Name: ix_password_reset_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_user_id ON public.password_reset_tokens USING btree (user_id);


--
-- Name: ix_password_reset_tokens_user_id_used; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_user_id_used ON public.password_reset_tokens USING btree (user_id, used);


--
-- Name: ix_performance_data_courier_date_range; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_courier_date_range ON public.performance_data USING btree (courier_id, date);


--
-- Name: ix_performance_data_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_courier_id ON public.performance_data USING btree (courier_id);


--
-- Name: ix_performance_data_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_date ON public.performance_data USING btree (date);


--
-- Name: ix_performance_data_efficiency_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_efficiency_score ON public.performance_data USING btree (efficiency_score);


--
-- Name: ix_performance_data_orders_completed; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_orders_completed ON public.performance_data USING btree (orders_completed);


--
-- Name: ix_performance_data_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_organization_id ON public.performance_data USING btree (organization_id);


--
-- Name: ix_performance_data_revenue_generated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_performance_data_revenue_generated ON public.performance_data USING btree (revenue_generated);


--
-- Name: ix_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_id ON public.permissions USING btree (id);


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);


--
-- Name: ix_permissions_resource; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_permissions_resource ON public.permissions USING btree (resource);


--
-- Name: ix_priority_queue_entries_delivery_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_priority_queue_entries_delivery_id ON public.priority_queue_entries USING btree (delivery_id);


--
-- Name: ix_priority_queue_entries_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_id ON public.priority_queue_entries USING btree (id);


--
-- Name: ix_priority_queue_entries_is_escalated; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_is_escalated ON public.priority_queue_entries USING btree (is_escalated);


--
-- Name: ix_priority_queue_entries_is_vip_customer; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_is_vip_customer ON public.priority_queue_entries USING btree (is_vip_customer);


--
-- Name: ix_priority_queue_entries_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_organization_id ON public.priority_queue_entries USING btree (organization_id);


--
-- Name: ix_priority_queue_entries_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_priority ON public.priority_queue_entries USING btree (priority);


--
-- Name: ix_priority_queue_entries_queue_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_priority_queue_entries_queue_number ON public.priority_queue_entries USING btree (queue_number);


--
-- Name: ix_priority_queue_entries_queue_position; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_queue_position ON public.priority_queue_entries USING btree (queue_position);


--
-- Name: ix_priority_queue_entries_queued_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_queued_at ON public.priority_queue_entries USING btree (queued_at);


--
-- Name: ix_priority_queue_entries_required_zone_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_required_zone_id ON public.priority_queue_entries USING btree (required_zone_id);


--
-- Name: ix_priority_queue_entries_sla_deadline; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_sla_deadline ON public.priority_queue_entries USING btree (sla_deadline);


--
-- Name: ix_priority_queue_entries_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_status ON public.priority_queue_entries USING btree (status);


--
-- Name: ix_priority_queue_entries_total_priority_score; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_priority_queue_entries_total_priority_score ON public.priority_queue_entries USING btree (total_priority_score);


--
-- Name: ix_quality_inspections_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_courier_id ON public.quality_inspections USING btree (courier_id);


--
-- Name: ix_quality_inspections_delivery_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_delivery_id ON public.quality_inspections USING btree (delivery_id);


--
-- Name: ix_quality_inspections_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_id ON public.quality_inspections USING btree (id);


--
-- Name: ix_quality_inspections_inspection_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_quality_inspections_inspection_number ON public.quality_inspections USING btree (inspection_number);


--
-- Name: ix_quality_inspections_inspection_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_inspection_type ON public.quality_inspections USING btree (inspection_type);


--
-- Name: ix_quality_inspections_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_organization_id ON public.quality_inspections USING btree (organization_id);


--
-- Name: ix_quality_inspections_scheduled_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_scheduled_date ON public.quality_inspections USING btree (scheduled_date);


--
-- Name: ix_quality_inspections_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_status ON public.quality_inspections USING btree (status);


--
-- Name: ix_quality_inspections_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_inspections_vehicle_id ON public.quality_inspections USING btree (vehicle_id);


--
-- Name: ix_quality_metrics_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_metrics_id ON public.quality_metrics USING btree (id);


--
-- Name: ix_quality_metrics_metric_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_quality_metrics_metric_code ON public.quality_metrics USING btree (metric_code);


--
-- Name: ix_quality_metrics_metric_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_metrics_metric_type ON public.quality_metrics USING btree (metric_type);


--
-- Name: ix_quality_metrics_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_quality_metrics_organization_id ON public.quality_metrics USING btree (organization_id);


--
-- Name: ix_reports_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_id ON public.reports USING btree (id);


--
-- Name: ix_reports_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_name ON public.reports USING btree (name);


--
-- Name: ix_reports_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_organization_id ON public.reports USING btree (organization_id);


--
-- Name: ix_reports_report_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_report_type ON public.reports USING btree (report_type);


--
-- Name: ix_reports_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_reports_status ON public.reports USING btree (status);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- Name: ix_rooms_building_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rooms_building_id ON public.rooms USING btree (building_id);


--
-- Name: ix_rooms_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rooms_organization_id ON public.rooms USING btree (organization_id);


--
-- Name: ix_rooms_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_rooms_status ON public.rooms USING btree (status);


--
-- Name: ix_routes_courier_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_courier_date ON public.routes USING btree (courier_id, date);


--
-- Name: ix_routes_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_courier_id ON public.routes USING btree (courier_id);


--
-- Name: ix_routes_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_date ON public.routes USING btree (date);


--
-- Name: ix_routes_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_organization_id ON public.routes USING btree (organization_id);


--
-- Name: ix_routes_route_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_routes_route_number ON public.routes USING btree (route_number);


--
-- Name: ix_routes_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_status ON public.routes USING btree (status);


--
-- Name: ix_routes_zone_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_routes_zone_id ON public.routes USING btree (zone_id);


--
-- Name: ix_salaries_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_salaries_courier_id ON public.salaries USING btree (courier_id);


--
-- Name: ix_salaries_month_year; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_salaries_month_year ON public.salaries USING btree (month, year);


--
-- Name: ix_salaries_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_salaries_organization_id ON public.salaries USING btree (organization_id);


--
-- Name: ix_sla_definitions_applies_to_zone_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_definitions_applies_to_zone_id ON public.sla_definitions USING btree (applies_to_zone_id);


--
-- Name: ix_sla_definitions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_definitions_id ON public.sla_definitions USING btree (id);


--
-- Name: ix_sla_definitions_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_definitions_organization_id ON public.sla_definitions USING btree (organization_id);


--
-- Name: ix_sla_definitions_sla_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sla_definitions_sla_code ON public.sla_definitions USING btree (sla_code);


--
-- Name: ix_sla_definitions_sla_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_definitions_sla_type ON public.sla_definitions USING btree (sla_type);


--
-- Name: ix_sla_events_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_events_id ON public.sla_events USING btree (id);


--
-- Name: ix_sla_events_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_events_organization_id ON public.sla_events USING btree (organization_id);


--
-- Name: ix_sla_thresholds_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_thresholds_organization_id ON public.sla_thresholds USING btree (organization_id);


--
-- Name: ix_sla_thresholds_service_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_thresholds_service_type ON public.sla_thresholds USING btree (service_type);


--
-- Name: ix_sla_thresholds_sla_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_thresholds_sla_type ON public.sla_thresholds USING btree (sla_type);


--
-- Name: ix_sla_thresholds_threshold_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_thresholds_threshold_code ON public.sla_thresholds USING btree (threshold_code);


--
-- Name: ix_sla_thresholds_zone_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_thresholds_zone_id ON public.sla_thresholds USING btree (zone_id);


--
-- Name: ix_sla_tracking_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_courier_id ON public.sla_tracking USING btree (courier_id);


--
-- Name: ix_sla_tracking_delivery_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_delivery_id ON public.sla_tracking USING btree (delivery_id);


--
-- Name: ix_sla_tracking_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_id ON public.sla_tracking USING btree (id);


--
-- Name: ix_sla_tracking_incident_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_incident_id ON public.sla_tracking USING btree (incident_id);


--
-- Name: ix_sla_tracking_is_breached; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_is_breached ON public.sla_tracking USING btree (is_breached);


--
-- Name: ix_sla_tracking_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_organization_id ON public.sla_tracking USING btree (organization_id);


--
-- Name: ix_sla_tracking_route_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_route_id ON public.sla_tracking USING btree (route_id);


--
-- Name: ix_sla_tracking_sla_definition_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_sla_definition_id ON public.sla_tracking USING btree (sla_definition_id);


--
-- Name: ix_sla_tracking_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_status ON public.sla_tracking USING btree (status);


--
-- Name: ix_sla_tracking_target_completion_time; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_sla_tracking_target_completion_time ON public.sla_tracking USING btree (target_completion_time);


--
-- Name: ix_sla_tracking_tracking_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_sla_tracking_tracking_number ON public.sla_tracking USING btree (tracking_number);


--
-- Name: ix_system_settings_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_settings_category ON public.system_settings USING btree (category);


--
-- Name: ix_system_settings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_settings_id ON public.system_settings USING btree (id);


--
-- Name: ix_system_settings_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_system_settings_key ON public.system_settings USING btree (key);


--
-- Name: ix_system_settings_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_system_settings_organization_id ON public.system_settings USING btree (organization_id);


--
-- Name: ix_ticket_attachments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_attachments_id ON public.ticket_attachments USING btree (id);


--
-- Name: ix_ticket_attachments_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_attachments_organization_id ON public.ticket_attachments USING btree (organization_id);


--
-- Name: ix_ticket_attachments_reply_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_attachments_reply_id ON public.ticket_attachments USING btree (reply_id);


--
-- Name: ix_ticket_attachments_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_attachments_ticket_id ON public.ticket_attachments USING btree (ticket_id);


--
-- Name: ix_ticket_replies_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_replies_organization_id ON public.ticket_replies USING btree (organization_id);


--
-- Name: ix_ticket_replies_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_replies_ticket_id ON public.ticket_replies USING btree (ticket_id);


--
-- Name: ix_ticket_replies_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_replies_user_id ON public.ticket_replies USING btree (user_id);


--
-- Name: ix_ticket_templates_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_templates_id ON public.ticket_templates USING btree (id);


--
-- Name: ix_ticket_templates_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_templates_is_active ON public.ticket_templates USING btree (is_active);


--
-- Name: ix_ticket_templates_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_ticket_templates_organization_id ON public.ticket_templates USING btree (organization_id);


--
-- Name: ix_tickets_assigned_to; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_assigned_to ON public.tickets USING btree (assigned_to);


--
-- Name: ix_tickets_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_category ON public.tickets USING btree (category);


--
-- Name: ix_tickets_category_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_category_status ON public.tickets USING btree (category, status);


--
-- Name: ix_tickets_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_courier_id ON public.tickets USING btree (courier_id);


--
-- Name: ix_tickets_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_created_at ON public.tickets USING btree (created_at);


--
-- Name: ix_tickets_created_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_created_by ON public.tickets USING btree (created_by);


--
-- Name: ix_tickets_department; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_department ON public.tickets USING btree (department);


--
-- Name: ix_tickets_escalation_level; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_escalation_level ON public.tickets USING btree (escalation_level);


--
-- Name: ix_tickets_is_merged; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_is_merged ON public.tickets USING btree (is_merged);


--
-- Name: ix_tickets_merged_into_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_merged_into_id ON public.tickets USING btree (merged_into_id);


--
-- Name: ix_tickets_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_organization_id ON public.tickets USING btree (organization_id);


--
-- Name: ix_tickets_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_priority ON public.tickets USING btree (priority);


--
-- Name: ix_tickets_sla_breached; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_sla_breached ON public.tickets USING btree (sla_breached);


--
-- Name: ix_tickets_sla_due_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_sla_due_at ON public.tickets USING btree (sla_due_at);


--
-- Name: ix_tickets_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_status ON public.tickets USING btree (status);


--
-- Name: ix_tickets_status_priority; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_tickets_status_priority ON public.tickets USING btree (status, priority);


--
-- Name: ix_tickets_ticket_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_tickets_ticket_id ON public.tickets USING btree (ticket_id);


--
-- Name: ix_trigger_executions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trigger_executions_id ON public.trigger_executions USING btree (id);


--
-- Name: ix_trigger_executions_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_trigger_executions_organization_id ON public.trigger_executions USING btree (organization_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_google_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_google_id ON public.users USING btree (google_id);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_vehicle_inspections_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_inspections_organization_id ON public.vehicle_inspections USING btree (organization_id);


--
-- Name: ix_vehicle_logs_courier_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_courier_id ON public.vehicle_logs USING btree (courier_id);


--
-- Name: ix_vehicle_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_id ON public.vehicle_logs USING btree (id);


--
-- Name: ix_vehicle_logs_log_date; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_log_date ON public.vehicle_logs USING btree (log_date);


--
-- Name: ix_vehicle_logs_log_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_log_type ON public.vehicle_logs USING btree (log_type);


--
-- Name: ix_vehicle_logs_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_organization_id ON public.vehicle_logs USING btree (organization_id);


--
-- Name: ix_vehicle_logs_vehicle_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_logs_vehicle_id ON public.vehicle_logs USING btree (vehicle_id);


--
-- Name: ix_vehicle_maintenance_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicle_maintenance_organization_id ON public.vehicle_maintenance USING btree (organization_id);


--
-- Name: ix_vehicles_fms_asset_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_vehicles_fms_asset_id ON public.vehicles USING btree (fms_asset_id);


--
-- Name: ix_vehicles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicles_id ON public.vehicles USING btree (id);


--
-- Name: ix_vehicles_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicles_organization_id ON public.vehicles USING btree (organization_id);


--
-- Name: ix_vehicles_plate_number; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_vehicles_plate_number ON public.vehicles USING btree (plate_number);


--
-- Name: ix_vehicles_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicles_status ON public.vehicles USING btree (status);


--
-- Name: ix_vehicles_vehicle_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_vehicles_vehicle_type ON public.vehicles USING btree (vehicle_type);


--
-- Name: ix_workflow_automations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_automations_id ON public.workflow_automations USING btree (id);


--
-- Name: ix_workflow_automations_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_automations_organization_id ON public.workflow_automations USING btree (organization_id);


--
-- Name: ix_workflow_instances_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_created_at ON public.workflow_instances USING btree (created_at);


--
-- Name: ix_workflow_instances_initiated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_initiated_by ON public.workflow_instances USING btree (initiated_by);


--
-- Name: ix_workflow_instances_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_organization_id ON public.workflow_instances USING btree (organization_id);


--
-- Name: ix_workflow_instances_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_status ON public.workflow_instances USING btree (status);


--
-- Name: ix_workflow_instances_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_instances_template_id ON public.workflow_instances USING btree (template_id);


--
-- Name: ix_workflow_metrics_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_metrics_id ON public.workflow_metrics USING btree (id);


--
-- Name: ix_workflow_metrics_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_metrics_organization_id ON public.workflow_metrics USING btree (organization_id);


--
-- Name: ix_workflow_performance_snapshots_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_performance_snapshots_id ON public.workflow_performance_snapshots USING btree (id);


--
-- Name: ix_workflow_performance_snapshots_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_performance_snapshots_organization_id ON public.workflow_performance_snapshots USING btree (organization_id);


--
-- Name: ix_workflow_sla_instances_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_sla_instances_id ON public.workflow_sla_instances USING btree (id);


--
-- Name: ix_workflow_sla_instances_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_sla_instances_organization_id ON public.workflow_sla_instances USING btree (organization_id);


--
-- Name: ix_workflow_slas_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_slas_id ON public.workflow_slas USING btree (id);


--
-- Name: ix_workflow_slas_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_slas_organization_id ON public.workflow_slas USING btree (organization_id);


--
-- Name: ix_workflow_step_metrics_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_step_metrics_id ON public.workflow_step_metrics USING btree (id);


--
-- Name: ix_workflow_step_metrics_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_step_metrics_organization_id ON public.workflow_step_metrics USING btree (organization_id);


--
-- Name: ix_workflow_templates_category; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_templates_category ON public.workflow_templates USING btree (category);


--
-- Name: ix_workflow_templates_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_templates_is_active ON public.workflow_templates USING btree (is_active);


--
-- Name: ix_workflow_templates_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_templates_name ON public.workflow_templates USING btree (name);


--
-- Name: ix_workflow_templates_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_templates_organization_id ON public.workflow_templates USING btree (organization_id);


--
-- Name: ix_workflow_triggers_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_triggers_id ON public.workflow_triggers USING btree (id);


--
-- Name: ix_workflow_triggers_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_triggers_organization_id ON public.workflow_triggers USING btree (organization_id);


--
-- Name: ix_workflow_user_metrics_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_user_metrics_id ON public.workflow_user_metrics USING btree (id);


--
-- Name: ix_workflow_user_metrics_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_workflow_user_metrics_organization_id ON public.workflow_user_metrics USING btree (organization_id);


--
-- Name: ix_zone_defaults_default_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zone_defaults_default_code ON public.zone_defaults USING btree (default_code);


--
-- Name: ix_zone_defaults_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zone_defaults_organization_id ON public.zone_defaults USING btree (organization_id);


--
-- Name: ix_zones_city; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zones_city ON public.zones USING btree (city);


--
-- Name: ix_zones_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zones_id ON public.zones USING btree (id);


--
-- Name: ix_zones_organization_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zones_organization_id ON public.zones USING btree (organization_id);


--
-- Name: ix_zones_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zones_status ON public.zones USING btree (status);


--
-- Name: ix_zones_zone_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_zones_zone_code ON public.zones USING btree (zone_code);


--
-- Name: ix_zones_zone_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_zones_zone_name ON public.zones USING btree (zone_name);


--
-- Name: couriers audit_couriers; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER audit_couriers AFTER INSERT OR DELETE OR UPDATE ON barq.couriers FOR EACH ROW EXECUTE FUNCTION barq.audit_trigger_function();


--
-- Name: vehicles audit_vehicles; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER audit_vehicles AFTER INSERT OR DELETE OR UPDATE ON barq.vehicles FOR EACH ROW EXECUTE FUNCTION barq.audit_trigger_vehicles();


--
-- Name: couriers update_couriers_updated_at; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER update_couriers_updated_at BEFORE UPDATE ON barq.couriers FOR EACH ROW EXECUTE FUNCTION barq.update_updated_at_and_version();


--
-- Name: leave_requests update_leave_requests_updated_at; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER update_leave_requests_updated_at BEFORE UPDATE ON barq.leave_requests FOR EACH ROW EXECUTE FUNCTION barq.update_updated_at_column();


--
-- Name: vehicles update_vehicles_updated_at; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON barq.vehicles FOR EACH ROW EXECUTE FUNCTION barq.update_updated_at_and_version();


--
-- Name: workflow_instances update_workflow_instances_updated_at; Type: TRIGGER; Schema: barq; Owner: ramiz_new
--

CREATE TRIGGER update_workflow_instances_updated_at BEFORE UPDATE ON barq.workflow_instances FOR EACH ROW EXECUTE FUNCTION barq.update_updated_at_column();


--
-- Name: couriers fk_barq_couriers_public_couriers; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.couriers
    ADD CONSTRAINT fk_barq_couriers_public_couriers FOREIGN KEY (barq_id) REFERENCES public.couriers(barq_id) ON DELETE CASCADE;


--
-- Name: vehicles fk_barq_vehicles_public_vehicles; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicles
    ADD CONSTRAINT fk_barq_vehicles_public_vehicles FOREIGN KEY (plate_number) REFERENCES public.vehicles(plate_number) ON DELETE CASCADE;


--
-- Name: leave_approvals leave_approvals_request_id_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.leave_approvals
    ADD CONSTRAINT leave_approvals_request_id_fkey FOREIGN KEY (request_id) REFERENCES barq.leave_requests(request_id) ON DELETE CASCADE;


--
-- Name: leave_requests leave_requests_courier_id_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.leave_requests
    ADD CONSTRAINT leave_requests_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES barq.couriers(barq_id) ON DELETE CASCADE;


--
-- Name: leave_requests leave_requests_manager_id_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.leave_requests
    ADD CONSTRAINT leave_requests_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES barq.couriers(barq_id);


--
-- Name: vehicle_assignments vehicle_assignments_courier_id_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicle_assignments
    ADD CONSTRAINT vehicle_assignments_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES barq.couriers(barq_id) ON DELETE CASCADE;


--
-- Name: vehicle_assignments vehicle_assignments_vehicle_plate_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicle_assignments
    ADD CONSTRAINT vehicle_assignments_vehicle_plate_fkey FOREIGN KEY (vehicle_plate) REFERENCES barq.vehicles(plate_number) ON DELETE CASCADE;


--
-- Name: vehicles vehicles_assigned_to_fkey; Type: FK CONSTRAINT; Schema: barq; Owner: ramiz_new
--

ALTER TABLE ONLY barq.vehicles
    ADD CONSTRAINT vehicles_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES barq.couriers(barq_id) ON DELETE SET NULL;


--
-- Name: accident_logs accident_logs_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accident_logs
    ADD CONSTRAINT accident_logs_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: accident_logs accident_logs_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accident_logs
    ADD CONSTRAINT accident_logs_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: allocations allocations_bed_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allocations
    ADD CONSTRAINT allocations_bed_id_fkey FOREIGN KEY (bed_id) REFERENCES public.beds(id) ON DELETE CASCADE;


--
-- Name: allocations allocations_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allocations
    ADD CONSTRAINT allocations_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: api_keys api_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: approval_chain_approvers approval_chain_approvers_approval_chain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers
    ADD CONSTRAINT approval_chain_approvers_approval_chain_id_fkey FOREIGN KEY (approval_chain_id) REFERENCES public.approval_chains(id);


--
-- Name: approval_chain_approvers approval_chain_approvers_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers
    ADD CONSTRAINT approval_chain_approvers_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: approval_chain_approvers approval_chain_approvers_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers
    ADD CONSTRAINT approval_chain_approvers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: approval_chains approval_chains_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chains
    ADD CONSTRAINT approval_chains_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: approval_requests approval_requests_approval_chain_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_approval_chain_id_fkey FOREIGN KEY (approval_chain_id) REFERENCES public.approval_chains(id);


--
-- Name: approval_requests approval_requests_approver_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_approver_id_fkey FOREIGN KEY (approver_id) REFERENCES public.users(id);


--
-- Name: approval_requests approval_requests_delegated_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_delegated_to_id_fkey FOREIGN KEY (delegated_to_id) REFERENCES public.users(id);


--
-- Name: approval_requests approval_requests_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT approval_requests_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES public.workflow_instances(id);


--
-- Name: assets assets_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: attendance attendance_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT attendance_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: automation_execution_logs automation_execution_logs_automation_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_execution_logs
    ADD CONSTRAINT automation_execution_logs_automation_id_fkey FOREIGN KEY (automation_id) REFERENCES public.workflow_automations(id);


--
-- Name: automation_execution_logs automation_execution_logs_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_execution_logs
    ADD CONSTRAINT automation_execution_logs_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES public.workflow_instances(id);


--
-- Name: backups backups_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT backups_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: backups backups_last_restored_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT backups_last_restored_by_id_fkey FOREIGN KEY (last_restored_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: beds beds_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT beds_room_id_fkey FOREIGN KEY (room_id) REFERENCES public.rooms(id) ON DELETE CASCADE;


--
-- Name: bonuses bonuses_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bonuses
    ADD CONSTRAINT bonuses_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id);


--
-- Name: bonuses bonuses_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bonuses
    ADD CONSTRAINT bonuses_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: canned_responses canned_responses_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canned_responses
    ADD CONSTRAINT canned_responses_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: chat_messages chat_messages_sender_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_sender_id_fkey FOREIGN KEY (sender_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: chat_messages chat_messages_session_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT chat_messages_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.chat_sessions(id) ON DELETE CASCADE;


--
-- Name: chat_sessions chat_sessions_agent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_agent_id_fkey FOREIGN KEY (agent_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: chat_sessions chat_sessions_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT chat_sessions_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: cod_transactions cod_transactions_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cod_transactions
    ADD CONSTRAINT cod_transactions_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: cod_transactions cod_transactions_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cod_transactions
    ADD CONSTRAINT cod_transactions_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: courier_vehicle_assignments courier_vehicle_assignments_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courier_vehicle_assignments
    ADD CONSTRAINT courier_vehicle_assignments_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: courier_vehicle_assignments courier_vehicle_assignments_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courier_vehicle_assignments
    ADD CONSTRAINT courier_vehicle_assignments_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: couriers couriers_accommodation_building_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers
    ADD CONSTRAINT couriers_accommodation_building_id_fkey FOREIGN KEY (accommodation_building_id) REFERENCES public.buildings(id) ON DELETE SET NULL;


--
-- Name: couriers couriers_accommodation_room_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers
    ADD CONSTRAINT couriers_accommodation_room_id_fkey FOREIGN KEY (accommodation_room_id) REFERENCES public.rooms(id) ON DELETE SET NULL;


--
-- Name: couriers couriers_current_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers
    ADD CONSTRAINT couriers_current_vehicle_id_fkey FOREIGN KEY (current_vehicle_id) REFERENCES public.vehicles(id) ON DELETE SET NULL;


--
-- Name: customer_feedbacks customer_feedbacks_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: customer_feedbacks customer_feedbacks_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: customer_feedbacks customer_feedbacks_escalated_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_escalated_to_id_fkey FOREIGN KEY (escalated_to_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: customer_feedbacks customer_feedbacks_resolved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_resolved_by_id_fkey FOREIGN KEY (resolved_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: customer_feedbacks customer_feedbacks_responded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT customer_feedbacks_responded_by_id_fkey FOREIGN KEY (responded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: dashboards dashboards_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT dashboards_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: deliveries deliveries_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT deliveries_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: dispatch_assignments dispatch_assignments_assigned_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_assigned_by_id_fkey FOREIGN KEY (assigned_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: dispatch_assignments dispatch_assignments_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: dispatch_assignments dispatch_assignments_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: dispatch_assignments dispatch_assignments_previous_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_previous_courier_id_fkey FOREIGN KEY (previous_courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: dispatch_assignments dispatch_assignments_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT dispatch_assignments_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(id) ON DELETE SET NULL;


--
-- Name: dispatch_rules dispatch_rules_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_rules
    ADD CONSTRAINT dispatch_rules_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: dispatch_rules dispatch_rules_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_rules
    ADD CONSTRAINT dispatch_rules_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: feedback_templates feedback_templates_created_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_templates
    ADD CONSTRAINT feedback_templates_created_by_id_fkey FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: feedbacks feedbacks_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: feedbacks feedbacks_responded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_responded_by_fkey FOREIGN KEY (responded_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: feedbacks feedbacks_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedbacks
    ADD CONSTRAINT feedbacks_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: accident_logs fk_accident_logs_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.accident_logs
    ADD CONSTRAINT fk_accident_logs_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: allocations fk_allocations_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.allocations
    ADD CONSTRAINT fk_allocations_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: api_keys fk_api_keys_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT fk_api_keys_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: approval_chain_approvers fk_approval_chain_approvers_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chain_approvers
    ADD CONSTRAINT fk_approval_chain_approvers_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: approval_chains fk_approval_chains_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_chains
    ADD CONSTRAINT fk_approval_chains_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: approval_requests fk_approval_requests_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.approval_requests
    ADD CONSTRAINT fk_approval_requests_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: assets fk_assets_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT fk_assets_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: assignments fk_assignments_assigned_by; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT fk_assignments_assigned_by FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: assignments fk_assignments_courier; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT fk_assignments_courier FOREIGN KEY (courier_id) REFERENCES public.couriers(id);


--
-- Name: assignments fk_assignments_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT fk_assignments_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: assignments fk_assignments_terminated_by; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT fk_assignments_terminated_by FOREIGN KEY (terminated_by) REFERENCES public.users(id);


--
-- Name: assignments fk_assignments_vehicle; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.assignments
    ADD CONSTRAINT fk_assignments_vehicle FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: attendance fk_attendance_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attendance
    ADD CONSTRAINT fk_attendance_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: automation_execution_logs fk_automation_execution_logs_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.automation_execution_logs
    ADD CONSTRAINT fk_automation_execution_logs_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: backups fk_backups_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.backups
    ADD CONSTRAINT fk_backups_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: beds fk_beds_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.beds
    ADD CONSTRAINT fk_beds_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: bonuses fk_bonuses_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.bonuses
    ADD CONSTRAINT fk_bonuses_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: buildings fk_buildings_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.buildings
    ADD CONSTRAINT fk_buildings_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: canned_responses fk_canned_responses_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.canned_responses
    ADD CONSTRAINT fk_canned_responses_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: chat_messages fk_chat_messages_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT fk_chat_messages_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: chat_sessions fk_chat_sessions_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_sessions
    ADD CONSTRAINT fk_chat_sessions_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: courier_vehicle_assignments fk_courier_vehicle_assignments_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.courier_vehicle_assignments
    ADD CONSTRAINT fk_courier_vehicle_assignments_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: couriers fk_couriers_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.couriers
    ADD CONSTRAINT fk_couriers_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: customer_feedbacks fk_customer_feedbacks_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_feedbacks
    ADD CONSTRAINT fk_customer_feedbacks_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: dashboards fk_dashboards_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dashboards
    ADD CONSTRAINT fk_dashboards_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: deliveries fk_deliveries_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.deliveries
    ADD CONSTRAINT fk_deliveries_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: dispatch_assignments fk_dispatch_assignments_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dispatch_assignments
    ADD CONSTRAINT fk_dispatch_assignments_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: documents fk_documents_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.documents
    ADD CONSTRAINT fk_documents_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: driver_orders fk_driver_orders_courier; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.driver_orders
    ADD CONSTRAINT fk_driver_orders_courier FOREIGN KEY (courier_id) REFERENCES public.couriers(id);


--
-- Name: driver_orders fk_driver_orders_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.driver_orders
    ADD CONSTRAINT fk_driver_orders_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: faqs fk_faqs_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.faqs
    ADD CONSTRAINT fk_faqs_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: feedback_templates fk_feedback_templates_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.feedback_templates
    ADD CONSTRAINT fk_feedback_templates_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: fuel_logs fk_fuel_logs_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_logs
    ADD CONSTRAINT fk_fuel_logs_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: handovers fk_handovers_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT fk_handovers_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: incidents fk_incidents_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: integrations fk_integrations_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.integrations
    ADD CONSTRAINT fk_integrations_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: kb_articles fk_kb_articles_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_articles
    ADD CONSTRAINT fk_kb_articles_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: kb_categories fk_kb_categories_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_categories
    ADD CONSTRAINT fk_kb_categories_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: kpis fk_kpis_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kpis
    ADD CONSTRAINT fk_kpis_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: leaves fk_leaves_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT fk_leaves_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: loans fk_loans_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT fk_loans_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: metric_snapshots fk_metric_snapshots_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_snapshots
    ADD CONSTRAINT fk_metric_snapshots_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: operations_documents fk_operations_documents_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_documents
    ADD CONSTRAINT fk_operations_documents_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: orders fk_orders_courier; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_courier FOREIGN KEY (courier_id) REFERENCES public.couriers(id);


--
-- Name: orders fk_orders_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: orders fk_orders_user; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_user FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: orders fk_orders_vehicle; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_vehicle FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: performance_data fk_performance_data_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_data
    ADD CONSTRAINT fk_performance_data_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: priority_queue_entries fk_priority_queue_entries_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT fk_priority_queue_entries_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: quality_inspections fk_quality_inspections_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT fk_quality_inspections_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: quality_metrics fk_quality_metrics_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_metrics
    ADD CONSTRAINT fk_quality_metrics_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: reports fk_reports_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT fk_reports_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: rooms fk_rooms_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT fk_rooms_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: routes fk_routes_assigned_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT fk_routes_assigned_by FOREIGN KEY (assigned_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: routes fk_routes_created_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT fk_routes_created_by FOREIGN KEY (created_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: routes fk_routes_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT fk_routes_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: routes fk_routes_zone_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT fk_routes_zone_id FOREIGN KEY (zone_id) REFERENCES public.zones(id) ON DELETE SET NULL;


--
-- Name: salaries fk_salaries_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries
    ADD CONSTRAINT fk_salaries_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sla_definitions fk_sla_definitions_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_definitions
    ADD CONSTRAINT fk_sla_definitions_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sla_events fk_sla_events_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_events
    ADD CONSTRAINT fk_sla_events_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sla_tracking fk_sla_tracking_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT fk_sla_tracking_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sub_projects fk_sub_projects_created_by; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects
    ADD CONSTRAINT fk_sub_projects_created_by FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: sub_projects fk_sub_projects_manager; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects
    ADD CONSTRAINT fk_sub_projects_manager FOREIGN KEY (manager_id) REFERENCES public.users(id);


--
-- Name: sub_projects fk_sub_projects_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.sub_projects
    ADD CONSTRAINT fk_sub_projects_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: system_settings fk_system_settings_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.system_settings
    ADD CONSTRAINT fk_system_settings_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: tasks fk_tasks_assigned_by; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_assigned_by FOREIGN KEY (assigned_by) REFERENCES public.users(id);


--
-- Name: tasks fk_tasks_assigned_to; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_assigned_to FOREIGN KEY (assigned_to) REFERENCES public.users(id);


--
-- Name: tasks fk_tasks_courier; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_courier FOREIGN KEY (courier_id) REFERENCES public.couriers(id);


--
-- Name: tasks fk_tasks_created_by; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_created_by FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: tasks fk_tasks_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: tasks fk_tasks_vehicle; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.tasks
    ADD CONSTRAINT fk_tasks_vehicle FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id);


--
-- Name: ticket_attachments fk_ticket_attachments_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT fk_ticket_attachments_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: ticket_replies fk_ticket_replies_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_replies
    ADD CONSTRAINT fk_ticket_replies_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: ticket_templates fk_ticket_templates_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_templates
    ADD CONSTRAINT fk_ticket_templates_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: tickets fk_tickets_escalated_by; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT fk_tickets_escalated_by FOREIGN KEY (escalated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tickets fk_tickets_merged_into; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT fk_tickets_merged_into FOREIGN KEY (merged_into_id) REFERENCES public.tickets(id) ON DELETE SET NULL;


--
-- Name: tickets fk_tickets_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT fk_tickets_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: tickets fk_tickets_template; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT fk_tickets_template FOREIGN KEY (template_id) REFERENCES public.ticket_templates(id) ON DELETE SET NULL;


--
-- Name: trigger_executions fk_trigger_executions_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trigger_executions
    ADD CONSTRAINT fk_trigger_executions_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: vehicle_data fk_vehicle_data_courier; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.vehicle_data
    ADD CONSTRAINT fk_vehicle_data_courier FOREIGN KEY (courier_id) REFERENCES public.couriers(id);


--
-- Name: vehicle_data fk_vehicle_data_organization; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.vehicle_data
    ADD CONSTRAINT fk_vehicle_data_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id);


--
-- Name: vehicle_data fk_vehicle_data_vehicle; Type: FK CONSTRAINT; Schema: public; Owner: ramiz_new
--

ALTER TABLE ONLY public.vehicle_data
    ADD CONSTRAINT fk_vehicle_data_vehicle FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicle_inspections fk_vehicle_inspections_organization; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT fk_vehicle_inspections_organization FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: vehicle_logs fk_vehicle_logs_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_logs
    ADD CONSTRAINT fk_vehicle_logs_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: vehicle_maintenance fk_vehicle_maintenance_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_maintenance
    ADD CONSTRAINT fk_vehicle_maintenance_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: vehicles fk_vehicles_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicles
    ADD CONSTRAINT fk_vehicles_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_automations fk_workflow_automations_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT fk_workflow_automations_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_instances fk_workflow_instances_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT fk_workflow_instances_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_metrics fk_workflow_metrics_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_metrics
    ADD CONSTRAINT fk_workflow_metrics_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_performance_snapshots fk_workflow_performance_snapshots_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_performance_snapshots
    ADD CONSTRAINT fk_workflow_performance_snapshots_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_sla_instances fk_workflow_sla_instances_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_sla_instances
    ADD CONSTRAINT fk_workflow_sla_instances_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_slas fk_workflow_slas_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_slas
    ADD CONSTRAINT fk_workflow_slas_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_step_metrics fk_workflow_step_metrics_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_step_metrics
    ADD CONSTRAINT fk_workflow_step_metrics_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_templates fk_workflow_templates_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_templates
    ADD CONSTRAINT fk_workflow_templates_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_triggers fk_workflow_triggers_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_triggers
    ADD CONSTRAINT fk_workflow_triggers_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: workflow_user_metrics fk_workflow_user_metrics_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_user_metrics
    ADD CONSTRAINT fk_workflow_user_metrics_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: zones fk_zones_organization_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zones
    ADD CONSTRAINT fk_zones_organization_id FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: fuel_logs fuel_logs_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_logs
    ADD CONSTRAINT fuel_logs_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: fuel_logs fuel_logs_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.fuel_logs
    ADD CONSTRAINT fuel_logs_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: handovers handovers_approved_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_approved_by_id_fkey FOREIGN KEY (approved_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: handovers handovers_from_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_from_courier_id_fkey FOREIGN KEY (from_courier_id) REFERENCES public.couriers(id) ON DELETE RESTRICT;


--
-- Name: handovers handovers_to_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_to_courier_id_fkey FOREIGN KEY (to_courier_id) REFERENCES public.couriers(id) ON DELETE RESTRICT;


--
-- Name: handovers handovers_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE RESTRICT;


--
-- Name: handovers handovers_witness_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.handovers
    ADD CONSTRAINT handovers_witness_id_fkey FOREIGN KEY (witness_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: incidents incidents_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: incidents incidents_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT incidents_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE SET NULL;


--
-- Name: kb_articles kb_articles_author_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_articles
    ADD CONSTRAINT kb_articles_author_id_fkey FOREIGN KEY (author_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: kb_categories kb_categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.kb_categories
    ADD CONSTRAINT kb_categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.kb_categories(id) ON DELETE CASCADE;


--
-- Name: leaves leaves_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT leaves_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: leaves leaves_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leaves
    ADD CONSTRAINT leaves_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: loans loans_approved_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_approved_by_fkey FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: loans loans_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.loans
    ADD CONSTRAINT loans_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE RESTRICT;


--
-- Name: notification_settings notification_settings_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification_settings
    ADD CONSTRAINT notification_settings_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: operations_documents operations_documents_uploaded_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_documents
    ADD CONSTRAINT operations_documents_uploaded_by_id_fkey FOREIGN KEY (uploaded_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: operations_settings operations_settings_last_modified_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_settings
    ADD CONSTRAINT operations_settings_last_modified_by_id_fkey FOREIGN KEY (last_modified_by_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: operations_settings operations_settings_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.operations_settings
    ADD CONSTRAINT operations_settings_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: organization_users organization_users_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_users
    ADD CONSTRAINT organization_users_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: organization_users organization_users_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organization_users
    ADD CONSTRAINT organization_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: password_reset_tokens password_reset_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: performance_data performance_data_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.performance_data
    ADD CONSTRAINT performance_data_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: priority_queue_entries priority_queue_entries_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT priority_queue_entries_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: priority_queue_entries priority_queue_entries_escalated_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT priority_queue_entries_escalated_to_id_fkey FOREIGN KEY (escalated_to_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: priority_queue_entries priority_queue_entries_preferred_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT priority_queue_entries_preferred_courier_id_fkey FOREIGN KEY (preferred_courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: priority_queue_entries priority_queue_entries_required_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.priority_queue_entries
    ADD CONSTRAINT priority_queue_entries_required_zone_id_fkey FOREIGN KEY (required_zone_id) REFERENCES public.zones(id) ON DELETE SET NULL;


--
-- Name: quality_inspections quality_inspections_completion_verified_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_completion_verified_by_fkey FOREIGN KEY (completion_verified_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: quality_inspections quality_inspections_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: quality_inspections quality_inspections_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: quality_inspections quality_inspections_inspector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_inspector_id_fkey FOREIGN KEY (inspector_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: quality_inspections quality_inspections_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.quality_inspections
    ADD CONSTRAINT quality_inspections_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: reports reports_generated_by_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.reports
    ADD CONSTRAINT reports_generated_by_user_id_fkey FOREIGN KEY (generated_by_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: rooms rooms_building_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.rooms
    ADD CONSTRAINT rooms_building_id_fkey FOREIGN KEY (building_id) REFERENCES public.buildings(id) ON DELETE CASCADE;


--
-- Name: routes routes_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: salaries salaries_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.salaries
    ADD CONSTRAINT salaries_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE RESTRICT;


--
-- Name: sla_definitions sla_definitions_applies_to_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_definitions
    ADD CONSTRAINT sla_definitions_applies_to_zone_id_fkey FOREIGN KEY (applies_to_zone_id) REFERENCES public.zones(id) ON DELETE CASCADE;


--
-- Name: sla_events sla_events_sla_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_events
    ADD CONSTRAINT sla_events_sla_instance_id_fkey FOREIGN KEY (sla_instance_id) REFERENCES public.workflow_sla_instances(id);


--
-- Name: sla_events sla_events_triggered_by_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_events
    ADD CONSTRAINT sla_events_triggered_by_id_fkey FOREIGN KEY (triggered_by_id) REFERENCES public.users(id);


--
-- Name: sla_thresholds sla_thresholds_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_thresholds
    ADD CONSTRAINT sla_thresholds_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: sla_thresholds sla_thresholds_zone_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_thresholds
    ADD CONSTRAINT sla_thresholds_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES public.zones(id) ON DELETE CASCADE;


--
-- Name: sla_tracking sla_tracking_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: sla_tracking sla_tracking_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_delivery_id_fkey FOREIGN KEY (delivery_id) REFERENCES public.deliveries(id) ON DELETE CASCADE;


--
-- Name: sla_tracking sla_tracking_escalated_to_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_escalated_to_id_fkey FOREIGN KEY (escalated_to_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: sla_tracking sla_tracking_incident_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_incident_id_fkey FOREIGN KEY (incident_id) REFERENCES public.incidents(id) ON DELETE CASCADE;


--
-- Name: sla_tracking sla_tracking_route_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_route_id_fkey FOREIGN KEY (route_id) REFERENCES public.routes(id) ON DELETE CASCADE;


--
-- Name: sla_tracking sla_tracking_sla_definition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sla_tracking
    ADD CONSTRAINT sla_tracking_sla_definition_id_fkey FOREIGN KEY (sla_definition_id) REFERENCES public.sla_definitions(id) ON DELETE CASCADE;


--
-- Name: ticket_attachments ticket_attachments_reply_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_reply_id_fkey FOREIGN KEY (reply_id) REFERENCES public.ticket_replies(id) ON DELETE CASCADE;


--
-- Name: ticket_attachments ticket_attachments_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(id) ON DELETE CASCADE;


--
-- Name: ticket_attachments ticket_attachments_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_attachments
    ADD CONSTRAINT ticket_attachments_uploaded_by_fkey FOREIGN KEY (uploaded_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: ticket_replies ticket_replies_ticket_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_replies
    ADD CONSTRAINT ticket_replies_ticket_id_fkey FOREIGN KEY (ticket_id) REFERENCES public.tickets(id) ON DELETE CASCADE;


--
-- Name: ticket_replies ticket_replies_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_replies
    ADD CONSTRAINT ticket_replies_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: ticket_templates ticket_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.ticket_templates
    ADD CONSTRAINT ticket_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tickets tickets_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: tickets tickets_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE CASCADE;


--
-- Name: tickets tickets_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tickets
    ADD CONSTRAINT tickets_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: trigger_executions trigger_executions_trigger_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trigger_executions
    ADD CONSTRAINT trigger_executions_trigger_id_fkey FOREIGN KEY (trigger_id) REFERENCES public.workflow_triggers(id);


--
-- Name: trigger_executions trigger_executions_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trigger_executions
    ADD CONSTRAINT trigger_executions_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES public.workflow_instances(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: vehicle_inspections vehicle_inspections_inspector_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT vehicle_inspections_inspector_id_fkey FOREIGN KEY (inspector_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: vehicle_inspections vehicle_inspections_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_inspections
    ADD CONSTRAINT vehicle_inspections_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicle_logs vehicle_logs_courier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_logs
    ADD CONSTRAINT vehicle_logs_courier_id_fkey FOREIGN KEY (courier_id) REFERENCES public.couriers(id) ON DELETE SET NULL;


--
-- Name: vehicle_logs vehicle_logs_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_logs
    ADD CONSTRAINT vehicle_logs_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: vehicle_maintenance vehicle_maintenance_vehicle_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.vehicle_maintenance
    ADD CONSTRAINT vehicle_maintenance_vehicle_id_fkey FOREIGN KEY (vehicle_id) REFERENCES public.vehicles(id) ON DELETE CASCADE;


--
-- Name: workflow_automations workflow_automations_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_automations
    ADD CONSTRAINT workflow_automations_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_instances workflow_instances_initiated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_initiated_by_fkey FOREIGN KEY (initiated_by) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: workflow_instances workflow_instances_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_instances
    ADD CONSTRAINT workflow_instances_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.workflow_templates(id) ON DELETE CASCADE;


--
-- Name: workflow_metrics workflow_metrics_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_metrics
    ADD CONSTRAINT workflow_metrics_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_performance_snapshots workflow_performance_snapshots_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_performance_snapshots
    ADD CONSTRAINT workflow_performance_snapshots_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_sla_instances workflow_sla_instances_sla_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_sla_instances
    ADD CONSTRAINT workflow_sla_instances_sla_id_fkey FOREIGN KEY (sla_id) REFERENCES public.workflow_slas(id);


--
-- Name: workflow_sla_instances workflow_sla_instances_workflow_instance_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_sla_instances
    ADD CONSTRAINT workflow_sla_instances_workflow_instance_id_fkey FOREIGN KEY (workflow_instance_id) REFERENCES public.workflow_instances(id);


--
-- Name: workflow_slas workflow_slas_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_slas
    ADD CONSTRAINT workflow_slas_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_step_metrics workflow_step_metrics_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_step_metrics
    ADD CONSTRAINT workflow_step_metrics_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_triggers workflow_triggers_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_triggers
    ADD CONSTRAINT workflow_triggers_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: workflow_user_metrics workflow_user_metrics_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_user_metrics
    ADD CONSTRAINT workflow_user_metrics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: workflow_user_metrics workflow_user_metrics_workflow_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.workflow_user_metrics
    ADD CONSTRAINT workflow_user_metrics_workflow_template_id_fkey FOREIGN KEY (workflow_template_id) REFERENCES public.workflow_templates(id);


--
-- Name: zone_defaults zone_defaults_organization_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.zone_defaults
    ADD CONSTRAINT zone_defaults_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id) ON DELETE CASCADE;


--
-- Name: accident_logs; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.accident_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: allocations; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.allocations ENABLE ROW LEVEL SECURITY;

--
-- Name: api_keys; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.api_keys ENABLE ROW LEVEL SECURITY;

--
-- Name: approval_chain_approvers; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.approval_chain_approvers ENABLE ROW LEVEL SECURITY;

--
-- Name: approval_chains; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.approval_chains ENABLE ROW LEVEL SECURITY;

--
-- Name: approval_requests; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.approval_requests ENABLE ROW LEVEL SECURITY;

--
-- Name: assets; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.assets ENABLE ROW LEVEL SECURITY;

--
-- Name: attendance; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.attendance ENABLE ROW LEVEL SECURITY;

--
-- Name: automation_execution_logs; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.automation_execution_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: backups; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.backups ENABLE ROW LEVEL SECURITY;

--
-- Name: beds; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.beds ENABLE ROW LEVEL SECURITY;

--
-- Name: bonuses; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.bonuses ENABLE ROW LEVEL SECURITY;

--
-- Name: buildings; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.buildings ENABLE ROW LEVEL SECURITY;

--
-- Name: canned_responses; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.canned_responses ENABLE ROW LEVEL SECURITY;

--
-- Name: chat_messages; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;

--
-- Name: chat_sessions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;

--
-- Name: courier_vehicle_assignments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.courier_vehicle_assignments ENABLE ROW LEVEL SECURITY;

--
-- Name: couriers; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.couriers ENABLE ROW LEVEL SECURITY;

--
-- Name: dashboards; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.dashboards ENABLE ROW LEVEL SECURITY;

--
-- Name: deliveries; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.deliveries ENABLE ROW LEVEL SECURITY;

--
-- Name: dispatch_assignments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.dispatch_assignments ENABLE ROW LEVEL SECURITY;

--
-- Name: documents; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

--
-- Name: faqs; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.faqs ENABLE ROW LEVEL SECURITY;

--
-- Name: feedback_templates; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.feedback_templates ENABLE ROW LEVEL SECURITY;

--
-- Name: fuel_logs; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.fuel_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: handovers; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.handovers ENABLE ROW LEVEL SECURITY;

--
-- Name: incidents; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;

--
-- Name: integrations; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.integrations ENABLE ROW LEVEL SECURITY;

--
-- Name: kb_articles; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.kb_articles ENABLE ROW LEVEL SECURITY;

--
-- Name: kb_categories; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.kb_categories ENABLE ROW LEVEL SECURITY;

--
-- Name: kpis; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.kpis ENABLE ROW LEVEL SECURITY;

--
-- Name: leaves; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.leaves ENABLE ROW LEVEL SECURITY;

--
-- Name: loans; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.loans ENABLE ROW LEVEL SECURITY;

--
-- Name: metric_snapshots; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.metric_snapshots ENABLE ROW LEVEL SECURITY;

--
-- Name: operations_documents; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.operations_documents ENABLE ROW LEVEL SECURITY;

--
-- Name: performance_data; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.performance_data ENABLE ROW LEVEL SECURITY;

--
-- Name: priority_queue_entries; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.priority_queue_entries ENABLE ROW LEVEL SECURITY;

--
-- Name: quality_inspections; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.quality_inspections ENABLE ROW LEVEL SECURITY;

--
-- Name: quality_metrics; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.quality_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: reports; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

--
-- Name: rooms; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.rooms ENABLE ROW LEVEL SECURITY;

--
-- Name: routes; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.routes ENABLE ROW LEVEL SECURITY;

--
-- Name: salaries; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.salaries ENABLE ROW LEVEL SECURITY;

--
-- Name: sla_definitions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sla_definitions ENABLE ROW LEVEL SECURITY;

--
-- Name: sla_events; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sla_events ENABLE ROW LEVEL SECURITY;

--
-- Name: sla_tracking; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.sla_tracking ENABLE ROW LEVEL SECURITY;

--
-- Name: accident_logs superuser_bypass_accident_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_accident_logs ON public.accident_logs USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: allocations superuser_bypass_allocations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_allocations ON public.allocations USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: api_keys superuser_bypass_api_keys; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_api_keys ON public.api_keys USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: approval_chain_approvers superuser_bypass_approval_chain_approvers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_approval_chain_approvers ON public.approval_chain_approvers USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: approval_chains superuser_bypass_approval_chains; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_approval_chains ON public.approval_chains USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: approval_requests superuser_bypass_approval_requests; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_approval_requests ON public.approval_requests USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: assets superuser_bypass_assets; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_assets ON public.assets USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: attendance superuser_bypass_attendance; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_attendance ON public.attendance USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: automation_execution_logs superuser_bypass_automation_execution_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_automation_execution_logs ON public.automation_execution_logs USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: backups superuser_bypass_backups; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_backups ON public.backups USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: beds superuser_bypass_beds; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_beds ON public.beds USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: bonuses superuser_bypass_bonuses; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_bonuses ON public.bonuses USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: buildings superuser_bypass_buildings; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_buildings ON public.buildings USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: canned_responses superuser_bypass_canned_responses; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_canned_responses ON public.canned_responses USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: chat_messages superuser_bypass_chat_messages; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_chat_messages ON public.chat_messages USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: chat_sessions superuser_bypass_chat_sessions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_chat_sessions ON public.chat_sessions USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: courier_vehicle_assignments superuser_bypass_courier_vehicle_assignments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_courier_vehicle_assignments ON public.courier_vehicle_assignments USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: couriers superuser_bypass_couriers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_couriers ON public.couriers USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: dashboards superuser_bypass_dashboards; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_dashboards ON public.dashboards USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: deliveries superuser_bypass_deliveries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_deliveries ON public.deliveries USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: dispatch_assignments superuser_bypass_dispatch_assignments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_dispatch_assignments ON public.dispatch_assignments USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: documents superuser_bypass_documents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_documents ON public.documents USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: faqs superuser_bypass_faqs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_faqs ON public.faqs USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: feedback_templates superuser_bypass_feedback_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_feedback_templates ON public.feedback_templates USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: fuel_logs superuser_bypass_fuel_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_fuel_logs ON public.fuel_logs USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: handovers superuser_bypass_handovers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_handovers ON public.handovers USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: incidents superuser_bypass_incidents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_incidents ON public.incidents USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: integrations superuser_bypass_integrations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_integrations ON public.integrations USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: kb_articles superuser_bypass_kb_articles; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_kb_articles ON public.kb_articles USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: kb_categories superuser_bypass_kb_categories; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_kb_categories ON public.kb_categories USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: kpis superuser_bypass_kpis; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_kpis ON public.kpis USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: leaves superuser_bypass_leaves; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_leaves ON public.leaves USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: loans superuser_bypass_loans; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_loans ON public.loans USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: metric_snapshots superuser_bypass_metric_snapshots; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_metric_snapshots ON public.metric_snapshots USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: operations_documents superuser_bypass_operations_documents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_operations_documents ON public.operations_documents USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: performance_data superuser_bypass_performance_data; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_performance_data ON public.performance_data USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: priority_queue_entries superuser_bypass_priority_queue_entries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_priority_queue_entries ON public.priority_queue_entries USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: quality_inspections superuser_bypass_quality_inspections; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_quality_inspections ON public.quality_inspections USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: quality_metrics superuser_bypass_quality_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_quality_metrics ON public.quality_metrics USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: reports superuser_bypass_reports; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_reports ON public.reports USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: rooms superuser_bypass_rooms; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_rooms ON public.rooms USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: routes superuser_bypass_routes; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_routes ON public.routes USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: salaries superuser_bypass_salaries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_salaries ON public.salaries USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: sla_definitions superuser_bypass_sla_definitions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_sla_definitions ON public.sla_definitions USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: sla_events superuser_bypass_sla_events; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_sla_events ON public.sla_events USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: sla_tracking superuser_bypass_sla_tracking; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_sla_tracking ON public.sla_tracking USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: system_settings superuser_bypass_system_settings; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_system_settings ON public.system_settings USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: ticket_attachments superuser_bypass_ticket_attachments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_ticket_attachments ON public.ticket_attachments USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: ticket_replies superuser_bypass_ticket_replies; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_ticket_replies ON public.ticket_replies USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: ticket_templates superuser_bypass_ticket_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_ticket_templates ON public.ticket_templates USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: tickets superuser_bypass_tickets; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_tickets ON public.tickets USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: trigger_executions superuser_bypass_trigger_executions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_trigger_executions ON public.trigger_executions USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: vehicle_logs superuser_bypass_vehicle_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_vehicle_logs ON public.vehicle_logs USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: vehicle_maintenance superuser_bypass_vehicle_maintenance; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_vehicle_maintenance ON public.vehicle_maintenance USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: vehicles superuser_bypass_vehicles; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_vehicles ON public.vehicles USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_automations superuser_bypass_workflow_automations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_automations ON public.workflow_automations USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_instances superuser_bypass_workflow_instances; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_instances ON public.workflow_instances USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_metrics superuser_bypass_workflow_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_metrics ON public.workflow_metrics USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_performance_snapshots superuser_bypass_workflow_performance_snapshots; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_performance_snapshots ON public.workflow_performance_snapshots USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_sla_instances superuser_bypass_workflow_sla_instances; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_sla_instances ON public.workflow_sla_instances USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_slas superuser_bypass_workflow_slas; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_slas ON public.workflow_slas USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_step_metrics superuser_bypass_workflow_step_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_step_metrics ON public.workflow_step_metrics USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_templates superuser_bypass_workflow_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_templates ON public.workflow_templates USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_triggers superuser_bypass_workflow_triggers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_triggers ON public.workflow_triggers USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: workflow_user_metrics superuser_bypass_workflow_user_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_workflow_user_metrics ON public.workflow_user_metrics USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: zones superuser_bypass_zones; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY superuser_bypass_zones ON public.zones USING (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true)) WITH CHECK (((COALESCE(current_setting('app.is_superuser'::text, true), 'false'::text))::boolean = true));


--
-- Name: system_settings; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.system_settings ENABLE ROW LEVEL SECURITY;

--
-- Name: accident_logs tenant_isolation_accident_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_accident_logs ON public.accident_logs USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: allocations tenant_isolation_allocations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_allocations ON public.allocations USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: api_keys tenant_isolation_api_keys; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_api_keys ON public.api_keys USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: approval_chain_approvers tenant_isolation_approval_chain_approvers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_approval_chain_approvers ON public.approval_chain_approvers USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: approval_chains tenant_isolation_approval_chains; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_approval_chains ON public.approval_chains USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: approval_requests tenant_isolation_approval_requests; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_approval_requests ON public.approval_requests USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: assets tenant_isolation_assets; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_assets ON public.assets USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: attendance tenant_isolation_attendance; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_attendance ON public.attendance USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: automation_execution_logs tenant_isolation_automation_execution_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_automation_execution_logs ON public.automation_execution_logs USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: backups tenant_isolation_backups; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_backups ON public.backups USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: beds tenant_isolation_beds; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_beds ON public.beds USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: bonuses tenant_isolation_bonuses; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_bonuses ON public.bonuses USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: buildings tenant_isolation_buildings; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_buildings ON public.buildings USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: canned_responses tenant_isolation_canned_responses; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_canned_responses ON public.canned_responses USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: chat_messages tenant_isolation_chat_messages; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_chat_messages ON public.chat_messages USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: chat_sessions tenant_isolation_chat_sessions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_chat_sessions ON public.chat_sessions USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: courier_vehicle_assignments tenant_isolation_courier_vehicle_assignments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_courier_vehicle_assignments ON public.courier_vehicle_assignments USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: couriers tenant_isolation_couriers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_couriers ON public.couriers USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: dashboards tenant_isolation_dashboards; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_dashboards ON public.dashboards USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: deliveries tenant_isolation_deliveries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_deliveries ON public.deliveries USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: dispatch_assignments tenant_isolation_dispatch_assignments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_dispatch_assignments ON public.dispatch_assignments USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: documents tenant_isolation_documents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_documents ON public.documents USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: faqs tenant_isolation_faqs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_faqs ON public.faqs USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: feedback_templates tenant_isolation_feedback_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_feedback_templates ON public.feedback_templates USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: fuel_logs tenant_isolation_fuel_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_fuel_logs ON public.fuel_logs USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: handovers tenant_isolation_handovers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_handovers ON public.handovers USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: incidents tenant_isolation_incidents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_incidents ON public.incidents USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: integrations tenant_isolation_integrations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_integrations ON public.integrations USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: kb_articles tenant_isolation_kb_articles; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_kb_articles ON public.kb_articles USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: kb_categories tenant_isolation_kb_categories; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_kb_categories ON public.kb_categories USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: kpis tenant_isolation_kpis; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_kpis ON public.kpis USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: leaves tenant_isolation_leaves; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_leaves ON public.leaves USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: loans tenant_isolation_loans; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_loans ON public.loans USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: metric_snapshots tenant_isolation_metric_snapshots; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_metric_snapshots ON public.metric_snapshots USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: operations_documents tenant_isolation_operations_documents; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_operations_documents ON public.operations_documents USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: performance_data tenant_isolation_performance_data; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_performance_data ON public.performance_data USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: priority_queue_entries tenant_isolation_priority_queue_entries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_priority_queue_entries ON public.priority_queue_entries USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: quality_inspections tenant_isolation_quality_inspections; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_quality_inspections ON public.quality_inspections USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: quality_metrics tenant_isolation_quality_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_quality_metrics ON public.quality_metrics USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: reports tenant_isolation_reports; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_reports ON public.reports USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: rooms tenant_isolation_rooms; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_rooms ON public.rooms USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: routes tenant_isolation_routes; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_routes ON public.routes USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: salaries tenant_isolation_salaries; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_salaries ON public.salaries USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: sla_definitions tenant_isolation_sla_definitions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_sla_definitions ON public.sla_definitions USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: sla_events tenant_isolation_sla_events; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_sla_events ON public.sla_events USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: sla_tracking tenant_isolation_sla_tracking; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_sla_tracking ON public.sla_tracking USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: system_settings tenant_isolation_system_settings; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_system_settings ON public.system_settings USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: ticket_attachments tenant_isolation_ticket_attachments; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_ticket_attachments ON public.ticket_attachments USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: ticket_replies tenant_isolation_ticket_replies; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_ticket_replies ON public.ticket_replies USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: ticket_templates tenant_isolation_ticket_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_ticket_templates ON public.ticket_templates USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: tickets tenant_isolation_tickets; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_tickets ON public.tickets USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: trigger_executions tenant_isolation_trigger_executions; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_trigger_executions ON public.trigger_executions USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: vehicle_logs tenant_isolation_vehicle_logs; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_vehicle_logs ON public.vehicle_logs USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: vehicle_maintenance tenant_isolation_vehicle_maintenance; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_vehicle_maintenance ON public.vehicle_maintenance USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: vehicles tenant_isolation_vehicles; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_vehicles ON public.vehicles USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_automations tenant_isolation_workflow_automations; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_automations ON public.workflow_automations USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_instances tenant_isolation_workflow_instances; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_instances ON public.workflow_instances USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_metrics tenant_isolation_workflow_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_metrics ON public.workflow_metrics USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_performance_snapshots tenant_isolation_workflow_performance_snapshots; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_performance_snapshots ON public.workflow_performance_snapshots USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_sla_instances tenant_isolation_workflow_sla_instances; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_sla_instances ON public.workflow_sla_instances USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_slas tenant_isolation_workflow_slas; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_slas ON public.workflow_slas USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_step_metrics tenant_isolation_workflow_step_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_step_metrics ON public.workflow_step_metrics USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_templates tenant_isolation_workflow_templates; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_templates ON public.workflow_templates USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_triggers tenant_isolation_workflow_triggers; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_triggers ON public.workflow_triggers USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: workflow_user_metrics tenant_isolation_workflow_user_metrics; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_workflow_user_metrics ON public.workflow_user_metrics USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: zones tenant_isolation_zones; Type: POLICY; Schema: public; Owner: postgres
--

CREATE POLICY tenant_isolation_zones ON public.zones USING ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id))) WITH CHECK ((organization_id = COALESCE((NULLIF(current_setting('app.current_org_id'::text, true), ''::text))::integer, organization_id)));


--
-- Name: ticket_attachments; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.ticket_attachments ENABLE ROW LEVEL SECURITY;

--
-- Name: ticket_replies; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.ticket_replies ENABLE ROW LEVEL SECURITY;

--
-- Name: ticket_templates; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.ticket_templates ENABLE ROW LEVEL SECURITY;

--
-- Name: tickets; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.tickets ENABLE ROW LEVEL SECURITY;

--
-- Name: trigger_executions; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.trigger_executions ENABLE ROW LEVEL SECURITY;

--
-- Name: vehicle_logs; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.vehicle_logs ENABLE ROW LEVEL SECURITY;

--
-- Name: vehicle_maintenance; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.vehicle_maintenance ENABLE ROW LEVEL SECURITY;

--
-- Name: vehicles; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.vehicles ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_automations; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_automations ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_instances; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_instances ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_metrics; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_performance_snapshots; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_performance_snapshots ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_sla_instances; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_sla_instances ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_slas; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_slas ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_step_metrics; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_step_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_templates; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_templates ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_triggers; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_triggers ENABLE ROW LEVEL SECURITY;

--
-- Name: workflow_user_metrics; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.workflow_user_metrics ENABLE ROW LEVEL SECURITY;

--
-- Name: zones; Type: ROW SECURITY; Schema: public; Owner: postgres
--

ALTER TABLE public.zones ENABLE ROW LEVEL SECURITY;

--
-- Name: SCHEMA barq; Type: ACL; Schema: -; Owner: ramiz_new
--

GRANT USAGE ON SCHEMA barq TO barq_app;
GRANT USAGE ON SCHEMA barq TO barq_readonly;


--
-- Name: FUNCTION audit_trigger_function(); Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON FUNCTION barq.audit_trigger_function() TO barq_app;


--
-- Name: FUNCTION refresh_courier_summary(); Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON FUNCTION barq.refresh_courier_summary() TO barq_app;


--
-- Name: FUNCTION update_updated_at_column(); Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON FUNCTION barq.update_updated_at_column() TO barq_app;


--
-- Name: TABLE audit_logs; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.audit_logs TO barq_app;
GRANT SELECT ON TABLE barq.audit_logs TO barq_readonly;


--
-- Name: TABLE couriers; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.couriers TO barq_app;
GRANT SELECT ON TABLE barq.couriers TO barq_readonly;


--
-- Name: TABLE leave_approvals; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.leave_approvals TO barq_app;
GRANT SELECT ON TABLE barq.leave_approvals TO barq_readonly;


--
-- Name: TABLE leave_requests; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.leave_requests TO barq_app;
GRANT SELECT ON TABLE barq.leave_requests TO barq_readonly;


--
-- Name: TABLE vehicle_assignments; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.vehicle_assignments TO barq_app;
GRANT SELECT ON TABLE barq.vehicle_assignments TO barq_readonly;


--
-- Name: TABLE vehicles; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.vehicles TO barq_app;
GRANT SELECT ON TABLE barq.vehicles TO barq_readonly;


--
-- Name: TABLE workflow_instances; Type: ACL; Schema: barq; Owner: ramiz_new
--

GRANT ALL ON TABLE barq.workflow_instances TO barq_app;
GRANT SELECT ON TABLE barq.workflow_instances TO barq_readonly;


--
-- PostgreSQL database dump complete
--

