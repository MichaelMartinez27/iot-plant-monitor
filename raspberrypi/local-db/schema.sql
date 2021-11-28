-- sensor table
CREATE TABLE IF NOT EXISTS Sensor_data (
	data_id INTEGER PRIMARY KEY,
	plant_id TEXT NOT NULL,
	sensor_id TEXT,
	dt TEXT NOT NULL,
	type TEXT NOT NULL,
	value TEXT NOT NULL,
    unit TEXT NOT NULL
);

