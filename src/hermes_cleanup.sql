
SELECT f_add_col('hermes_company', 'nome_da_entidade_norm', 'text');
UPDATE hermes_company SET nome_da_entidade_norm = f_mz_company(nome_da_entidade);


SELECT f_add_col('hermes_relation', 'target_name_norm', 'text');
UPDATE hermes_relation
    SET target_name_norm = f_mz_company(target_name)
    WHERE rel_key = 'socios_instituicoes';
UPDATE hermes_relation
    SET target_name_norm = f_mz_person(target_name)
    WHERE rel_key = 'socios_pessoas';
UPDATE hermes_relation
    SET target_name_norm = normtxt(target_name)
    WHERE rel_key = 'lugar_da_sede';
