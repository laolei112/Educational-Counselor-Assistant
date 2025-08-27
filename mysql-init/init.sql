-- MySQL 初始化脚本
-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS dev_yundisoft CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 确保使用正确的数据库
USE dev_yundisoft;

-- 设置时区
SET time_zone = '+08:00';

-- 可以在这里添加其他初始化 SQL 语句
-- 例如：创建初始表、插入基础数据等

-- 显示创建成功的信息
SELECT 'Database dev_yundisoft initialized successfully' as message; 