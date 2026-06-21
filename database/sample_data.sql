-- Insert default admin user (plain text for beginner simplicity)
INSERT INTO users (username, password) VALUES ('admin', 'admin123');

-- Insert initial satellites
INSERT INTO satellites (name, launch_date, orbit_type, status) VALUES
('Polaris-1', '2024-01-15', 'LEO', 'Active'),
('Polaris-2', '2024-03-22', 'MEO', 'Active'),
('Astra-X', '2023-11-10', 'GEO', 'Inactive'),
('Nova-Explorer', '2025-05-01', 'LEO', 'Active');

-- Insert initial missions
INSERT INTO missions (name, target, start_date, status) VALUES
('Artemis Relay', 'Moon', '2024-02-10', 'Active'),
('Mars Pathfinder II', 'Mars', '2024-05-15', 'Active'),
('Titan Atmospheric Probe', 'Titan', '2023-09-01', 'Completed'),
('Europa Ocean Explorer', 'Europa', '2026-08-01', 'Planning');

-- Insert initial telemetry data
INSERT INTO telemetry (satellite_id, temperature, battery_level, signal_strength, timestamp) VALUES
(1, 24.5, 98.0, -55.0, '2026-06-21 12:00:00'),
(1, 25.1, 97.2, -56.5, '2026-06-21 12:05:00'),
(2, 18.2, 85.0, -62.0, '2026-06-21 12:00:00'),
(4, 22.0, 99.5, -48.0, '2026-06-21 12:01:00');
