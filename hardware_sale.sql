-- MySQL dump 10.13  Distrib 5.6.29-76.2, for Linux (x86_64)
--
-- Host: localhost    Database: hardware_sale
-- ------------------------------------------------------
-- Server version	5.6.29-76.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tbl_admin`
--

DROP TABLE IF EXISTS `tbl_admin`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_admin` (
  `admin_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `admin_name` varchar(255) NOT NULL,
  `hashed_password` varchar(255) NOT NULL,
  `admin_email` varchar(255) NOT NULL,
  PRIMARY KEY (`admin_id`),
  UNIQUE KEY `admin_name` (`admin_name`),
  UNIQUE KEY `admin_email` (`admin_email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_device`
--

DROP TABLE IF EXISTS `tbl_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_device` (
  `device_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `device_name` varchar(255) NOT NULL,
  `type_id` int(255) unsigned NOT NULL,
  `device_description` varchar(1024) DEFAULT NULL,
  `price` int(255) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`device_id`),
  UNIQUE KEY `device_id__ukey` (`device_id`),
  KEY `type_id__fkey` (`type_id`),
  CONSTRAINT `tbl_device_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `tbl_type` (`type_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_sale`
--

DROP TABLE IF EXISTS `tbl_sale`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_sale` (
  `sale_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `sale_name` varchar(255) NOT NULL,
  `sale_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`sale_id`),
  UNIQUE KEY `sale_id` (`sale_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_sale_device`
--

DROP TABLE IF EXISTS `tbl_sale_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_sale_device` (
  `sale_device_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `sale_id` int(255) unsigned NOT NULL,
  `device_id` int(255) unsigned NOT NULL,
  `quantity` int(255) DEFAULT '0',
  PRIMARY KEY (`sale_device_id`),
  UNIQUE KEY `sale_device_id` (`sale_device_id`),
  UNIQUE KEY `sale_device_id__ukey` (`sale_device_id`),
  KEY `sale_id__fkey` (`sale_id`),
  KEY `device_id__fkey` (`device_id`),
  CONSTRAINT `tbl_sale_device_ibfk_1` FOREIGN KEY (`sale_id`) REFERENCES `tbl_sale` (`sale_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tbl_sale_device_ibfk_2` FOREIGN KEY (`device_id`) REFERENCES `tbl_device` (`device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_type`
--

DROP TABLE IF EXISTS `tbl_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_type` (
  `type_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `type_name` varchar(255) NOT NULL,
  PRIMARY KEY (`type_id`),
  UNIQUE KEY `type_id` (`type_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_user`
--

DROP TABLE IF EXISTS `tbl_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_user` (
  `user_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `user_email` varchar(255) NOT NULL,
  `active` tinyint(1) unsigned NOT NULL DEFAULT '1',
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_name` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_user_sale_device`
--

DROP TABLE IF EXISTS `tbl_user_sale_device`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_user_sale_device` (
  `user_sale_device_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(255) unsigned NOT NULL,
  `sale_device_id` int(255) unsigned NOT NULL,
  `won` tinyint(1) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`user_sale_device_id`),
  UNIQUE KEY `user_sale_device_id__ukey` (`user_sale_device_id`),
  UNIQUE KEY `user_id` (`user_id`,`sale_device_id`),
  KEY `sale_device_id__fkey` (`sale_device_id`),
  KEY `user_id__fkey` (`user_id`),
  CONSTRAINT `tbl_user_sale_device_ibfk_1` FOREIGN KEY (`sale_device_id`) REFERENCES `tbl_sale_device` (`sale_device_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tbl_user_sale_device_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `tbl_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tbl_user_uuid`
--

DROP TABLE IF EXISTS `tbl_user_uuid`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tbl_user_uuid` (
  `user_uuid_id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` int(255) unsigned NOT NULL,
  `uuid` varchar(255) NOT NULL,
  `sale_device_id` int(255) unsigned NOT NULL,
  PRIMARY KEY (`user_uuid_id`),
  UNIQUE KEY `user_uuid_id__ukey` (`user_uuid_id`),
  KEY `user_id__fkey` (`user_id`),
  KEY `tbl_user_uuid_ibfk_2` (`sale_device_id`),
  CONSTRAINT `tbl_user_uuid_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `tbl_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `tbl_user_uuid_ibfk_2` FOREIGN KEY (`sale_device_id`) REFERENCES `tbl_sale_device` (`sale_device_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Temporary view structure for view `view_entrants`
--

DROP TABLE IF EXISTS `view_entrants`;
/*!50001 DROP VIEW IF EXISTS `view_entrants`*/;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
/*!50001 CREATE VIEW `view_entrants` AS SELECT 
 1 AS `sale_id`,
 1 AS `sale_name`,
 1 AS `sale_date`,
 1 AS `sale_device_id`,
 1 AS `quantity`,
 1 AS `device_id`,
 1 AS `device_name`,
 1 AS `device_description`,
 1 AS `price`,
 1 AS `type_id`,
 1 AS `type_name`,
 1 AS `user_sale_device_id`,
 1 AS `user_id`,
 1 AS `user_email`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `view_entrants`
--

/*!50001 DROP VIEW IF EXISTS `view_entrants`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8 */;
/*!50001 SET character_set_results     = utf8 */;
/*!50001 SET collation_connection      = utf8_general_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `view_entrants` AS select `s`.`sale_id` AS `sale_id`,`s`.`sale_name` AS `sale_name`,`s`.`sale_date` AS `sale_date`,`sd`.`sale_device_id` AS `sale_device_id`,`sd`.`quantity` AS `quantity`,`d`.`device_id` AS `device_id`,`d`.`device_name` AS `device_name`,`d`.`device_description` AS `device_description`,`d`.`price` AS `price`,`t`.`type_id` AS `type_id`,`t`.`type_name` AS `type_name`,`usd`.`user_sale_device_id` AS `user_sale_device_id`,`u`.`user_id` AS `user_id`,`u`.`user_email` AS `user_email` from (((((`tbl_sale` `s` join `tbl_sale_device` `sd` on((`s`.`sale_id` = `sd`.`sale_id`))) join `tbl_device` `d` on((`d`.`device_id` = `sd`.`device_id`))) join `tbl_type` `t` on((`t`.`type_id` = `d`.`type_id`))) join `tbl_user_sale_device` `usd` on((`sd`.`sale_device_id` = `usd`.`sale_device_id`))) join `tbl_user` `u` on((`u`.`user_id` = `usd`.`user_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-05-02 11:26:53
