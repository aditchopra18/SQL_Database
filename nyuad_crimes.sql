-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 22, 2024 at 01:05 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `nyuad_crimes`
--

DELIMITER $$
--
-- Procedures
--
CREATE DEFINER=`root`@`localhost` PROCEDURE `AddCrime` (IN `p_Classification` VARCHAR(255), IN `p_Date_Charged` DATE, IN `p_Appeal_Status` BOOLEAN, IN `p_Hearing_Date` DATE, IN `p_Amount_Of_Fine` DECIMAL(10,2), IN `p_Court_Fee` DECIMAL(10,2), IN `p_Payment_Due_Date` DATE, IN `p_Charge_Status` VARCHAR(255), IN `p_Crime_Code` VARCHAR(255))   BEGIN
    DECLARE v_Crime_ID INT;


    INSERT INTO Crimes (Classification, Date_Charged, Appeal_Status, Hearing_Date, Amount_Of_Fine, Court_Fee, Amount_Paid, Payment_Due_Date, Charge_Status)
    VALUES (p_Classification, p_Date_Charged, p_Appeal_Status, p_Hearing_Date, p_Amount_Of_Fine, p_Court_Fee, 0, p_Payment_Due_Date, p_Charge_Status);
   
    SET v_Crime_ID = LAST_INSERT_ID();


    INSERT INTO Crime_Codes (Crime_ID, Crime_Code) VALUES (v_Crime_ID, p_Crime_Code);
END$$

DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `appeals`
--

CREATE TABLE `appeals` (
  `Appeal_ID` int(11) NOT NULL,
  `Appeal_Filing_Date` date DEFAULT NULL,
  `Appeal_Hearing_Date` date DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appeals`
--

INSERT INTO `appeals` (`Appeal_ID`, `Appeal_Filing_Date`, `Appeal_Hearing_Date`, `Status`) VALUES
(1, '2023-01-01', '2023-02-01', 'Filed'),
(2, '2023-02-02', '2023-03-02', 'Pending'),
(3, '2023-03-03', '2023-04-03', 'Denied'),
(4, '2023-04-04', '2023-05-04', 'Granted'),
(5, '2023-05-05', '2023-06-05', 'Filed'),
(6, '2023-06-06', '2023-07-06', 'Pending'),
(7, '2023-07-07', '2023-08-07', 'Denied'),
(8, '2023-08-08', '2023-09-08', 'Granted'),
(9, '2023-09-09', '2023-10-09', 'Filed'),
(10, '2023-10-10', '2023-11-10', 'Pending');

-- --------------------------------------------------------

--
-- Table structure for table `appeal_cutoff`
--

CREATE TABLE `appeal_cutoff` (
  `Hearing_Date` date NOT NULL,
  `Appeal_Cutoff_Date` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `appeal_cutoff`
--

INSERT INTO `appeal_cutoff` (`Hearing_Date`, `Appeal_Cutoff_Date`) VALUES
('2023-02-20', '2023-04-20'),
('2023-02-25', '2023-04-25'),
('2023-03-05', '2023-05-05'),
('2023-03-15', '2023-05-15'),
('2023-03-16', '2023-05-16'),
('2023-03-25', '2023-05-25'),
('2023-03-30', '2023-05-30'),
('2023-04-05', '2023-06-05'),
('2023-04-15', '2023-06-15'),
('2023-04-25', '2023-06-25');

-- --------------------------------------------------------

--
-- Table structure for table `crimes`
--

CREATE TABLE `crimes` (
  `Crime_ID` int(11) NOT NULL,
  `Classification` varchar(255) DEFAULT NULL,
  `Date_Charged` date DEFAULT NULL,
  `Appeal_Status` tinyint(1) DEFAULT NULL,
  `Hearing_Date` date DEFAULT NULL,
  `Amount_Of_Fine` decimal(10,2) DEFAULT NULL,
  `Court_Fee` decimal(10,2) DEFAULT NULL,
  `Amount_Paid` decimal(10,2) DEFAULT NULL,
  `Payment_Due_Date` date DEFAULT NULL,
  `Charge_Status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crimes`
--

INSERT INTO `crimes` (`Crime_ID`, `Classification`, `Date_Charged`, `Appeal_Status`, `Hearing_Date`, `Amount_Of_Fine`, `Court_Fee`, `Amount_Paid`, `Payment_Due_Date`, `Charge_Status`) VALUES
(1, 'Theft', '2023-01-10', 0, '2023-02-20', 500.00, 50.00, 550.00, '2023-03-10', 'Completed'),
(2, 'Burglary', '2023-01-15', 1, '2023-03-15', 1000.00, 100.00, 500.00, '2023-04-15', 'Pending'),
(3, 'Robbery', '2023-01-20', 0, '2023-02-25', 1500.00, 150.00, 1650.00, '2023-03-20', 'Completed'),
(4, 'Assault', '2023-01-25', 1, '2023-03-30', 2000.00, 200.00, 1000.00, '2023-04-25', 'Pending'),
(5, 'Fraud', '2023-02-01', 0, '2023-03-05', 2500.00, 250.00, 2750.00, '2023-04-01', 'Completed'),
(6, 'Homicide', '2023-02-05', 1, '2023-04-05', 3000.00, 300.00, 1500.00, '2023-05-05', 'Pending'),
(7, 'Kidnapping', '2023-02-10', 0, '2023-03-15', 3500.00, 350.00, 3850.00, '2023-04-10', 'Completed'),
(8, 'Arson', '2023-02-15', 1, '2023-04-15', 4000.00, 400.00, 2000.00, '2023-05-15', 'Pending'),
(9, 'Vandalism', '2023-02-20', 0, '2023-03-25', 4500.00, 450.00, 4950.00, '2023-04-20', 'Completed'),
(10, 'Drug Trafficking', '2023-02-25', 1, '2023-04-25', 5000.00, 500.00, 2500.00, '2023-05-25', 'Pending');

--
-- Triggers `crimes`
--
DELIMITER $$
CREATE TRIGGER `AfterPaymentUpdate` AFTER UPDATE ON `crimes` FOR EACH ROW BEGIN
    IF NEW.Amount_Paid >= NEW.Amount_Of_Fine THEN
        UPDATE Crimes SET Charge_Status = 'Completed' WHERE Crime_ID = NEW.Crime_ID;
    END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- Table structure for table `crime_arrest`
--

CREATE TABLE `crime_arrest` (
  `Crime_ID` int(11) NOT NULL,
  `Badge_Number` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crime_arrest`
--

INSERT INTO `crime_arrest` (`Crime_ID`, `Badge_Number`) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6),
(7, 7),
(8, 8),
(9, 9),
(10, 10);

-- --------------------------------------------------------

--
-- Table structure for table `crime_case`
--

CREATE TABLE `crime_case` (
  `Crime_ID` int(11) NOT NULL,
  `Criminal_ID` int(11) NOT NULL,
  `Sentence_ID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crime_case`
--

INSERT INTO `crime_case` (`Crime_ID`, `Criminal_ID`, `Sentence_ID`) VALUES
(1, 2, 3),
(2, 1, 2),
(3, 3, 10),
(3, 5, 6),
(4, 3, 1),
(5, 5, 9),
(5, 7, 5),
(6, 5, 4),
(7, 8, 7),
(8, 9, 8);

-- --------------------------------------------------------

--
-- Table structure for table `crime_codes`
--

CREATE TABLE `crime_codes` (
  `Crime_ID` int(11) NOT NULL,
  `Crime_Code` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `crime_codes`
--

INSERT INTO `crime_codes` (`Crime_ID`, `Crime_Code`) VALUES
(1, 'THF'),
(2, 'BRG'),
(3, 'ROB'),
(4, 'ASL'),
(5, 'FRD'),
(6, 'HMC'),
(7, 'KDN'),
(8, 'ARS'),
(9, 'VND'),
(10, 'DRG');

-- --------------------------------------------------------

--
-- Table structure for table `criminals`
--

CREATE TABLE `criminals` (
  `Criminal_ID` int(11) NOT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Address` varchar(255) DEFAULT NULL,
  `Violent_Offender_Status` tinyint(1) DEFAULT NULL,
  `Probation_Status` tinyint(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `criminals`
--

INSERT INTO `criminals` (`Criminal_ID`, `Name`, `Address`, `Violent_Offender_Status`, `Probation_Status`) VALUES
(1, 'Samo Zain', '50 Dairy St', 1, 0),
(2, 'Khalid Al', 'Palladium Hall', 0, 1),
(3, 'Saleh Zew', '80 Lafayette St', 1, 0),
(4, 'Rayed Pew', '12 E 4th St', 0, 1),
(5, 'Bruce Wayne', '654 Jay St', 0, 0),
(6, 'Clark Kent', '987 Metrotech', 1, 0),
(7, 'Ahmed Osman', '246 Union St', 1, 1),
(8, 'Mima Cindy', '135 Ahmed St', 0, 1),
(9, 'Ahmed Mohsen', '864 Lafayette St', 1, 0),
(10, 'Jana Kotb', '975 Aspen St', 1, 1),
(11, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `criminal_alias`
--

CREATE TABLE `criminal_alias` (
  `Criminal_ID` int(11) NOT NULL,
  `Alias` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `criminal_alias`
--

INSERT INTO `criminal_alias` (`Criminal_ID`, `Alias`) VALUES
(1, 'The Fox'),
(1, 'The Jackal'),
(1, 'The Wolf'),
(2, 'Ghost'),
(3, 'Halawa'),
(4, 'Bulldozer'),
(6, 'Nightmare'),
(7, 'Phantom'),
(9, 'The Snake'),
(10, 'The Rat');

-- --------------------------------------------------------

--
-- Table structure for table `criminal_phonenumber`
--

CREATE TABLE `criminal_phonenumber` (
  `Criminal_ID` int(11) NOT NULL,
  `Phone_Number` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `criminal_phonenumber`
--

INSERT INTO `criminal_phonenumber` (`Criminal_ID`, `Phone_Number`) VALUES
(1, '123-456-7890'),
(1, '234-567-8901'),
(2, '125-678-9112'),
(3, '345-678-9012'),
(4, '456-789-0123'),
(5, '567-890-1234'),
(6, '678-901-2345'),
(7, '789-012-3456'),
(8, '890-123-4567'),
(9, '901-234-5678'),
(10, '012-345-6789');

-- --------------------------------------------------------

--
-- Table structure for table `police_officers`
--

CREATE TABLE `police_officers` (
  `Badge_Number` int(11) NOT NULL,
  `Name` varchar(255) DEFAULT NULL,
  `Precinct` varchar(100) DEFAULT NULL,
  `Status` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `police_officers`
--

INSERT INTO `police_officers` (`Badge_Number`, `Name`, `Precinct`, `Status`) VALUES
(1, 'Officer A', 'North', 'Active'),
(2, 'Officer B', 'South', 'Inactive'),
(3, 'Officer C', 'East', 'Active'),
(4, 'Officer D', 'West', 'MIA'),
(5, 'Officer E', 'Central', 'Active'),
(6, 'Officer F', 'North', 'Inactive'),
(7, 'Officer G', 'South', 'Active'),
(8, 'Officer H', 'East', 'Inactive'),
(9, 'Officer I', 'West', 'Active'),
(10, 'Officer J', 'Central', 'Inactive');

-- --------------------------------------------------------

--
-- Table structure for table `police_officer_phonecontact`
--

CREATE TABLE `police_officer_phonecontact` (
  `Badge_Number` int(11) NOT NULL,
  `Phone_Contact` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `police_officer_phonecontact`
--

INSERT INTO `police_officer_phonecontact` (`Badge_Number`, `Phone_Contact`) VALUES
(1, '112-345-6788'),
(2, '212-345-6788'),
(3, '312-345-6788'),
(4, '412-345-6788'),
(5, '512-345-6788'),
(6, '612-345-6788'),
(7, '712-345-6788'),
(8, '812-345-6788'),
(9, '912-345-6788'),
(10, '101-345-6788');

-- --------------------------------------------------------

--
-- Table structure for table `sentencing`
--

CREATE TABLE `sentencing` (
  `Sentence_ID` int(11) NOT NULL,
  `Start_Date` date DEFAULT NULL,
  `End_Date` date DEFAULT NULL,
  `Number_of_Violations` int(11) DEFAULT NULL,
  `Type_of_Sentence` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `sentencing`
--

INSERT INTO `sentencing` (`Sentence_ID`, `Start_Date`, `End_Date`, `Number_of_Violations`, `Type_of_Sentence`) VALUES
(1, '2023-01-01', '2024-01-01', 1, 'Class time at Tandon'),
(2, '2023-02-01', '2024-02-01', 2, 'Probation'),
(3, '2023-03-01', '2024-03-01', 3, 'Incarceration'),
(4, '2023-04-01', '2024-04-01', 4, 'Death by Hugs'),
(5, '2023-05-01', '2024-05-01', 5, 'Community Service'),
(6, '2023-06-01', '2024-06-01', 6, 'Probation'),
(7, '2023-07-01', '2024-07-01', 7, 'Incarceration'),
(8, '2023-08-01', '2024-08-01', 8, 'House Arrest'),
(9, '2023-09-01', '2024-09-01', 9, 'Community Service'),
(10, '2023-10-01', '2024-10-01', 10, 'Probation');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `username` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appeals`
--
ALTER TABLE `appeals`
  ADD PRIMARY KEY (`Appeal_ID`);

--
-- Indexes for table `appeal_cutoff`
--
ALTER TABLE `appeal_cutoff`
  ADD PRIMARY KEY (`Hearing_Date`);

--
-- Indexes for table `crimes`
--
ALTER TABLE `crimes`
  ADD PRIMARY KEY (`Crime_ID`);

--
-- Indexes for table `crime_arrest`
--
ALTER TABLE `crime_arrest`
  ADD PRIMARY KEY (`Crime_ID`,`Badge_Number`),
  ADD KEY `Badge_Number` (`Badge_Number`);

--
-- Indexes for table `crime_case`
--
ALTER TABLE `crime_case`
  ADD PRIMARY KEY (`Crime_ID`,`Criminal_ID`,`Sentence_ID`),
  ADD KEY `Criminal_ID` (`Criminal_ID`),
  ADD KEY `Sentence_ID` (`Sentence_ID`);

--
-- Indexes for table `crime_codes`
--
ALTER TABLE `crime_codes`
  ADD PRIMARY KEY (`Crime_ID`,`Crime_Code`);

--
-- Indexes for table `criminals`
--
ALTER TABLE `criminals`
  ADD PRIMARY KEY (`Criminal_ID`);

--
-- Indexes for table `criminal_alias`
--
ALTER TABLE `criminal_alias`
  ADD PRIMARY KEY (`Criminal_ID`,`Alias`);

--
-- Indexes for table `criminal_phonenumber`
--
ALTER TABLE `criminal_phonenumber`
  ADD PRIMARY KEY (`Criminal_ID`,`Phone_Number`);

--
-- Indexes for table `police_officers`
--
ALTER TABLE `police_officers`
  ADD PRIMARY KEY (`Badge_Number`);

--
-- Indexes for table `police_officer_phonecontact`
--
ALTER TABLE `police_officer_phonecontact`
  ADD PRIMARY KEY (`Badge_Number`,`Phone_Contact`);

--
-- Indexes for table `sentencing`
--
ALTER TABLE `sentencing`
  ADD PRIMARY KEY (`Sentence_ID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appeals`
--
ALTER TABLE `appeals`
  MODIFY `Appeal_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `crimes`
--
ALTER TABLE `crimes`
  MODIFY `Crime_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `criminals`
--
ALTER TABLE `criminals`
  MODIFY `Criminal_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=12;

--
-- AUTO_INCREMENT for table `police_officers`
--
ALTER TABLE `police_officers`
  MODIFY `Badge_Number` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `sentencing`
--
ALTER TABLE `sentencing`
  MODIFY `Sentence_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `crime_arrest`
--
ALTER TABLE `crime_arrest`
  ADD CONSTRAINT `crime_arrest_ibfk_1` FOREIGN KEY (`Crime_ID`) REFERENCES `crimes` (`Crime_ID`),
  ADD CONSTRAINT `crime_arrest_ibfk_2` FOREIGN KEY (`Badge_Number`) REFERENCES `police_officers` (`Badge_Number`);

--
-- Constraints for table `crime_case`
--
ALTER TABLE `crime_case`
  ADD CONSTRAINT `crime_case_ibfk_1` FOREIGN KEY (`Crime_ID`) REFERENCES `crimes` (`Crime_ID`),
  ADD CONSTRAINT `crime_case_ibfk_2` FOREIGN KEY (`Criminal_ID`) REFERENCES `criminals` (`Criminal_ID`),
  ADD CONSTRAINT `crime_case_ibfk_3` FOREIGN KEY (`Sentence_ID`) REFERENCES `sentencing` (`Sentence_ID`);

--
-- Constraints for table `crime_codes`
--
ALTER TABLE `crime_codes`
  ADD CONSTRAINT `crime_codes_ibfk_1` FOREIGN KEY (`Crime_ID`) REFERENCES `crimes` (`Crime_ID`);

--
-- Constraints for table `criminal_alias`
--
ALTER TABLE `criminal_alias`
  ADD CONSTRAINT `FK_Criminal_Alias_Criminal_ID` FOREIGN KEY (`Criminal_ID`) REFERENCES `criminals` (`Criminal_ID`);

--
-- Constraints for table `criminal_phonenumber`
--
ALTER TABLE `criminal_phonenumber`
  ADD CONSTRAINT `FK_Criminal_PhoneNumber_Criminal_ID` FOREIGN KEY (`Criminal_ID`) REFERENCES `criminals` (`Criminal_ID`);

--
-- Constraints for table `police_officer_phonecontact`
--
ALTER TABLE `police_officer_phonecontact`
  ADD CONSTRAINT `police_officer_phonecontact_ibfk_1` FOREIGN KEY (`Badge_Number`) REFERENCES `police_officers` (`Badge_Number`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
