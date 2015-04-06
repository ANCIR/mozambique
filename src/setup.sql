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


-- CREATE TABLE IF NOT EXISTS name_distances (
--     left_name VARCHAR NOT NULL,
--     right_name VARCHAR NOT NULL,
--     edit_dist INTEGER
-- );

-- DROP INDEX IF EXISTS left_name_distances;
-- DROP INDEX IF EXISTS right_name_distances;
-- DROP INDEX IF EXISTS all_name_distances;
-- CREATE INDEX left_name_distances ON name_distances (left_name);
-- CREATE INDEX right_name_distances ON name_distances (right_name);
-- CREATE INDEX all_name_distances ON name_distances (right_name, left_name, edit_dist);
