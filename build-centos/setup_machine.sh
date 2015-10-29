#!/bin/bash

# Config .rpmmacros
echo '%_topdir /rpm/rpmbuild/' > ~.rpmmacros
echo '%_bindir /rpm/rpmbuild/BUILD/' >> ~.rpmmacros

# Create the Local Dirs for source code of the 3 packages
mkdir -p ~/rpms/Apps
mkdir -p ~/rpms/Docs
mkdir -p ~/rpms/Layers






