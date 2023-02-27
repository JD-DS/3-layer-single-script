default:
	@cat makefile

view: test
	python db_viewer.py

init:
	python initialize_database.py

test:
	pytest -vvx db_viewer.py

clean:
	rm aquarium.db

clean_view: clean init view

test_smoke:
	pytest -k test_database_connect db_viewer.py