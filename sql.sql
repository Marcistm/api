-- MySQL dump 10.13  Distrib 8.3.0, for Win64 (x86_64)
--
-- Host: localhost    Database: nba
-- ------------------------------------------------------
-- Server version	8.3.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `evaluate`
--

DROP TABLE IF EXISTS `evaluate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluate` (
  `id` int NOT NULL AUTO_INCREMENT,
  `gameId` varchar(20) DEFAULT NULL,
  `username` varchar(20) DEFAULT NULL,
  `name` varchar(30) DEFAULT NULL,
  `rate` varchar(10) DEFAULT NULL,
  `comment` varchar(100) DEFAULT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `evaluate_id_uindex` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluate`
--

LOCK TABLES `evaluate` WRITE;
/*!40000 ALTER TABLE `evaluate` DISABLE KEYS */;
INSERT INTO `evaluate` VALUES (1,'0022301171','test','Kelly Oubre Jr.','3','','2024-04-13 15:27:11'),(2,'0022301171','test','Kelly Oubre Jr.','3','ss','2024-04-13 15:27:31'),(3,'0022301171','test','De\'Anthony Melton','2','ss','2024-04-13 15:35:21');
/*!40000 ALTER TABLE `evaluate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluate_report`
--

DROP TABLE IF EXISTS `evaluate_report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluate_report` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) DEFAULT NULL,
  `evaluateId` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `evaluate_report_id_uindex` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluate_report`
--

LOCK TABLES `evaluate_report` WRITE;
/*!40000 ALTER TABLE `evaluate_report` DISABLE KEYS */;
/*!40000 ALTER TABLE `evaluate_report` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluate_stats`
--

DROP TABLE IF EXISTS `evaluate_stats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluate_stats` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(20) DEFAULT NULL,
  `category` varchar(20) DEFAULT NULL,
  `evaluateId` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `evaluate_stats_id_uindex` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluate_stats`
--

LOCK TABLES `evaluate_stats` WRITE;
/*!40000 ALTER TABLE `evaluate_stats` DISABLE KEYS */;
/*!40000 ALTER TABLE `evaluate_stats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(40) DEFAULT '2b2786d75fe0463ed7a764532695dae0',
  `username` varchar(20) DEFAULT NULL,
  `privilege` int DEFAULT NULL,
  `name` varchar(20) DEFAULT NULL,
  `has_login` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `sys_user_id_uindex` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sys_user`
--

LOCK TABLES `sys_user` WRITE;
/*!40000 ALTER TABLE `sys_user` DISABLE KEYS */;
INSERT INTO `sys_user` VALUES (1,'2b2786d75fe0463ed7a764532695dae0','test',2,'test',1),(2,'2b2786d75fe0463ed7a764532695dae0','admin',2,'admin',1);
/*!40000 ALTER TABLE `sys_user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-04-17 16:54:25
