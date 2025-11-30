/*
 Navicat Premium Data Transfer

 Source Server         : coal
 Source Server Type    : MySQL
 Source Server Version : 80042
 Source Host           : localhost:3306
 Source Schema         : coal_db

 Target Server Type    : MySQL
 Target Server Version : 80042
 File Encoding         : 65001

 Date: 30/11/2025 15:53:40
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blend_history
-- ----------------------------
DROP TABLE IF EXISTS `blend_history`;
CREATE TABLE `blend_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` datetime DEFAULT NULL,
  `result_json` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of blend_history
-- ----------------------------
BEGIN;
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (1, '2025-10-31 12:48:58', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (2, '2025-10-31 12:56:24', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": -0.0}, {\"name\": \"原煤C\", \"ratio\": 100.0}], \"指标\": {\"灰分\": 12.0, \"硫分\": 0.7, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (3, '2025-10-31 12:56:41', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (4, '2025-10-31 12:56:53', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 100.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 15.0, \"硫分\": 0.9, \"发热量\": 5000.0, \"单位成本\": 600.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (5, '2025-10-31 16:42:29', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (6, '2025-10-31 16:42:49', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 100.0}, {\"name\": \"原煤B\", \"ratio\": 0.0}, {\"name\": \"原煤C\", \"ratio\": -0.0}], \"指标\": {\"灰分\": 10.0, \"硫分\": 0.6, \"发热量\": 6000.0, \"单位成本\": 800.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (7, '2025-10-31 17:46:09', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (8, '2025-10-31 17:46:15', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (9, '2025-10-31 17:46:20', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (10, '2025-10-31 17:51:34', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (11, '2025-10-31 17:53:47', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (12, '2025-10-31 17:55:17', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 50.0}, {\"name\": \"原煤B\", \"ratio\": 50.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.5, \"硫分\": 0.75, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (13, '2025-11-01 16:35:53', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 1.86}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 98.14}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 6.17, \"硫分\": 8.85, \"发热量\": 99.0, \"单位成本\": 19.02}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (14, '2025-11-01 16:36:17', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 1.86}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 98.14}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 6.17, \"硫分\": 8.85, \"发热量\": 99.0, \"单位成本\": 19.02}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (15, '2025-11-01 16:39:48', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 24.69}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 75.31}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 8.22, \"硫分\": 7.0, \"发热量\": 1239.09, \"单位成本\": 154.17}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (16, '2025-11-01 16:50:36', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 24.69}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 75.31}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 8.22, \"硫分\": 7.0, \"发热量\": 1239.09, \"单位成本\": 154.17}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (17, '2025-11-01 16:50:53', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 24.69}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 75.31}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 8.22, \"硫分\": 7.0, \"发热量\": 1239.09, \"单位成本\": 154.17}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (18, '2025-11-03 08:44:14', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": -0.0}, {\"name\": \"原煤C\", \"ratio\": 100.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 0.0}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.0, \"硫分\": 0.7, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (19, '2025-11-03 08:44:38', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": -0.0}, {\"name\": \"原煤C\", \"ratio\": 100.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 0.0}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.0, \"硫分\": 0.7, \"发热量\": 5500.0, \"单位成本\": 700.0}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (20, '2025-11-03 08:46:56', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 0.0}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 95.51}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}, {\"name\": \"W煤\", \"ratio\": 4.49}], \"指标\": {\"灰分\": 6.63, \"硫分\": 9.0, \"发热量\": 900.0, \"单位成本\": 48.04}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (21, '2025-11-03 09:00:30', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 24.69}, {\"name\": \"原煤C\", \"ratio\": 0.0}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 75.31}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}, {\"name\": \"W煤\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 8.22, \"硫分\": 7.0, \"发热量\": 1239.09, \"单位成本\": 154.17}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (22, '2025-11-03 09:18:19', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 20.48}, {\"name\": \"原煤C\", \"ratio\": 78.81}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 0.0}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}, {\"name\": \"W煤\", \"ratio\": 0.71}], \"指标\": {\"灰分\": 12.67, \"硫分\": 0.8, \"发热量\": 5500.0, \"单位成本\": 680.93}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (23, '2025-11-28 09:13:25', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 20.48}, {\"name\": \"原煤C\", \"ratio\": 78.81}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 0.0}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}, {\"name\": \"W煤\", \"ratio\": 0.71}], \"指标\": {\"灰分\": 12.67, \"硫分\": 0.8, \"发热量\": 5500.0, \"单位成本\": 680.93}, \"success\": true}');
INSERT INTO `blend_history` (`id`, `timestamp`, `result_json`) VALUES (24, '2025-11-30 15:03:08', '{\"ratio\": [{\"name\": \"原煤A\", \"ratio\": 0.0}, {\"name\": \"原煤B\", \"ratio\": 20.48}, {\"name\": \"原煤C\", \"ratio\": 78.81}, {\"name\": \"222\", \"ratio\": 0.0}, {\"name\": \"123\", \"ratio\": 0.0}, {\"name\": \"eeee\", \"ratio\": 0.0}, {\"name\": \"test\", \"ratio\": 0.0}, {\"name\": \"666\", \"ratio\": 0.0}, {\"name\": \"W煤\", \"ratio\": 0.71}, {\"name\": \"123\", \"ratio\": 0.0}], \"指标\": {\"灰分\": 12.67, \"硫分\": 0.8, \"发热量\": 5500.0, \"单位成本\": 680.93}, \"success\": true}');
COMMIT;

-- ----------------------------
-- Table structure for raw_coals
-- ----------------------------
DROP TABLE IF EXISTS `raw_coals`;
CREATE TABLE `raw_coals` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `calorific` double NOT NULL,
  `ash` double NOT NULL,
  `sulfur` double NOT NULL,
  `price` double NOT NULL,
  `short_transport` double DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- ----------------------------
-- Records of raw_coals
-- ----------------------------
BEGIN;
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (1, '原煤A', 6000, 10, 0.6, 800, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (2, '原煤B', 5000, 15, 0.9, 600, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (3, '原煤C', 5500, 12, 0.7, 700, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (5, '222', 0, 222, 222, 222, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (6, '123', 6, 6, 9, 9, 15);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (7, 'eeee', 111, 111, 1111, 1111, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (8, 'test', 11, 22, 33, 44, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (9, '666', 16, 26, 37, 48, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (10, 'W煤', 19900, 20, 9, 899, 0);
INSERT INTO `raw_coals` (`id`, `name`, `calorific`, `ash`, `sulfur`, `price`, `short_transport`) VALUES (11, '123', 6, 6, 9, 88, 0);
COMMIT;

SET FOREIGN_KEY_CHECKS = 1;
