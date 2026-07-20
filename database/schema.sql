CREATE TABLE employees (
        employee_id      TEXT PRIMARY KEY,
        name             TEXT NOT NULL,
        email            TEXT NOT NULL,
        phone            TEXT,
        department       TEXT NOT NULL,
        designation      TEXT NOT NULL,
        date_of_joining  TEXT NOT NULL,
        exit_date        TEXT,
        status           TEXT NOT NULL CHECK (status IN ('active','inactive')),
        basic_salary     REAL NOT NULL,
        da_percent       REAL NOT NULL,
        hra_percent      REAL NOT NULL,
        other_allowances REAL NOT NULL,
        pf_percent       REAL NOT NULL,
        professional_tax REAL NOT NULL
    );

CREATE TABLE attendance (
        employee_id TEXT NOT NULL,
        date        TEXT NOT NULL,
        status      TEXT NOT NULL CHECK (status IN ('present','absent','half-day','leave')),
        PRIMARY KEY (employee_id, date),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

CREATE TABLE payroll (
        employee_id       TEXT NOT NULL,
        department        TEXT NOT NULL,
        month             INTEGER NOT NULL,
        year              INTEGER NOT NULL,
        working_days      INTEGER NOT NULL,
        present_days      INTEGER NOT NULL,
        absent_days       INTEGER NOT NULL,
        half_days         INTEGER NOT NULL,
        leave_days        INTEGER NOT NULL,
        basic_salary      REAL NOT NULL,
        da                REAL NOT NULL,
        hra               REAL NOT NULL,
        other_allowances  REAL NOT NULL,
        gross_salary      REAL NOT NULL,
        pf                REAL NOT NULL,
        professional_tax  REAL NOT NULL,
        lop_deduction     REAL NOT NULL,
        total_deductions  REAL NOT NULL,
        net_salary        REAL NOT NULL,
        status            TEXT NOT NULL,
        PRIMARY KEY (employee_id, year, month),
        FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    );

CREATE INDEX idx_attendance_date ON attendance(date);

CREATE INDEX idx_attendance_status ON attendance(status);

CREATE INDEX idx_payroll_year_month ON payroll(year, month);

CREATE INDEX idx_payroll_department ON payroll(department);

CREATE INDEX idx_employees_department ON employees(department);

CREATE INDEX idx_employees_status ON employees(status);

