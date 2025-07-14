export $(shell cat .env | grep -v '^#' | xargs)

dbt-debug:
	dbt debug --project-dir dbt/telepharm_dbt --profiles-dir dbt

dbt-run:
	dbt run --project-dir dbt/telepharm_dbt --profiles-dir dbt
dbt-test:
	dbt test --project-dir dbt/telepharm_dbt --profiles-dir dbt
dbt-doc-generate:
	dbt docs generate --project-dir dbt/telepharm_dbt --profiles-dir dbt
dbt-doc-serve:
	dbt docs serve --project-dir dbt/telepharm_dbt --profiles-dir dbt
