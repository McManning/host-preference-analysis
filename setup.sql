
-- Table for the subset of eBird observation data that intersects collection dates
CREATE TABLE bird_observations (
  global_unique_identifier TEXT,
  common_name TEXT,
  scientific_name TEXT,
  observation_count INTEGER,
  county TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  observation_date DATE
);

COPY bird_observations FROM '/data/ebird/trimmed.csv' DELIMITER ',' CSV HEADER;
-- 2,667,119 rows, imported in ~40s

-- PostGIS setup for sample coordinates
ALTER TABLE bird_observations ADD COLUMN location GEOGRAPHY(POINT, 4326);
UPDATE bird_observations SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
  -- ~55s

-- I should've added indexes to start but I didn't. So let's index geo data.
CREATE UNIQUE INDEX guid_index ON bird_observations (global_unique_identifier);
CREATE INDEX location_idx ON bird_observations USING GIST (location);

-- Alden's collection and sequencing data
CREATE TABLE collections (
  Collection_Date DATE,
  Season TEXT,
  Species_PCR_GR TEXT,
  Sequence_Results TEXT,
  latitude NUMERIC,
  longitude NUMERIC,
  Site_Name TEXT
);

COPY collections FROM '/data/collections.csv' DELIMITER ',' CSV HEADER;
-- 132

-- PostGIS setup for sample coordinates
ALTER TABLE collections ADD COLUMN location GEOGRAPHY(POINT, 4326);
UPDATE collections SET location = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);
CREATE INDEX collection_location_idx ON collections USING GIST (location);

-- Correct common name for a mislabeled bird in Alden's data
UPDATE collections SET sequence_results = 'European Starling' WHERE sequence_results = 'Common Starling'


-- I need to backfill Alden's seasons into eBird data for easy aggregating.
-- Should've done this during the Python preprocessing but... hindsight.
ALTER TABLE bird_observations ADD COLUMN season TEXT;

UPDATE bird_observations
SET season =
    CASE
        WHEN observation_date BETWEEN '2021-05-21' AND '2021-06-14' THEN 'Spring 2021'
        WHEN observation_date BETWEEN '2021-06-21' AND '2021-09-20' THEN 'Summer 2021'
        WHEN observation_date BETWEEN '2021-10-04' AND '2021-11-04' THEN 'Fall 2021'
        WHEN observation_date BETWEEN '2022-03-25' AND '2022-05-12' THEN 'Spring 2022'
        ELSE NULL
    END;

CREATE INDEX observation_season_idx ON bird_observations (season);
