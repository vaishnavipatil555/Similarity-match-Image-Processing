-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 29, 2020 at 11:39 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `quality_assurance`
--

-- --------------------------------------------------------

--
-- Table structure for table `pdetails`
--

CREATE TABLE `pdetails` (
  `pname` varchar(50) NOT NULL,
  `pimage` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pdetails`
--

INSERT INTO `pdetails` (`pname`, `pimage`) VALUES
('Menu', 'Screenshot.png'),
('Optics box', 'opticsBox.jpeg');

-- --------------------------------------------------------

--
-- Table structure for table `pstats`
--

CREATE TABLE `pstats` (
  `pname` varchar(50) DEFAULT NULL,
  `pdate` date DEFAULT NULL,
  `passed` int(11) DEFAULT NULL,
  `failed` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pstats`
--

INSERT INTO `pstats` (`pname`, `pdate`, `passed`, `failed`) VALUES
('Optics box', '2020-05-26', 19, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pdetails`
--
ALTER TABLE `pdetails`
  ADD PRIMARY KEY (`pname`);

--
-- Indexes for table `pstats`
--
ALTER TABLE `pstats`
  ADD KEY `fk_pname` (`pname`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `pstats`
--
ALTER TABLE `pstats`
  ADD CONSTRAINT `fk_pname` FOREIGN KEY (`pname`) REFERENCES `pdetails` (`pname`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
