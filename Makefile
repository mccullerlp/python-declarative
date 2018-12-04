
#mainly just recipes to help distribution
.PHONY: git-package

git-package:
	mkdir -p dist
	git archive --format=tar.gz master -o dist/IIRrational-`git describe --abbrev=0 --tags`.tar.gz

