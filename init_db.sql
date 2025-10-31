-- 数据库初始化脚本：配煤优化系统
CREATE DATABASE IF NOT EXISTS coal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE coal_db;

-- 原煤数据表
DROP TABLE IF EXISTS raw_coals;
CREATE TABLE raw_coals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    calorific DOUBLE NOT NULL,
    ash DOUBLE NOT NULL,
    sulfur DOUBLE NOT NULL,
    price DOUBLE NOT NULL
);

INSERT INTO raw_coals (name, calorific, ash, sulfur, price) VALUES
('原煤A', 6000, 10, 0.6, 800),
('原煤B', 5000, 15, 0.9, 600),
('原煤C', 5500, 12, 0.7, 700);

-- 配煤历史记录表
DROP TABLE IF EXISTS blend_history;
CREATE TABLE blend_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME,
    result_json JSON
);