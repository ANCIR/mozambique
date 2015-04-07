CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS unaccent; 

CREATE OR REPLACE function f_add_col(_tbl regclass, _col  text, _type regtype, OUT success bool)
    LANGUAGE plpgsql AS
$func$
BEGIN
    IF EXISTS (
       SELECT 1 FROM pg_attribute
       WHERE  attrelid = _tbl
       AND    attname = _col
       AND    NOT attisdropped) THEN
       success := FALSE;

    ELSE
       EXECUTE '
       ALTER TABLE ' || _tbl || ' ADD COLUMN ' || quote_ident(_col) || ' ' || _type;
       success := TRUE;
    END IF;
END
$func$;


CREATE OR REPLACE FUNCTION f_normtxt(t varchar) RETURNS varchar AS $$
  BEGIN
    RETURN LOWER(TRIM(UNACCENT(t)));
  END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION f_mz_company(t varchar) RETURNS varchar AS $$
  BEGIN
    RETURN TRIM(
      regexp_replace(
        regexp_replace(
          regexp_replace(
            regexp_replace(
              regexp_replace(
                f_normtxt(t),
                '\([0-9,\.]*%?\)', '', 'g'
              ),
              '\( ?(moz|mozambique|moc).?\)', '', 'g'
            ),
            '[, ]+(lda|ltd)\.?', ' limitada', 'g'
          ),
          '\W+', ' ', 'g'
        ),
        '\s+', ' ', 'g'
      )
    );
  END;
$$ LANGUAGE plpgsql;


CREATE OR REPLACE FUNCTION f_mz_person(t varchar) RETURNS varchar AS $$
  BEGIN
    RETURN TRIM(
      regexp_replace(
        regexp_replace(
          regexp_replace(
            f_normtxt(t),
            '\([0-9,\.]*%?\)', '', 'g'
          ),
          '\W+', ' ', 'g'
        ),
        '\s+', ' ', 'g'
      )
    );
  END;
$$ LANGUAGE plpgsql;




-- DROP TABLE IF EXISTS dedupe_company;
-- DROP TABLE IF EXISTS dedupe_person;

CREATE TABLE IF NOT EXISTS dedupe_company (
    name_plain VARCHAR NOT NULL,
    name_norm VARCHAR NOT NULL,
    source VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dedupe_person (
    name_plain VARCHAR NOT NULL,
    name_norm VARCHAR NOT NULL,
    source VARCHAR NOT NULL
);

DROP INDEX IF EXISTS dep_name_plain;
CREATE INDEX dep_name_plain ON dedupe_person (name_plain);

DROP INDEX IF EXISTS ded_name_plain;
CREATE INDEX ded_name_plain ON dedupe_company (name_plain);
