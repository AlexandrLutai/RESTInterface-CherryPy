CREATE TABLE IF NOT EXISTS equipment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_id INT NOT NULL,
    serial_number VARCHAR(255) NOT NULL UNIQUE,
    note TEXT,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (type_id) REFERENCES equipment_type(id) ON DELETE CASCADE
);