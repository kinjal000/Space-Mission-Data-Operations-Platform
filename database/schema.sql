-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

-- Create satellites table
CREATE TABLE IF NOT EXISTS satellites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    launch_date TEXT NOT NULL,
    orbit_type TEXT NOT NULL,
    status TEXT CHECK( status IN ('Active', 'Inactive') ) NOT NULL
);

-- Create missions table
CREATE TABLE IF NOT EXISTS missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    target TEXT NOT NULL,
    start_date TEXT NOT NULL,
    status TEXT CHECK( status IN ('Planning', 'Active', 'Completed', 'Failed') ) NOT NULL
);

-- Create telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    satellite_id INTEGER NOT NULL,
    temperature REAL NOT NULL,
    battery_level REAL NOT NULL,
    signal_strength REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (satellite_id) REFERENCES satellites(id) ON DELETE CASCADE
);
