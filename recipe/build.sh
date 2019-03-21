#!/bin/bash

# LIBVERSION shall only include MAJOR.MINOR.PATCH for require
LIBVERSION=$(echo ${PKG_VERSION}| cut -d'.' -f1-3)

# Clean between variants builds
make clean

make MODULE=${PKG_NAME} LIBVERSION=${LIBVERSION}
make MODULE=${PKG_NAME} LIBVERSION=${LIBVERSION} db
make MODULE=${PKG_NAME} LIBVERSION=${LIBVERSION} install

