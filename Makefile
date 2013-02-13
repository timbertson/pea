0:
	mkzero-gfxmonk -p pea -p setup.py python-pea.xml

python-pea-local.xml: python-pea.xml
	0local python-pea.xml

local: python-pea-local.xml
	0install run python-pea-local.xml

test: python-pea-local.xml
	0install run --command=test python-pea-local.xml

test-all: python-pea-local.xml
	0test python-pea-local.xml http://repo.roscidus.com/python/python 2.6,2.8 3.0,4

