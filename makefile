py=.venv/bin/python
pip=.venv/bin/pip
user=guenthner
program-name=messthaler-wulff

install_dependencies:
	python3 -m venv .venv
	$(py) -m pip install --upgrade pip
	$(pip) install build hatchling twine colorama pytest hypothesis pdoc

test:
	$(py) -m pytest $(args)

set_user:
	cp ~/.pypirc_$(user) ~/.pypirc

build: version
	HATCH_BUILD_CLEAN=true $(py) -m build

version:
	vinc

upload: set_user build
	$(py) -m twine upload --repository pypi dist/*

reload: upload
	pipx upgrade $(program-name)
	pipx upgrade $(program-name)
	$(program-name) --version

latex/README.tex: README.md latex/packages.tex
	pandoc -f markdown -t latex --standalone README.md -o latex/README.tex -H latex/packages.tex

latex/README.pdf: latex/README.tex
	cd latex && texfot pdflatex -synctex=1 -interaction=nonstopmode "README.tex"

documentation:
	$(py) -m pdoc -o documentation --math --search messthaler_wulff/

show_documentation:
	.venv/bin/python -m pdoc messthaler_wulff/ --search --math