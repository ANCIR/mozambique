
-- DELETE FROM name_distances;

-- INSERT INTO name_distances (left_name, right_name)
--     SELECT DISTINCT fx.parties_norm, co.nome_da_entidade_norm
--     FROM hermes_company AS co, mz_flexicadastre fx
--     WHERE
--         co.nome_da_entidade_norm IS NOT NULL
--         AND fx.parties_norm IS NOT NULL;
