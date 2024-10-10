--
-- PostgreSQL database dump
--

-- Dumped from database version 16.2 (Postgres.app)
-- Dumped by pg_dump version 16.2 (Postgres.app)

CREATE TABLE analysis.zq_saleorder_temp (
	salesorderid int4 NOT NULL,
	salesdepartment varchar(255) NOT NULL,
	salesdate timestamp NOT NULL,
	salespersonname varchar(255) NOT NULL,
	salesamount numeric(10,2) NOT NULL,
	salesquantity int4 NOT NULL,
	productname varchar(255) NOT NULL,
	CONSTRAINT zq_saleorder_temp_pkey PRIMARY KEY (salesorderid)
);

-- 添加字段描述信息
COMMENT ON COLUMN analysis.zq_saleorder_temp.salesorderid IS '销售订单ID';
COMMENT ON COLUMN analysis.zq_saleorder_temp.salesdepartment IS '销售部门';
COMMENT ON COLUMN analysis.zq_saleorder_temp.salesdate IS '销售日期';
COMMENT ON COLUMN analysis.zq_saleorder_temp.salespersonname IS '销售人员姓名';
COMMENT ON COLUMN analysis.zq_saleorder_temp.salesamount IS '销售金额';
COMMENT ON COLUMN analysis.zq_saleorder_temp.salesquantity IS '销售数量';
COMMENT ON COLUMN analysis.zq_saleorder_temp.productname IS '产品名称';


CREATE TABLE analysis.zq_sales_dept (
	deptid varchar(32) NOT NULL,
	deptname varchar(255) NULL,
	CONSTRAINT zq_sales_dept_pkey PRIMARY KEY (deptid)
);

-- 添加字段描述信息
COMMENT ON COLUMN analysis.zq_sales_dept.deptid IS '部门ID';
COMMENT ON COLUMN analysis.zq_sales_dept.deptname IS '部门名称';


