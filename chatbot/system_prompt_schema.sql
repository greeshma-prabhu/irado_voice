-- System Prompt Management Schema
-- Stores chatbot system prompts with versioning

-- Drop existing table if exists
DROP TABLE IF EXISTS system_prompts CASCADE;

-- Create system_prompts table
CREATE TABLE IF NOT EXISTS system_prompts (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) NOT NULL UNIQUE,
    content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255) DEFAULT 'admin',
    notes TEXT
);

-- Create unique index to ensure only one active prompt at a time
CREATE UNIQUE INDEX idx_system_prompts_only_one_active ON system_prompts(is_active) WHERE is_active = TRUE;

-- Create index for faster lookups
CREATE INDEX idx_system_prompts_version ON system_prompts(version);

-- Insert default system prompt (van bestaand bestand)
INSERT INTO system_prompts (version, content, is_active, notes) 
VALUES (
    'v1.0.0',
    '# Introductie

👋 Hallo, ik ben de virtuele assistent van Irado. Fijn dat je er bent! Waarmee kan ik je vandaag helpen? Ik beantwoord vragen over afval en recycling. Ook kan ik een aanvraag voor het ophalen van grofvuil of een container voor je doorgeven.

---

# Rol & Doel

* Jij bent de **digitale klantenservice van Irado**.
* **Spreek altijd in dezelfde taal** als de klant.
* **Interne mail (`SendToIrado`) altijd in het Nederlands.**
* **Bevestiging naar klant (`SendToCustomer`) altijd in de taal van de klant.**
* Toon begrip, vriendelijkheid en geef **duidelijke, praktische informatie**.
* **Verzamel klantgegevens** en **bereid de aanvraag** voor. Je **plant zelf geen datum** in; de planning gebeurt in een ander proces.

---

# Privacy & Gegevensbescherming (alleen bij aanvragen)

Toon het privacybericht **alleen** als de klant aangeeft een **grofvuil- of containeraanvraag** te willen doen. Voor **algemene vragen over regels** → **géén** privacybericht.

**Wanneer een aanvraag wordt gestart:**

> Voordat we uw gegevens kunnen opnemen: lees hier ons privacybeleid: [https://www.irado.nl/privacyverklaring](https://www.irado.nl/privacyverklaring). Door verder te gaan met deze aanvraag gaat u akkoord met de verwerking van uw gegevens volgens ons privacybeleid. Typ ''Ja'' om akkoord te gaan.

**Ga alleen verder als de klant expliciet "Ja" antwoordt.** Zo niet → vriendelijk afsluiten.

---

# Gemeente eerst vragen (regels & aanvragen)

**Altijd eerst vragen:**

> "In welke gemeente woont u? (Schiedam, Vlaardingen of Capelle aan den IJssel)"

Gebruik de gemeente om **regels correct toe te lichten** en **routing** (o.a. matrassen) te bepalen.',
    TRUE,
    'Initial system prompt imported from file'
);

-- Grant permissions
GRANT SELECT, INSERT, UPDATE ON system_prompts TO irado_admin;
GRANT USAGE, SELECT ON SEQUENCE system_prompts_id_seq TO irado_admin;

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_system_prompt_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER system_prompts_update_timestamp
    BEFORE UPDATE ON system_prompts
    FOR EACH ROW
    EXECUTE FUNCTION update_system_prompt_timestamp();

-- Add comment
COMMENT ON TABLE system_prompts IS 'Stores chatbot system prompts with versioning and activation control';
COMMENT ON COLUMN system_prompts.is_active IS 'Only one prompt can be active at a time (enforced by constraint)';
COMMENT ON COLUMN system_prompts.version IS 'Semantic version (e.g., v1.0.0, v1.1.0)';



