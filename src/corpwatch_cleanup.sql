
SELECT f_add_col('corpwatch_companies', 'company_name_norm', 'text');
UPDATE corpwatch_companies SET company_name_norm = f_mz_person(company_name);
