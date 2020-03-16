#
#	Contents of the directory (see also SDFD doc)
#

#	Definitions

set_env.sh: 		for configuring a BUILD machine (adds to /etc/var/sources.list.d), for example adding postgresql 9.3 repository and Ubuntu image to sources.list
config:			REPO dir definitions
list_amd64_2.0.txt	list for eStation 2.0

#	Retrieve packages (to be used on BUILD machine - vm26)

add-list-packages.sh: 	go through a list of packages and retrieves them
add-package.sh:		retrieves a single package.
			Either called by the add-list-packages.sh, or run with Package-Repository -> Package-Repository-manual
add-package-ppa.sh:	retrieves a single package from a ppa.
			Either called by the add-list-packages.sh, or run with Package-Repository -> Package-Repository-manual
update-repository.sh:	update repository package inxed
			Called by add-package[-ppa].sh

#	Install packages (to be used on TEST - or DEV - machine, namely vm22)

inst-list-packages.sh: 	go through a list of packages, download and install them
inst-package-ppa.sh:	retrieves and install a single package from a ppa.

#	Create a ISO

sync-cd-repository.sh:	update repository package inxed and rsync .deb to target dir (CD_BUILD_DIR)
sync-cd.sh:		update whole contents of $CD_BUILD_DIR (incl. command above)

create-cd-iso.sh: 	create the ISO file (mkisoft)


