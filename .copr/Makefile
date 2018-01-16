srpm:
	rm -rf .srpm/custodia-0.5.0
	mkdir -p .srpm/custodia-0.5.0
	cp -rp * .srpm/custodia-0.5.0
	( cd .srpm && tar cf ../custodia-0.5.0.tar.gz custodia-0.5.0 )
	rm -rf .srpm/custodia-0.5.0
	sha512sum custodia-0.5.0.tar.gz > custodia-0.5.0.tar.gz.sha512sum.txt
	rpmbuild -bs custodia.spec --define "_sourcedir ." --define "_srcrpmdir $(outdir)"
