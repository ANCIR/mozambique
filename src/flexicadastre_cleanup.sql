
SELECT f_add_col('mz_flexicadastre', 'parties_norm', 'text');
UPDATE mz_flexicadastre SET parties_norm = f_mz_company(parties);

