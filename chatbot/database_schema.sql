-- Irado Bedrijfsklanten Database Schema
-- Migratie van KOAD CSV naar PostgreSQL database

-- Tabel voor bedrijfsklanten (voormalig KOAD blacklist)
CREATE TABLE IF NOT EXISTS bedrijfsklanten (
    id SERIAL PRIMARY KEY,
    koad_nummer VARCHAR(20) UNIQUE,
    straat VARCHAR(255),
    postcode VARCHAR(10),
    huisnummer VARCHAR(20),
    huisnummer_toevoeging VARCHAR(10),
    etage VARCHAR(50),
    naam VARCHAR(255),
    actief BOOLEAN DEFAULT true,
    inwoner BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index voor snelle zoekopdrachten op postcode + huisnummer
CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_postcode_huisnummer 
ON bedrijfsklanten(postcode, huisnummer);

-- Index voor zoeken op naam
CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_naam 
ON bedrijfsklanten(naam);

-- Index voor actieve klanten
CREATE INDEX IF NOT EXISTS idx_bedrijfsklanten_actief 
ON bedrijfsklanten(actief) WHERE actief = true;

-- Functie om automatisch updated_at te updaten
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger voor updated_at
CREATE TRIGGER update_bedrijfsklanten_updated_at 
    BEFORE UPDATE ON bedrijfsklanten 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Tabel voor CSV upload historie
CREATE TABLE IF NOT EXISTS csv_uploads (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    records_imported INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_deleted INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    error_message TEXT
);

-- Functie om alle bedrijfsklanten te verwijderen (voor CSV overschrijving)
CREATE OR REPLACE FUNCTION clear_all_bedrijfsklanten()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM bedrijfsklanten;
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Functie om te controleren of een adres een bedrijfsklant is
CREATE OR REPLACE FUNCTION is_bedrijfsklant(
    p_postcode VARCHAR(10),
    p_huisnummer VARCHAR(20)
)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM bedrijfsklanten 
        WHERE postcode = UPPER(TRIM(p_postcode)) 
        AND huisnummer = TRIM(p_huisnummer)
        AND actief = true
    );
END;
$$ LANGUAGE plpgsql;

-- Functie om bedrijfsklant details op te halen
CREATE OR REPLACE FUNCTION get_bedrijfsklant_info(
    p_postcode VARCHAR(10),
    p_huisnummer VARCHAR(20)
)
RETURNS TABLE (
    koad_nummer VARCHAR(20),
    straat VARCHAR(255),
    naam VARCHAR(255),
    actief BOOLEAN
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        b.koad_nummer,
        b.straat,
        b.naam,
        b.actief
    FROM bedrijfsklanten b
    WHERE b.postcode = UPPER(TRIM(p_postcode)) 
    AND b.huisnummer = TRIM(p_huisnummer)
    AND b.actief = true;
END;
$$ LANGUAGE plpgsql;

-- View voor dashboard statistieken
CREATE OR REPLACE VIEW bedrijfsklanten_stats AS
SELECT 
    COUNT(*) as totaal_klanten,
    COUNT(*) FILTER (WHERE actief = true) as actieve_klanten,
    COUNT(*) FILTER (WHERE actief = false) as inactieve_klanten,
    COUNT(DISTINCT postcode) as unieke_postcodes,
    COUNT(DISTINCT straat) as unieke_straten,
    MAX(created_at) as laatste_toevoeging,
    MAX(updated_at) as laatste_update
FROM bedrijfsklanten;

-- Comments voor documentatie
COMMENT ON TABLE bedrijfsklanten IS 'Tabel voor bedrijfsklanten (voormalig KOAD blacklist)';
COMMENT ON COLUMN bedrijfsklanten.koad_nummer IS 'Uniek KOAD nummer van de bedrijfsklant';
COMMENT ON COLUMN bedrijfsklanten.actief IS 'Of de bedrijfsklant actief is (true = geblokkeerd voor particuliere service)';
COMMENT ON COLUMN bedrijfsklanten.inwoner IS 'Of het een inwoner betreft';

COMMENT ON TABLE csv_uploads IS 'Historie van CSV uploads voor audit trail';
COMMENT ON COLUMN csv_uploads.records_imported IS 'Aantal records geïmporteerd bij deze upload';
COMMENT ON COLUMN csv_uploads.records_updated IS 'Aantal records bijgewerkt bij deze upload';
COMMENT ON COLUMN csv_uploads.records_deleted IS 'Aantal records verwijderd bij deze upload';





