
SELECT f_add_col('pep', 'full_name_norm', 'text');
UPDATE pep SET full_name_norm = f_mz_person(full_name);
