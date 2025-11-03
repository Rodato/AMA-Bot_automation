-- ================================
-- AGREGAR SESIONES 7, 8 y 9
-- ================================

-- SESIÓN 7
DROP TABLE IF EXISTS session_7 CASCADE;
CREATE TABLE session_7 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_7_number ON session_7(number);

-- SESIÓN 8
DROP TABLE IF EXISTS session_8 CASCADE;
CREATE TABLE session_8 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_8_number ON session_8(number);

-- SESIÓN 9
DROP TABLE IF EXISTS session_9 CASCADE;
CREATE TABLE session_9 (
    number VARCHAR(15) PRIMARY KEY,
    day_1 SMALLINT DEFAULT 0 CHECK (day_1 IN (0, 1)),
    day_2 SMALLINT DEFAULT 0 CHECK (day_2 IN (0, 1)),
    day_3 SMALLINT DEFAULT 0 CHECK (day_3 IN (0, 1)),
    day_4 SMALLINT DEFAULT 0 CHECK (day_4 IN (0, 1)),
    day_5 SMALLINT DEFAULT 0 CHECK (day_5 IN (0, 1)),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (number) REFERENCES users(number) ON DELETE CASCADE
);
CREATE INDEX idx_session_9_number ON session_9(number);

-- TRIGGERS PARA ACTUALIZAR TIMESTAMPS
DROP TRIGGER IF EXISTS update_session_7_updated_at ON session_7;
CREATE TRIGGER update_session_7_updated_at 
    BEFORE UPDATE ON session_7 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_8_updated_at ON session_8;
CREATE TRIGGER update_session_8_updated_at 
    BEFORE UPDATE ON session_8 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_session_9_updated_at ON session_9;
CREATE TRIGGER update_session_9_updated_at 
    BEFORE UPDATE ON session_9 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- COMENTARIOS
COMMENT ON TABLE session_7 IS 'Progreso por día en la sesión 7';
COMMENT ON TABLE session_8 IS 'Progreso por día en la sesión 8';
COMMENT ON TABLE session_9 IS 'Progreso por día en la sesión 9';

-- ================================
-- FIN SESIONES ADICIONALES
-- ================================