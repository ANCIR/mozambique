
INSERT INTO dedupe_company (name_plain, name_norm, source)
    SELECT DISTINCT fx.parties, f_mz_company(fx.parties), 'flexicadastre'
        FROM mz_flexicadastre fx
        WHERE NOT EXISTS 
            (SELECT dc.name_plain FROM dedupe_company dc WHERE dc.name_plain = fx.parties)
            AND LENGTH(fx.parties) > 2;

INSERT INTO dedupe_company (name_plain, name_norm, source)
    SELECT DISTINCT hc.nome_da_entidade, f_mz_company(hc.nome_da_entidade), 'hermes'
        FROM hermes_company hc
        WHERE NOT EXISTS 
            (SELECT dc.name_plain FROM dedupe_company dc WHERE dc.name_plain = hc.nome_da_entidade)
            AND LENGTH(hc.nome_da_entidade) > 2;

INSERT INTO dedupe_person (name_plain, name_norm, source)
    SELECT DISTINCT pe.full_name, f_mz_person(pe.full_name), 'pep'
        FROM pep pe
        WHERE NOT EXISTS 
            (SELECT dp.name_plain FROM dedupe_person dp WHERE dp.name_plain = pe.full_name)
            AND LENGTH(pe.full_name) > 2;

INSERT INTO dedupe_person (name_plain, name_norm, source)
    SELECT DISTINCT hr.target_name, f_mz_person(hr.target_name), 'hermes'
        FROM hermes_relation hr
        WHERE NOT EXISTS 
            (SELECT dp.name_plain FROM dedupe_person dp WHERE dp.name_plain = hr.target_name)
            AND hr.rel_key = 'socios_pessoas'
            AND LENGTH(hr.target_name) > 2;

