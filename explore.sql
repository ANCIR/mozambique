

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





