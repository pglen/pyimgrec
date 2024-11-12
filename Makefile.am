# Makefile for image recognition libraries

all-am:
	make -C imgrec

clean:
	@make -C imgrec clean
	@rm -rf __pycache__
	@rm -f *~

git:
	git add .
	git commit -m "Auto"
	git push

help:
	@echo "Targets: pydocs clean git pydocs cycle"

XPATH=python3 -W ignore::DeprecationWarning `which pdoc` --force --html

pydocs:
	@#echo ${XPATH}
	@${XPATH} -o docs algorithm/flood.py
	@${XPATH} -o docs algorithm/norm_outline.py
	@${XPATH} -o docs pyimgutils.py
	@${XPATH} -o docs pyimgrec.py

cycle:
	@make -C imgrec
	@./pyimgrec.py

# EOF
