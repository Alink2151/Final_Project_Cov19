-- Create Resource Monitor and assign to warehouse
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE RESOURCE MONITOR RM_COVID
  WITH CREDIT_QUOTA = 20
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS ON 80 PERCENT DO NOTIFY
           ON 90 PERCENT DO SUSPEND
           ON 100 PERCENT DO SUSPEND_IMMEDIATE;

-- Warehouse will be created in another script and attached to this monitor