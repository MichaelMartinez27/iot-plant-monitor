-- sensor table
CREATE TABLE IF NOT EXISTS Sensor_data (
	data_id INTEGER PRIMARY KEY,
	plant_id TEXT NOT NULL,
	sensor_id TEXT,
	dt TEXT NOT NULL,
	value REAL NOT NULL,
    type TEXT NOT NULL
);

