-- phpMyAdmin SQL Dump
-- version 4.9.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 01, 2020 at 06:42 PM
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
-- Database: `product_inspection`
--

-- --------------------------------------------------------

--
-- Table structure for table `pdetails`
--

CREATE TABLE `pdetails` (
  `pname` varchar(50) NOT NULL,
  `username` varchar(20) NOT NULL,
  `pimage` varchar(200) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pdetails`
--

INSERT INTO `pdetails` (`pname`, `username`, `pimage`) VALUES
('Admin_Smartphone', 'Admin', 'Admin_index.jpeg');

-- --------------------------------------------------------

--
-- Table structure for table `pstats`
--

CREATE TABLE `pstats` (
  `pname` varchar(50) NOT NULL,
  `username` varchar(20) NOT NULL,
  `pdate` date NOT NULL,
  `passed` int(11) NOT NULL,
  `failed` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pstats`
--

INSERT INTO `pstats` (`pname`, `username`, `pdate`, `passed`, `failed`) VALUES
('Admin_Smartphone', 'Admin', '2020-09-01', 0, 5);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `username` varchar(20) NOT NULL,
  `password` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`username`, `password`) VALUES
('Admin', 'admin123');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `pdetails`
--
ALTER TABLE `pdetails`
  ADD PRIMARY KEY (`pname`,`username`),
  ADD KEY `fk` (`username`);

--
-- Indexes for table `pstats`
--
ALTER TABLE `pstats`
  ADD KEY `fk1` (`pname`,`username`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`username`);

--
-- Constraints for dumped tables
--

--
-- Constraints for table `pdetails`
--
ALTER TABLE `pdetails`
  ADD CONSTRAINT `fk` FOREIGN KEY (`username`) REFERENCES `users` (`username`) ON DELETE CASCADE;

--
-- Constraints for table `pstats`
--
ALTER TABLE `pstats`
  ADD CONSTRAINT `fk1` FOREIGN KEY (`pname`,`username`) REFERENCES `pdetails` (`pname`, `username`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
