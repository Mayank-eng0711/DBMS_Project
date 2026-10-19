-- Attendance Management System
-- Run this file in MySQL Workbench if you want to create the schema manually.

CREATE DATABASE IF NOT EXISTS attendance_db;
USE attendance_db;

CREATE TABLE IF NOT EXISTS Student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    branch VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    email VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS Subject (
    subject_id INT PRIMARY KEY AUTO_INCREMENT,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent') NOT NULL,
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id)
        REFERENCES Student(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_attendance_subject FOREIGN KEY (subject_id)
        REFERENCES Subject(subject_id) ON DELETE CASCADE,
    CONSTRAINT uq_attendance_per_day UNIQUE (student_id, subject_id, attendance_date)
);

-- Useful checks in MySQL Workbench:
SHOW TABLES;
DESCRIBE Student;
DESCRIBE Subject;
DESCRIBE Attendance;
SELECT * FROM Student;
SELECT * FROM Subject;
SELECT * FROM Attendance;
