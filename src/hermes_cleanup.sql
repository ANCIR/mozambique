
SELECT f_add_col('hermes_company', 'nome_da_entidade_norm', 'text');
UPDATE hermes_company SET nome_da_entidade_norm = f_mz_company(nome_da_entidade);
