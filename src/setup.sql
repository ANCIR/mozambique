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
                RETURN f_normtxt(t);
        END;
$$ LANGUAGE plpgsql;



