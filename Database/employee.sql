-- phpMyAdmin SQL Dump
-- version 5.4.6
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Oct 25, 2020 at 09:17 AM
-- Server version: 5.6.35
-- PHP Version: 5.5.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `heyzot-analytics`
--

-- --------------------------------------------------------

--
-- Table structure for table `city`
--

CREATE TABLE `employee` (
  `id` int(11) NOT NULL,
  `name` varchar(30) NOT NULL,
  `age` int(11) NOT NULL,
  `salary` int(11) NOT NULL,
  `cityId` int(11) NOT NULL,
  `email` varchar(30) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `city`
--

INSERT INTO `employee` (`id`, `name`, `age`, `salary`, `cityId`, `email`) VALUES
(1, 'Paul', 22, 1000, 2, 'pl2019'),
(2, 'John', 25, 2000, 1, 'js114'),
(3, 'Sandy', 26, 1000, 1, 'dy1010'),
(4, 'Paula', 21, 3000, 3, 'pla200'),
(5, 'Johny', 31, 5000, 2, 'jny19');

-- --------------------------------------------------------

--
-- Table structure for table `emp`
--

CREATE TABLE `city` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `pincode` int(11) NOT NULL,
  `department` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `emp`
--

INSERT INTO `city` (`id`, `name`, `pincode`, `department`) VALUES
(1, 'Indore', 452010, 'sales'),
(2, 'Guwahati', 781039, 'hr'),
(3, 'Surat', 134521, 'it'),
(4, 'Mumbai', 235021, 'sales'),
(5, 'Chandigarh', 332001, 'it'),
(6, 'Hyderabad', 154052, 'engineering'),
(7, 'Phoenix', 234056, 'design');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `city`
--
ALTER TABLE `city`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id` (`id`);

--
-- Indexes for table `emp`
--
ALTER TABLE `employee`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cityId` (`cityId`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `emp`
--
ALTER TABLE `employee`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=31;
--
-- Constraints for dumped tables
--

--
-- Constraints for table `emp`
--
ALTER TABLE `employee`
  ADD CONSTRAINT `emp_ibfk_1` FOREIGN KEY (`cityId`) REFERENCES `city` (`id`);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
