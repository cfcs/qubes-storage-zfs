
dist: qubes_storage_zfs/* requirements.txt setup.py Makefile README.md
	rm -rf dist/
	python3 setup.py sdist
	find dist/ -name '*.tar*'
