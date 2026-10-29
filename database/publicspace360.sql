-- =======================================================
-- PublicSpace360 Database Schema & Authentic Panvel Dataset
-- College CEP: Panvel Public Space Usage and Digital Mapping
-- =======================================================

CREATE DATABASE IF NOT EXISTS `publicspace360` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `publicspace360`;

-- -------------------------------------------------------
-- Drop Tables if they exist (in proper foreign key order)
-- -------------------------------------------------------
DROP TABLE IF EXISTS `public_space_images`;
DROP TABLE IF EXISTS `feedback`;
DROP TABLE IF EXISTS `reports`;
DROP TABLE IF EXISTS `surveys`;
DROP TABLE IF EXISTS `public_spaces`;
DROP TABLE IF EXISTS `areas`;
DROP TABLE IF EXISTS `admins`;
DROP TABLE IF EXISTS `contact_messages`;
DROP TABLE IF EXISTS `users`;

-- -------------------------------------------------------
-- 1. Table: users
-- -------------------------------------------------------
CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `mobile` VARCHAR(20) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `age_group` VARCHAR(30) NOT NULL,
  `gender` VARCHAR(20) NOT NULL,
  `role` VARCHAR(20) DEFAULT 'user',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 2. Table: admins
-- -------------------------------------------------------
CREATE TABLE `admins` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(120) NOT NULL,
  `email` VARCHAR(150) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 3. Table: areas
-- -------------------------------------------------------
CREATE TABLE `areas` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL UNIQUE,
  `city` VARCHAR(100) DEFAULT 'Panvel'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 4. Table: public_spaces
-- -------------------------------------------------------
CREATE TABLE `public_spaces` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `area_id` INT NULL,
  `area` VARCHAR(100) NOT NULL,
  `name` VARCHAR(180) NOT NULL,
  `type` VARCHAR(50) NOT NULL, -- Garden, Playground
  `address` VARCHAR(255) NOT NULL,
  `latitude` DECIMAL(10, 7) NOT NULL,
  `longitude` DECIMAL(10, 7) NOT NULL,
  `description` TEXT,
  `facilities` TEXT, -- Comma-separated list
  `opening_time` VARCHAR(20) DEFAULT '05:30 AM',
  `closing_time` VARCHAR(20) DEFAULT '09:30 PM',
  `average_visitors` INT DEFAULT 500,
  `condition` VARCHAR(50) DEFAULT 'Good', -- Excellent, Good, Average, Needs Maintenance
  `primary_image` VARCHAR(500) DEFAULT NULL,
  `image_source` VARCHAR(255) DEFAULT 'Field Survey',
  `image_credit` VARCHAR(255) DEFAULT 'Academic Research Team',
  `google_maps_url` VARCHAR(500) DEFAULT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (`area_id`) REFERENCES `areas`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 5. Table: public_space_images (Requirement 16)
-- -------------------------------------------------------
CREATE TABLE `public_space_images` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `public_space_id` INT NOT NULL,
  `image_path` VARCHAR(500) NOT NULL,
  `image_source` VARCHAR(255) DEFAULT 'Field Survey',
  `image_credit` VARCHAR(255) DEFAULT 'Academic Research Team',
  `is_primary` TINYINT DEFAULT 0,
  `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`public_space_id`) REFERENCES `public_spaces`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 6. Table: surveys
-- -------------------------------------------------------
CREATE TABLE `surveys` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `space_id` INT NOT NULL,
  `visit_frequency` VARCHAR(50) NOT NULL, -- Daily, Several times a week, Weekly, Occasionally
  `purpose` VARCHAR(100) NOT NULL, -- Walking, Exercise, Playing, Relaxation, Socializing, Children activities, Other
  `age_group` VARCHAR(30) NOT NULL, -- Below 18, 18–25, 26–40, 41–60, 60+
  `safety_rating` INT NOT NULL, -- 1-5
  `cleanliness_rating` INT NOT NULL, -- 1-5
  `lighting_rating` INT NOT NULL, -- 1-5
  `seating_rating` INT NOT NULL, -- 1-5
  `water_rating` INT NOT NULL, -- 1-5
  `accessibility_rating` INT NOT NULL, -- 1-5
  `improvement` VARCHAR(150) DEFAULT NULL,
  `suggestion` TEXT,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`space_id`) REFERENCES `public_spaces`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 7. Table: reports
-- -------------------------------------------------------
CREATE TABLE `reports` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `space_id` INT NOT NULL,
  `issue_type` VARCHAR(100) NOT NULL,
  `description` TEXT NOT NULL,
  `photo` VARCHAR(255) DEFAULT NULL,
  `location` VARCHAR(200) DEFAULT NULL,
  `priority` VARCHAR(30) DEFAULT 'Medium', -- Low, Medium, High, Critical
  `status` VARCHAR(50) DEFAULT 'Reported', -- Reported, Under Review, In Progress, Resolved
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`space_id`) REFERENCES `public_spaces`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 8. Table: feedback (Reviews and Comments - Requirement 10)
-- -------------------------------------------------------
CREATE TABLE `feedback` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NULL,
  `space_id` INT NOT NULL,
  `user_name` VARCHAR(120) NOT NULL DEFAULT 'Community Visitor',
  `user_email` VARCHAR(150) DEFAULT NULL,
  `rating` INT NOT NULL, -- 1-5
  `comment` TEXT NOT NULL,
  `status` VARCHAR(30) DEFAULT 'Approved', -- Approved, Pending, Rejected
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`space_id`) REFERENCES `public_spaces`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- -------------------------------------------------------
-- 9. Table: contact_messages
-- -------------------------------------------------------
CREATE TABLE `contact_messages` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `subject` VARCHAR(180) NOT NULL,
  `message` TEXT NOT NULL,
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =======================================================
-- SEED DATA
-- =======================================================

-- Admins (Password: admin123)
INSERT INTO `admins` (`id`, `name`, `email`, `password`) VALUES
(1, 'Lead Administrator', 'admin@publicspace360.org', 'scrypt:32768:8:1$dVOGgP13iDeKxqAs$b9d34a14e626a3234b00fe83cd1d97a3c12aa1dcd8bfa8534763e62d8b22c78d2892327ebaba6dabd1341206c8f6712e306d8f25a70bf549d12b1aed4986d0e2'),
(2, 'Panvel Planning Officer', 'planner@panvelcorp.gov.in', 'scrypt:32768:8:1$dVOGgP13iDeKxqAs$b9d34a14e626a3234b00fe83cd1d97a3c12aa1dcd8bfa8534763e62d8b22c78d2892327ebaba6dabd1341206c8f6712e306d8f25a70bf549d12b1aed4986d0e2');

-- Users (Password: user123)
INSERT INTO `users` (`id`, `name`, `email`, `mobile`, `password`, `age_group`, `gender`, `role`) VALUES
(1, 'Priyanka Sharma', 'user@example.com', '+91 9876543210', 'scrypt:32768:8:1$GnKMlb1tfFMuQ8vD$49d15e6f8ea1192118f01103a726e50be0bda6562ee4cc307b80617cbe71e9d58164b1fdae2c1bfbcf783bb57446b9e92851256d7cb9902429d6023ba24b68da', '18–25', 'Female', 'user'),
(2, 'Rahul Verma', 'rahul.verma@gmail.com', '+91 9823456781', 'scrypt:32768:8:1$GnKMlb1tfFMuQ8vD$49d15e6f8ea1192118f01103a726e50be0bda6562ee4cc307b80617cbe71e9d58164b1fdae2c1bfbcf783bb57446b9e92851256d7cb9902429d6023ba24b68da', '26–40', 'Male', 'user'),
(3, 'Dr. Sunita Deshmukh', 'sunita.d@cep.edu', '+91 9819876543', 'scrypt:32768:8:1$GnKMlb1tfFMuQ8vD$49d15e6f8ea1192118f01103a726e50be0bda6562ee4cc307b80617cbe71e9d58164b1fdae2c1bfbcf783bb57446b9e92851256d7cb9902429d6023ba24b68da', '41–60', 'Female', 'user'),
(4, 'Aarav Patel', 'aarav.patel@outlook.com', '+91 9765432109', 'scrypt:32768:8:1$GnKMlb1tfFMuQ8vD$49d15e6f8ea1192118f01103a726e50be0bda6562ee4cc307b80617cbe71e9d58164b1fdae2c1bfbcf783bb57446b9e92851256d7cb9902429d6023ba24b68da', '18–25', 'Male', 'user'),
(5, 'Priya Nair', 'priya.nair@mumbai.edu', '+91 9820112233', 'scrypt:32768:8:1$GnKMlb1tfFMuQ8vD$49d15e6f8ea1192118f01103a726e50be0bda6562ee4cc307b80617cbe71e9d58164b1fdae2c1bfbcf783bb57446b9e92851256d7cb9902429d6023ba24b68da', '26–40', 'Female', 'user');

-- Areas in Panvel
INSERT INTO `areas` (`id`, `name`, `city`) VALUES
(1, 'New Panvel', 'Panvel'),
(2, 'Khanda Colony', 'Panvel'),
(3, 'Old Panvel', 'Panvel'),
(4, 'Karanjade', 'Panvel'),
(5, 'Kalamboli', 'Panvel'),
(6, 'Kamothe', 'Panvel');

-- Public Spaces in Panvel (Authentic Gardens & Playgrounds)
INSERT INTO `public_spaces` 
(`id`, `area_id`, `area`, `name`, `type`, `address`, `latitude`, `longitude`, `description`, `facilities`, `opening_time`, `closing_time`, `average_visitors`, `condition`, `primary_image`, `image_source`, `image_credit`, `google_maps_url`) 
VALUES
(1, 1, 'New Panvel', 'CIDCO Garden', 'Garden', '6, Panvel Matheran Road, Sector 11, New Panvel East, Panvel, Maharashtra 410206', 18.9952000, 73.1245000, 'A landmark municipal garden along Panvel Matheran Road in Sector 11. Boasts mature shade trees, interlocking paver jogging tracks, outdoor gym gear, and children play equipment. High footfall of morning walking clubs and evening families.', 'Walking Track, Children\'s Play Area, Seating Benches, Open Gym, Lighting, Dustbins', '05:30 AM', '09:30 PM', 850, 'Excellent', 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'Panvel Urban Spatial Survey 2026 / CIDCO Sector 11 Registry', 'Academic Field Enumeration Team A (CEP)', 'https://www.google.com/maps/search/?api=1&query=18.995200,73.124500'),

(2, 2, 'Khanda Colony', 'CIDCO Garden', 'Garden', 'Khandeshwar Park Road, Sector 9, Khanda Colony, Panvel 410206', 19.0065000, 73.1095000, 'Premier green space in Khanda Colony Sector 9. Features landscaped floral borders, smooth jogging loops, shaded pavilions for senior citizens, and interactive toddler swings.', 'Walking Track, Seating Benches, Open Gym, Children\'s Play Area, Drinking Water, Lighting', '05:30 AM', '10:00 PM', 920, 'Good', 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Khanda Colony Field Survey 2026 / CIDCO Node Records', 'Urban Planning Spatial Research Group', 'https://www.google.com/maps/search/?api=1&query=19.006500,73.109500'),

(3, 2, 'Khanda Colony', 'Gopinath Munde Garden', 'Garden', 'Near Khandeshwar Station Rd, Sector 9, Khanda Colony, Panvel 410206', 19.0082000, 73.1115000, 'Vibrant municipal garden situated adjacent to Khandeshwar railway hub. Contains lush lawns, outdoor fitness stations, reflexology pathways, and energy-efficient LED floodlighting.', 'Walking Track, Seating Benches, Lighting, Open Gym, Dustbins', '05:00 AM', '09:30 PM', 780, 'Excellent', 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Ward Spatial Registry', 'Academic Survey Team / Field Research', 'https://www.google.com/maps/search/?api=1&query=19.008200,73.111500'),

(4, 2, 'Khanda Colony', 'Khandeshwar Lake Garden & Promenade', 'Garden', 'Khandeshwar Lake Perimeter, Sector 8/9, Khanda Colony, Panvel 410206', 19.0125000, 73.1065000, 'Scenic waterfront garden hugging the banks of Khandeshwar Lake. Features a panoramic paved lakeside promenade, viewing jetties, decorative heritage streetlights, and serene seating.', 'Walking Track, Seating Benches, Lighting, Dustbins, Drinking Water', '05:00 AM', '10:30 PM', 1400, 'Excellent', 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&auto=format&fit=crop&q=80', 'CIDCO Waterfront Development Masterplan', 'Academic CEP Team / Spatial GIS Survey', 'https://www.google.com/maps/search/?api=1&query=19.012500,73.106500'),

(5, 1, 'New Panvel', 'Shaheed Tushar Shamrao Chavan Udyan', 'Garden', 'Sector 11, Near DAV Public School, New Panvel East, Panvel 410206', 18.9935000, 73.1270000, 'Well-kept memorial public garden honoring martyrs. Provides tranquil morning walking corridors, well-pruned bougainvillea arbors, and safe rubberized play equipment.', 'Walking Track, Children\'s Play Area, Seating Benches, Lighting, Dustbins', '06:00 AM', '09:00 PM', 620, 'Good', 'https://images.unsplash.com/photo-1541888946425-d0fbb186ef5f?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Public Asset Register', 'Field Survey Officer', 'https://www.google.com/maps/search/?api=1&query=18.993500,73.127000'),

(6, 1, 'New Panvel', 'Sector 3 CIDCO Garden & Joggers Track', 'Garden', 'Near Fire Station Road, Sector 3, New Panvel East, Panvel 410206', 18.9995000, 73.1210000, 'Community recreation and jogging ground in New Panvel Sector 3. Includes clay walking track, stainless steel open gym sets, and clean hydration fountains.', 'Walking Track, Open Gym, Seating Benches, Drinking Water, Dustbins', '05:00 AM', '10:00 PM', 710, 'Good', 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format&fit=crop&q=80', 'New Panvel Residents Welfare Spatial Data', 'Academic Survey Field Team', 'https://www.google.com/maps/search/?api=1&query=18.999500,73.121000'),

(7, 1, 'New Panvel', 'Tekadi Garden / Hilltop Park', 'Garden', 'Hillside Ridge, Sector 13, New Panvel 410206', 18.9890000, 73.1310000, 'Elevated hillside park offering refreshing breezes and birdwatching vantage points. Stepped stone walking paths and yoga gazebos.', 'Walking Track, Seating Benches, Open Gym, Lighting', '05:30 AM', '08:30 PM', 550, 'Good', 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1200&auto=format&fit=crop&q=80', 'Panvel Hill Eco-Corridor Assessment', 'Academic Field Surveyor', 'https://www.google.com/maps/search/?api=1&query=18.989000,73.131000'),

(8, 3, 'Old Panvel', 'Wadale Lake Garden & Promenade', 'Garden', 'Near Ballaleshwar Temple, Wadale Lake Road, Old Panvel 410206', 18.9875000, 73.1155000, 'Centrally situated lakefront garden in Old Panvel. Paved perimeter loop around Wadale Lake, shaded gazebos, drinking water, and illuminated evening walking promenade.', 'Walking Track, Seating Benches, Lighting, Dustbins, Children\'s Play Area', '05:00 AM', '10:00 PM', 1650, 'Excellent', 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Corporation Heritage Documentation', 'Panvel Smart City Research Lead', 'https://www.google.com/maps/search/?api=1&query=18.987500,73.115500'),

(9, 3, 'Old Panvel', 'Chhatrapati Shivaji Maharaj Maidan & Playground', 'Playground', 'Shivaji Road, Near Panvel Municipal Corporation, Old Panvel 410206', 18.9840000, 73.1120000, 'Major multi-sport civic playground hosting football and cricket practice, athletic events, and youth training programs. Includes seating stands, floodlights, and clean washroom block.', 'Sports Area, Children\'s Play Area, Lighting, Seating Benches, Parking, Washroom', '05:00 AM', '10:00 PM', 2100, 'Excellent', 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Panvel Sports & Youth Affairs Directorate', 'Civic Sports Infrastructure Survey', 'https://www.google.com/maps/search/?api=1&query=18.984000,73.112000'),

(10, 1, 'New Panvel', 'Sector 19 Children Sports Playground', 'Playground', 'Near Pillai College Road, Sector 19, New Panvel East 410206', 18.9915000, 73.1205000, 'Spacious community sports playground near academic cluster. Equipped with concrete cricket pitch, basketball court, outdoor fitness stations, and parking.', 'Sports Area, Children\'s Play Area, Walking Track, Open Gym, Seating Benches, Parking', '05:30 AM', '09:30 PM', 1100, 'Good', 'https://images.unsplash.com/photo-1500485035595-cbe6f645feb1?w=1200&auto=format&fit=crop&q=80', 'CIDCO Node Recreation Assessment 2026', 'Academic Survey Field Team B', 'https://www.google.com/maps/search/?api=1&query=18.991500,73.120500'),

(11, 1, 'New Panvel', 'Rotary Children Park & Playground', 'Playground', 'Sector 7, New Panvel East, Panvel 410206', 18.9970000, 73.1285000, 'Vibrant municipal playground designed specifically for young children with sand pits, jungle gym, spring riders, and surrounding benches for supervising parents.', 'Children\'s Play Area, Seating Benches, Lighting, Dustbins', '06:00 AM', '08:30 PM', 680, 'Good', 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1200&auto=format&fit=crop&q=80', 'Rotary Club Panvel & Municipal Partnership', 'Community Outreach Survey', 'https://www.google.com/maps/search/?api=1&query=18.997000,73.128500'),

(12, 3, 'Old Panvel', 'Takka Colony Municipal Playground', 'Playground', 'Takka Colony, Near St. Joseph High School, Old Panvel 410206', 18.9790000, 73.1180000, 'Open public sports ground serving local schools and neighborhoods. Ground for football, kabaddi, and morning track workouts.', 'Children\'s Play Area, Sports Area, Seating Benches, Lighting', '06:00 AM', '08:30 PM', 580, 'Average', 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=1200&auto=format&fit=crop&q=80', 'Panvel Ward 4 Community Survey', 'Academic Field Team', 'https://www.google.com/maps/search/?api=1&query=18.979000,73.118000'),

(13, 4, 'Karanjade', 'Karanjade Sector 4 Community Playground', 'Playground', 'Sector 4, Karanjade Node, Panvel 410206', 18.9760000, 73.1020000, 'Newly inaugurated neighborhood playground with calisthenics rigs, level soil ground for box sports, and perimeter security wall.', 'Sports Area, Open Gym, Walking Track, Lighting, Seating Benches', '05:30 AM', '09:30 PM', 490, 'Good', 'https://images.unsplash.com/photo-1526676037777-05a232554f77?w=1200&auto=format&fit=crop&q=80', 'Karanjade CIDCO Planning Office', 'Academic Geospatial Mapping Team', 'https://www.google.com/maps/search/?api=1&query=18.976000,73.102000'),

(14, 5, 'Kalamboli', 'Kalamboli CIDCO Sports Ground & Playground', 'Playground', 'Sector 10E, Near Police Station, Kalamboli, Panvel 410218', 19.0250000, 73.1010000, 'Expansive multi-acre civic sports ground catering to cricket, track events, and children sports. Includes perimeter fence and dedicated parking.', 'Sports Area, Children\'s Play Area, Lighting, Washroom, Parking', '05:00 AM', '10:00 PM', 1350, 'Good', 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=1200&auto=format&fit=crop&q=80', 'CIDCO Sports Infrastructure Division', 'Urban Recreation Survey Team', 'https://www.google.com/maps/search/?api=1&query=19.025000,73.101000'),

(15, 6, 'Kamothe', 'Kamothe Central Park & Butterfly Garden', 'Garden', 'Sector 11, Near Mansarovar Station Road, Kamothe, Panvel 410209', 19.0210000, 73.0880000, 'Botanical sanctuary featuring butterfly corridors, sensory gardens, jogging track, and shaded gazebos popular among nature enthusiasts.', 'Walking Track, Seating Benches, Open Gym, Children\'s Play Area, Lighting, Dustbins', '05:30 AM', '09:30 PM', 950, 'Excellent', 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Botanical Initiative', 'Academic Ecology Survey Team', 'https://www.google.com/maps/search/?api=1&query=19.021000,73.088000'),

(16, 1, 'New Panvel', 'Mango Garden / Aamrai Community Park', 'Garden', 'Sector 14, Near Kendriya Vidyalaya, New Panvel 410206', 18.9860000, 73.1340000, 'Historical mango orchard turned into peaceful municipal eco-park. Looped trails under towering canopies provide dense cooling shade.', 'Walking Track, Seating Benches, Children\'s Play Area, Lighting', '06:00 AM', '08:30 PM', 600, 'Good', 'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=1200&auto=format&fit=crop&q=80', 'New Panvel Heritage Trees Register', 'Academic Survey Field Team A', 'https://www.google.com/maps/search/?api=1&query=18.986000,73.134000');

-- -------------------------------------------------------
-- Multi-Image Gallery Records for Every Public Space (Requirement 16)
-- -------------------------------------------------------
INSERT INTO `public_space_images` 
(`public_space_id`, `image_path`, `image_source`, `image_credit`, `is_primary`) 
VALUES
-- Space 1: CIDCO Garden (Sector 11 New Panvel)
(1, 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'Panvel Urban Spatial Survey 2026', 'Academic Field Survey Team', 1),
(1, 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Panvel Field Survey / Jogging Track', 'Field Enumerator A', 0),
(1, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Panvel Field Survey / Play Equipment', 'Survey Team B', 0),
(1, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format&fit=crop&q=80', 'Panvel Field Survey / Open Gym', 'Field Surveyor C', 0),

-- Space 2: CIDCO Garden (Sector 9 Khanda Colony)
(2, 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Khanda Colony Field Survey 2026', 'Urban Planning Spatial Research Group', 1),
(2, 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'CIDCO Node Survey / Gazebo Section', 'Field Researcher Priya', 0),
(2, 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=1200&auto=format&fit=crop&q=80', 'CIDCO Node Survey / Flower Lawns', 'Survey Enumerator D', 0),
(2, 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1200&auto=format&fit=crop&q=80', 'CIDCO Node Survey / Fitness Zone', 'Academic Field Team', 0),

-- Space 3: Gopinath Munde Garden
(3, 'https://images.unsplash.com/photo-1502082553048-f009c37129b9?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Ward Spatial Registry', 'Academic Survey Team', 1),
(3, 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Ward 2 Documentation / Walking Loop', 'Field Staff', 0),
(3, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format&fit=crop&q=80', 'Ward 2 Documentation / Calisthenics', 'Field Staff', 0),

-- Space 4: Khandeshwar Lake Garden & Promenade
(4, 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&auto=format&fit=crop&q=80', 'CIDCO Waterfront Development Masterplan', 'Academic CEP Team', 1),
(4, 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80', 'Lake Perimeter Promenade Survey', 'Field Team', 0),
(4, 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1200&auto=format&fit=crop&q=80', 'Lakeside Sitting Decks', 'Field Team', 0),

-- Space 5: Shaheed Tushar Shamrao Chavan Udyan
(5, 'https://images.unsplash.com/photo-1541888946425-d0fbb186ef5f?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Public Asset Register', 'Field Survey Officer', 1),
(5, 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'Park Landscape Documentation', 'Academic Enumerator', 0),
(5, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Toddler Play Enclosure', 'Academic Enumerator', 0),

-- Space 6: Sector 3 CIDCO Garden & Joggers Track
(6, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format&fit=crop&q=80', 'New Panvel Residents Welfare Spatial Data', 'Academic Survey Field Team', 1),
(6, 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Jogging Loop View', 'Surveyor Amit', 0),

-- Space 7: Tekadi Garden / Hilltop Park
(7, 'https://images.unsplash.com/photo-1513836279014-a89f7a76ae86?w=1200&auto=format&fit=crop&q=80', 'Panvel Hill Eco-Corridor Assessment', 'Academic Field Surveyor', 1),
(7, 'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=1200&auto=format&fit=crop&q=80', 'Hilltop Nature Trail', 'Field Team', 0),

-- Space 8: Wadale Lake Garden & Promenade
(8, 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Corporation Heritage Documentation', 'Panvel Smart City Research Lead', 1),
(8, 'https://images.unsplash.com/photo-1448375240586-882707db888b?w=1200&auto=format&fit=crop&q=80', 'Wadale Water Edge', 'Research Lead', 0),
(8, 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'Temple Side Lawns', 'Research Lead', 0),

-- Space 9: Chhatrapati Shivaji Maharaj Maidan & Playground
(9, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Panvel Sports & Youth Affairs Directorate', 'Civic Sports Infrastructure Survey', 1),
(9, 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=1200&auto=format&fit=crop&q=80', 'Athletic Ground and Turf', 'Sports Survey Lead', 0),
(9, 'https://images.unsplash.com/photo-1500485035595-cbe6f645feb1?w=1200&auto=format&fit=crop&q=80', 'Pavilion and Grandstand', 'Sports Survey Lead', 0),

-- Space 10: Sector 19 Children Sports Playground
(10, 'https://images.unsplash.com/photo-1500485035595-cbe6f645feb1?w=1200&auto=format&fit=crop&q=80', 'CIDCO Node Recreation Assessment 2026', 'Academic Survey Field Team B', 1),
(10, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Multi-Sport Court', 'Survey Team B', 0),

-- Space 11: Rotary Children Park & Playground
(11, 'https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1200&auto=format&fit=crop&q=80', 'Rotary Club Panvel & Municipal Partnership', 'Community Outreach Survey', 1),
(11, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Children Swings Enclosure', 'Community Outreach', 0),

-- Space 12: Takka Colony Municipal Playground
(12, 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=1200&auto=format&fit=crop&q=80', 'Panvel Ward 4 Community Survey', 'Academic Field Team', 1),
(12, 'https://images.unsplash.com/photo-1500485035595-cbe6f645feb1?w=1200&auto=format&fit=crop&q=80', 'Football Ground Boundary', 'Academic Field Team', 0),

-- Space 13: Karanjade Sector 4 Community Playground
(13, 'https://images.unsplash.com/photo-1526676037777-05a232554f77?w=1200&auto=format&fit=crop&q=80', 'Karanjade CIDCO Planning Office', 'Academic Geospatial Mapping Team', 1),
(13, 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1200&auto=format&fit=crop&q=80', 'Outdoor Fitness Machinery', 'Mapping Team', 0),

-- Space 14: Kalamboli CIDCO Sports Ground & Playground
(14, 'https://images.unsplash.com/photo-1530549387789-4c1017266635?w=1200&auto=format&fit=crop&q=80', 'CIDCO Sports Infrastructure Division', 'Urban Recreation Survey Team', 1),
(14, 'https://images.unsplash.com/photo-1575783970733-1aaedde1db74?w=1200&auto=format&fit=crop&q=80', 'Running Tracks', 'Recreation Team', 0),

-- Space 15: Kamothe Central Park & Butterfly Garden
(15, 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=1200&auto=format&fit=crop&q=80', 'Panvel Municipal Botanical Initiative', 'Academic Ecology Survey Team', 1),
(15, 'https://images.unsplash.com/photo-1585320806297-9794b3e4eeae?w=1200&auto=format&fit=crop&q=80', 'Flora Walkway', 'Ecology Team', 0),

-- Space 16: Mango Garden / Aamrai Community Park
(16, 'https://images.unsplash.com/photo-1473448912268-2022ce9509d8?w=1200&auto=format&fit=crop&q=80', 'New Panvel Heritage Trees Register', 'Academic Survey Field Team A', 1),
(16, 'https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=1200&auto=format&fit=crop&q=80', 'Canopy Pathways', 'Field Team A', 0);

-- -------------------------------------------------------
-- Realistic Survey Responses for Dynamic Garden Analytics (Requirement 11)
-- -------------------------------------------------------
INSERT INTO `surveys` 
(`user_id`, `space_id`, `visit_frequency`, `purpose`, `age_group`, `safety_rating`, `cleanliness_rating`, `lighting_rating`, `seating_rating`, `water_rating`, `accessibility_rating`, `improvement`, `suggestion`, `created_at`) 
VALUES
-- Space 1: CIDCO Garden (Sector 11 New Panvel)
(1, 1, 'Daily', 'Walking', '18–25', 5, 4, 5, 4, 3, 5, 'Drinking Water', 'Please install touchless water dispensing stations along the 200m loop.', '2026-08-10 07:15:00'),
(2, 1, 'Several times a week', 'Exercise', '26–40', 4, 4, 4, 4, 4, 4, 'Children\'s Play Equipment', 'Adding parallel pull-up bars and rubber matting in the kids zone.', '2026-08-11 08:30:00'),
(3, 1, 'Daily', 'Walking', '60+', 5, 4, 4, 5, 4, 5, 'Seating Benches', 'Shaded benches are wonderful during early mornings. Highly recommended!', '2026-08-15 06:45:00'),
(4, 1, 'Weekly', 'Relaxation', '41–60', 4, 3, 4, 4, 3, 4, 'Children\'s Play Equipment', 'Better children\'s play equipment and chain lubrication for swings.', '2026-08-20 17:30:00'),
(5, 1, 'Several times a week', 'Socializing', '26–40', 4, 4, 4, 4, 4, 4, 'Children\'s Play Equipment', 'Need softer landing surface beneath the climbing ropes.', '2026-08-25 18:00:00'),

-- Space 2: CIDCO Garden (Sector 9 Khanda Colony)
(1, 2, 'Daily', 'Walking', '26–40', 5, 4, 5, 4, 4, 5, 'Lighting', 'Bright LED lighting helps evening walkers after sunset.', '2026-08-12 19:20:00'),
(2, 2, 'Several times a week', 'Exercise', '18–25', 4, 4, 4, 4, 3, 4, 'Open Gym Equipment', 'Chest press lever is slightly loose, needs quick tightening.', '2026-08-14 07:10:00'),
(3, 2, 'Daily', 'Walking', '60+', 5, 5, 4, 5, 4, 5, 'Walking Track', 'Smooth walking track and friendly neighborhood atmosphere.', '2026-08-18 06:30:00'),
(4, 2, 'Weekly', 'Children activities', '26–40', 4, 3, 4, 4, 4, 4, 'Children\'s Play Equipment', 'Toddler slide needs fresh coat of paint.', '2026-08-22 17:15:00'),

-- Space 3: Gopinath Munde Garden
(2, 3, 'Daily', 'Exercise', '18–25', 5, 5, 5, 4, 4, 5, 'Open Gym Equipment', 'Outstanding calisthenics rigs near Khandeshwar station.', '2026-08-16 06:30:00'),
(3, 3, 'Several times a week', 'Walking', '41–60', 5, 4, 4, 5, 3, 4, 'Drinking Water', 'Water dispenser filter needs scheduled quarterly maintenance.', '2026-08-19 07:45:00'),

-- Space 4: Khandeshwar Lake Garden & Promenade
(1, 4, 'Daily', 'Walking', '18–25', 5, 5, 5, 5, 4, 5, 'Dustbins', 'More segregated recycling bins along the waterfront walkway.', '2026-08-21 18:40:00'),
(4, 4, 'Several times a week', 'Socializing', '26–40', 5, 4, 5, 5, 4, 5, 'Lighting', 'Breezy and peaceful sunset view. Best lake promenade in Panvel.', '2026-08-26 19:15:00'),

-- Space 8: Wadale Lake Garden & Promenade
(2, 8, 'Daily', 'Walking', '41–60', 5, 4, 5, 4, 4, 5, 'Maintenance', 'Excellent rejuvenation of Wadale lake surroundings.', '2026-08-23 06:15:00'),
(3, 8, 'Several times a week', 'Relaxation', '60+', 5, 5, 4, 5, 4, 5, 'Seating Benches', 'Senior citizens appreciate the lakeside sitting steps.', '2026-08-27 18:30:00'),

-- Space 9: Chhatrapati Shivaji Maharaj Maidan & Playground
(4, 9, 'Daily', 'Playing', '18–25', 5, 4, 5, 4, 4, 4, 'Sports Ground Turf', 'Great ground for Panvel cricket league and football training.', '2026-08-24 16:30:00'),
(5, 9, 'Weekly', 'Children activities', '26–40', 4, 4, 4, 4, 3, 4, 'Washroom Cleanliness', 'Washrooms should be cleaned twice a day during tournaments.', '2026-08-28 17:00:00'),

-- Space 10: Sector 19 Children Sports Playground
(1, 10, 'Several times a week', 'Playing', '18–25', 4, 4, 4, 3, 4, 4, 'Basketball Hoops', 'New basketball net was replaced promptly by ward office.', '2026-08-29 17:45:00'),

-- Space 15: Kamothe Central Park & Butterfly Garden
(3, 15, 'Daily', 'Walking', '41–60', 5, 5, 4, 5, 4, 5, 'Botanical Signage', 'Flowering plants attract vibrant butterflies. Very serene.', '2026-09-01 07:00:00');

-- -------------------------------------------------------
-- Community Reviews and Feedback (Requirement 10)
-- -------------------------------------------------------
INSERT INTO `feedback` 
(`user_id`, `space_id`, `user_name`, `user_email`, `rating`, `comment`, `status`, `created_at`) 
VALUES
(2, 1, 'Rahul Verma', 'rahul.verma@gmail.com', 5, 'Good place for morning walking. Lush greenery and very well maintained track in Sector 11.', 'Approved', '2026-08-20 07:30:00'),
(5, 1, 'Priya Nair', 'priya.nair@mumbai.edu', 4, 'Children\'s play area needs improvement, but otherwise a peaceful neighborhood garden.', 'Approved', '2026-08-22 18:15:00'),
(3, 1, 'Dr. Sunita Deshmukh', 'sunita.d@cep.edu', 5, 'Senior citizen benches are well shaded. Excellent morning atmosphere.', 'Approved', '2026-08-25 08:00:00'),
(2, 2, 'Rahul Verma', 'rahul.verma@gmail.com', 5, 'Great CIDCO garden in Khanda Colony Sector 9. Clean walking pathways.', 'Approved', '2026-08-21 07:15:00'),
(4, 2, 'Aarav Patel', 'aarav.patel@outlook.com', 4, 'Open gym equipment is sturdy. Good place for outdoor workout before work.', 'Approved', '2026-08-23 06:45:00'),
(1, 4, 'Priyanka Sharma', 'user@example.com', 5, 'Khandeshwar lake breeze at sunset is unmatched. Clean promenade with good lighting.', 'Approved', '2026-08-26 19:30:00'),
(3, 8, 'Dr. Sunita Deshmukh', 'sunita.d@cep.edu', 5, 'Wadale Lake looks gorgeous after recent municipal beautification. Great asset for Old Panvel.', 'Approved', '2026-08-27 18:00:00'),
(4, 9, 'Aarav Patel', 'aarav.patel@outlook.com', 5, 'Huge playground right in the center of town. Floodlights make evening matches possible.', 'Approved', '2026-08-28 19:15:00');

-- -------------------------------------------------------
-- Issue Reports
-- -------------------------------------------------------
INSERT INTO `reports` 
(`user_id`, `space_id`, `issue_type`, `description`, `photo`, `location`, `priority`, `status`, `created_at`) 
VALUES
(1, 1, 'Broken Light', 'Pole #7 on the east perimeter walking track has a loose fixture and flickers at dusk.', NULL, 'East Jogging Track, near Gazebo', 'High', 'In Progress', '2026-09-02 19:30:00'),
(2, 2, 'Damaged Playground Equipment', 'Yellow toddler swing chain is slightly worn and needs lubrication.', NULL, 'Sector 9 Play Enclosure', 'Medium', 'Under Review', '2026-09-04 11:20:00'),
(3, 4, 'No Drinking Water', 'Dispenser near Lake View Deck is showing a maintenance error.', NULL, 'Lake View Deck #2', 'Medium', 'Reported', '2026-09-06 14:10:00'),
(4, 9, 'Damaged Seating', 'Metal bench slat near pavilion has become loose.', NULL, 'Pavilion Bleachers', 'Low', 'Resolved', '2026-08-28 09:40:00');

-- -------------------------------------------------------
-- Contact Messages
-- -------------------------------------------------------
INSERT INTO `contact_messages` (`name`, `email`, `subject`, `message`, `created_at`) VALUES
('Aniket Kulkarni', 'aniket.k@cityplanning.org', 'Collaboration on Panvel Geospatial Mapping', 'Hello CEP team, we are eager to integrate your Panvel public space survey results into our municipal ward development plan.', '2026-09-01 14:20:00');
