#!/bin/bash

# Config .rpmmacros
echo '%_topdir /rpm/rpmbuild/' > ~.rpmmacros
echo '%_bindir /rpm/rpmbuild/BUILD/' >> ~.rpmmacros

# Create the Local Dirs for source code of the 3 packages
mkdir -p ~/rpms/eStation-Apps
mkdir -p ~/rpms/eStation-Docs
mkdir -p ~/rpms/eStation-Layers






