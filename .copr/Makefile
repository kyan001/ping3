srpm:
	dnf install python3-pip dnf5-plugins python3-setuptools python3-wheel
	dnf builddep python3-ping3.spec
	pip install build
	python3 -m build --sdist
	rpmbuild --ta dist/ping3-5.1.5.tar.gz --define "_srcrpmdir $(outdir)"
