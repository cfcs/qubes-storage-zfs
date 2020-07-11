.PHONY: clean

clean:
	rm -fr dist/ build/ qubes_storage_zfs.egg-info/

dist: qubes_storage_zfs/* requirements.txt setup.py Makefile README.md
	make clean
	python3 setup.py sdist
	find dist/ -name '*.tar*'
