

-- Exploring the data from FlexiCadastre a bit:
SELECT COUNT(*) FROM mz_todas_licencas_extinto;
-- 4170 - Does this table hold all licenses?

SELECT COUNT(*) FROM mz_licenca_de_reconhecimento;
-- 9
SELECT COUNT(*) FROM mz_licenca_de_prospeccao_e_pesquisa;
-- 1795
SELECT COUNT(*) FROM mz_contratos;
-- 5
SELECT COUNT(*) FROM mz_concessao_mineira;
-- 263
SELECT COUNT(*) FROM mz_certificado_mineiro;
-- 829
SELECT COUNT(*) FROM mz_blocos_de_hidrocarbonetos_em_vigor;
-- 12
SELECT COUNT(*) FROM mz_autorizacao_de_recursos_minerais_para_construcao;
-- 45

-- 9 + 1795 + 5 + 263 + 829 + 12 + 45 = 2958
-- does not seem to add up to 4170.

SELECT layer_name, COUNT(*)
    FROM mz_flexicadastre
    GROUP BY layer_name
    ORDER BY COUNT(*) DESC;


SELECT parties, COUNT(*)
    FROM mz_flexicadastre
    WHERE parties IS NOT NULL
    GROUP BY parties
    ORDER BY COUNT(*) DESC;
-- http://databin.pudo.org/t/d2ddf1

SELECT f_normtxt(parties), COUNT(*)
    FROM mz_flexicadastre
    WHERE parties IS NOT NULL
    GROUP BY f_normtxt(parties)
    ORDER BY COUNT(*) DESC;
-- no obvious difference



SELECT f_normtxt(nome_da_entidade), COUNT(*)
    FROM hermes_company
    WHERE nome_da_entidade IS NOT NULL
    GROUP BY f_normtxt(nome_da_entidade)
    ORDER BY COUNT(*) DESC;



SELECT COUNT(DISTINCT fx.parties_norm)
    FROM hermes_company AS co, mz_flexicadastre fx
    WHERE
        co.nome_da_entidade_norm IS NOT NULL
        AND fx.parties_norm IS NOT NULL
        AND co.nome_da_entidade_norm = fx.parties_norm;

SELECT COUNT(DISTINCT fx.parties_norm)
    FROM mz_flexicadastre fx
    WHERE
        fx.parties_norm IS NOT NULL;


SELECT fx.parties_norm, COUNT(fx.id)
    FROM hermes_company AS co, mz_flexicadastre fx
    WHERE
        co.nome_da_entidade_norm IS NOT NULL
        AND fx.parties_norm IS NOT NULL
        AND LEVENSHTEIN(co.nome_da_entidade_norm, fx.parties_norm) < 3
    GROUP BY fx.parties_norm
    ORDER BY COUNT(fx.id) DESC;


-- link PEPs to Hermes Relation

SELECT hr.target_name_norm, COUNT(*)
    FROM hermes_relation AS hr, pep pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND hr.target_name_norm = pe.full_name_norm
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(*) DESC;


SELECT COUNT(DISTINCT hr.target_name_norm)
    FROM hermes_relation AS hr, pep pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND hr.target_name_norm = pe.full_name_norm;


SELECT hr.target_name_norm, COUNT(*)
    FROM hermes_relation AS hr, pep pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(*) DESC;

SELECT COUNT(DISTINCT hr.target_name_norm)
    FROM hermes_relation AS hr, pep pe
    WHERE
        hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3;



SELECT hc.id_do_registo AS company_id,
    hc.nome_da_entidade AS company_name,
    hr.target_name AS company_person_name,
    pe.given_name AS pep_given_name,
    pe.family_name AS pep_family_name,
    pe.menbership_role AS pep_menbership_role,
    pe.organization_name AS pep_organization_name
    FROM hermes_company AS hc, hermes_relation AS hr, pep AS pe
    WHERE
        hc.id_do_registo = hr.id_do_registo
        AND hr.target_name_norm IS NOT NULL
        AND LENGTH(hr.target_name_norm) > 2
        AND hr.rel_key = 'socios_pessoas'
        AND pe.full_name_norm IS NOT NULL
        AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3;



SELECT fx.layer_name AS conc_layer_name,
       fx.name AS conc_name,
       fx.parties AS conc_parties,
       hc.id_do_registo AS company_id,
       hc.nome_da_entidade AS company_name,
       hr.target_name AS company_person_name,
       pe.given_name AS pep_given_name,
       pe.family_name AS pep_family_name,
       pe.menbership_role AS pep_menbership_role,
       pe.organization_name AS pep_organization_name
    FROM hermes_company AS hc, hermes_relation AS hr,
         pep AS pe, mz_flexicadastre AS fx
    WHERE hc.id_do_registo = hr.id_do_registo
       AND fx.parties_norm = hc.nome_da_entidade_norm
       AND hr.target_name_norm IS NOT NULL
       AND LENGTH(hr.target_name_norm) > 2
       AND hr.rel_key = 'socios_pessoas'
       AND pe.full_name_norm IS NOT NULL
       AND LEVENSHTEIN(hr.target_name_norm, pe.full_name_norm) < 3;




SELECT MAX(hc.nome_da_entidade) AS company_name, COUNT(DISTINCT hr.target_name_norm)
    FROM hermes_company AS hc, hermes_relation AS hr
    WHERE hc.nome_da_entidade IS NOT NULL
        AND hc.id_do_registo = hr.id_do_registo
    GROUP BY hc.nome_da_entidade_norm
    ORDER BY COUNT(DISTINCT hr.target_name_norm) DESC;

SELECT hc.id_do_registo,
        LEFT(MAX(hc.nome_da_entidade), 80) AS company_name,
        MIN(data_da_escritura),
        COUNT(DISTINCT hr.target_name_norm)
    FROM hermes_company AS hc, hermes_relation AS hr
    WHERE hc.nome_da_entidade IS NOT NULL
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hc.id_do_registo, hc.nome_da_entidade_norm
    ORDER BY COUNT(DISTINCT hr.target_name_norm) DESC;


SELECT COALESCE(data_de_assinatura, data_da_escritura), COUNT(*)
    FROM hermes_company
    GROUP BY COALESCE(data_de_assinatura, data_da_escritura)
    ORDER BY COUNT(*) DESC;


SELECT MAX(hr.target_name) AS name,
        COUNT(DISTINCT hc.nome_da_entidade_norm) AS companies
    FROM hermes_company AS hc, hermes_relation AS hr
    WHERE LENGTH(hr.target_name_norm) > 1
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(DISTINCT hc.nome_da_entidade_norm) DESC;



SELECT parties_norm, COUNT(*) FROM mz_flexicadastre
    WHERE parties_norm IS NOT NULL
    GROUP BY parties_norm
    ORDER BY COUNT(*) DESC;


SELECT MAX(hr.target_name) AS name,
        COUNT(DISTINCT hc.nome_da_entidade_norm) AS companies,
        COUNT(DISTINCT fx.id) AS concessions
    FROM hermes_company AS hc,
        hermes_relation AS hr,
        mz_flexicadastre AS fx
    WHERE fx.parties_norm = hc.nome_da_entidade_norm
        AND LENGTH(hr.target_name_norm) > 1
        AND hc.id_do_registo = hr.id_do_registo
        AND hr.rel_key = 'socios_pessoas'
    GROUP BY hr.target_name_norm
    ORDER BY COUNT(DISTINCT fx.id) DESC;



SELECT co.nome_da_entidade AS hermes_name,
        cc.cw_id AS id,
        cc.company_name AS filed_name,
        cp.company_name AS parent_company
    FROM
        hermes_company AS co, corpwatch_companies AS cc,
        corpwatch_company_relations AS cr, corpwatch_companies AS cp
    WHERE
        LENGTH(co.nome_da_entidade_norm) > 2
        AND co.nome_da_entidade_norm = cc.company_name_norm
        AND cr.target_cw_id = cc.cw_id
        AND cr.source_cw_id = cp.cw_id;
