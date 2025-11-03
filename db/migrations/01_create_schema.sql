-- ================================
-- ESQUEMA DE BASE DE DATOS AMA BOT
-- ================================

-- 1. TABLA DE USUARIOS
-- Contiene información básica de cada usuario
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    number VARCHAR(15) PRIMARY KEY,
    location VARCHAR(50) NOT NULL,
    location_name VARCHAR(100) NOT NULL,
    salon VARCHAR(50),
    city VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para consultas frecuentes
CREATE INDEX idx_users_city ON users(city);
CREATE INDEX idx_users_location ON users(location, location_name);

-- 2. TABLAS DE SESIONES (1 a 6)
-- Cada tabla almacena el progreso por día de una sesión específica

-- SESIÓN 1
DROP TABLE IF EXISTS session_1 CASCADE;
CREATE TABLE session_1 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_1_number ON session_1(number);

-- SESIÓN 2
DROP TABLE IF EXISTS session_2 CASCADE;
CREATE TABLE session_2 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_2_number ON session_2(number);

-- SESIÓN 3
DROP TABLE IF EXISTS session_3 CASCADE;
CREATE TABLE session_3 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_3_number ON session_3(number);

-- SESIÓN 4
DROP TABLE IF EXISTS session_4 CASCADE;
CREATE TABLE session_4 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_4_number ON session_4(number);

-- SESIÓN 5
DROP TABLE IF EXISTS session_5 CASCADE;
CREATE TABLE session_5 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_5_number ON session_5(number);

-- SESIÓN 6
DROP TABLE IF EXISTS session_6 CASCADE;
CREATE TABLE session_6 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_6_number ON session_6(number);

-- 3. FUNCIONES AUXILIARES
-- Función para actualizar timestamp automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 4. TRIGGERS PARA ACTUALIZAR TIMESTAMPS
-- Trigger para tabla users
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Triggers para tablas de sesiones
DROP TRIGGER IF EXISTS update_session_1_updated_at ON session_1;
CREATE TRIGGER update_session_1_updated_at 
    BEFORE UPDATE ON session_1 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_2_updated_at ON session_2;
CREATE TRIGGER update_session_2_updated_at 
    BEFORE UPDATE ON session_2 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_3_updated_at ON session_3;
CREATE TRIGGER update_session_3_updated_at 
    BEFORE UPDATE ON session_3 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_4_updated_at ON session_4;
CREATE TRIGGER update_session_4_updated_at 
    BEFORE UPDATE ON session_4 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_5_updated_at ON session_5;
CREATE TRIGGER update_session_5_updated_at 
    BEFORE UPDATE ON session_5 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_6_updated_at ON session_6;
CREATE TRIGGER update_session_6_updated_at 
    BEFORE UPDATE ON session_6 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 5. VISTAS PARA REPORTES
-- Vista para estadísticas por ciudad
CREATE OR REPLACE VIEW city_stats AS
SELECT 
    u.city,
    COUNT(*) as total_users,
    COUNT(CASE WHEN u.location = 'Colegio' THEN 1 END) as colegios,
    COUNT(CASE WHEN u.location = 'Barrio' THEN 1 END) as barrios
FROM users u
GROUP BY u.city;

-- Vista para progreso por ubicación
CREATE OR REPLACE VIEW location_progress AS
SELECT 
    u.location,
    u.location_name,
    u.city,
    COUNT(*) as total_users,
    -- Progreso en sesión 1
    COUNT(CASE WHEN s1.day_1 = 1 THEN 1 END) as completed_s1d1,
    COUNT(CASE WHEN s1.day_2 = 1 THEN 1 END) as completed_s1d2,
    COUNT(CASE WHEN s1.day_3 = 1 THEN 1 END) as completed_s1d3,
    COUNT(CASE WHEN s1.day_4 = 1 THEN 1 END) as completed_s1d4,
    COUNT(CASE WHEN s1.day_5 = 1 THEN 1 END) as completed_s1d5
FROM users u
LEFT JOIN session_1 s1 ON u.number = s1.number
GROUP BY u.location, u.location_name, u.city
ORDER BY u.city, u.location, u.location_name;

-- 6. COMENTARIOS DESCRIPTIVOS
COMMENT ON TABLE users IS 'Tabla principal con información básica de usuarios';
COMMENT ON COLUMN users.number IS 'Número de teléfono (ID principal)';
COMMENT ON COLUMN users.city IS 'Ciudad determinada por prefijo: 59=Lago Agrio, 51=Iquitos';

COMMENT ON TABLE session_1 IS 'Progreso por día en la sesión 1';
COMMENT ON TABLE session_2 IS 'Progreso por día en la sesión 2';
COMMENT ON TABLE session_3 IS 'Progreso por día en la sesión 3';
COMMENT ON TABLE session_4 IS 'Progreso por día en la sesión 4';
COMMENT ON TABLE session_5 IS 'Progreso por día en la sesión 5';
COMMENT ON TABLE session_6 IS 'Progreso por día en la sesión 6';

-- ================================
-- FIN DEL ESQUEMA
-- ================================