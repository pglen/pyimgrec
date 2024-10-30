# Make image recognition libraries


all-am:
	make -C imgrec

clean:
	make -C imgrec clean

git:
	git add .
	git commit -m "Auto"
	git push

XPATH=python3 -W ignore::DeprecationWarning `which pdoc` --force --html

help:
	@echo "Targets: pydocs clean git"

#.PHONY: docs
#@echo "pydocs"

pydocs:
	@echo ${XPATH}
	@${XPATH} -o docs algorithm/flood.py

# EOF
