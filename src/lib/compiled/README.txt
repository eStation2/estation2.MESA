1. Modify the FrontUtils.cpp to match the correct header files (python-dev has to be installed)
2. Complile with: 
					gcc -c  -fPIC -I /usr/include/python2.7 FrontsUtils.cpp -o FrontsUtils.o
3. Create shared library with
					gcc FrontsUtils.o -shared -o FrontsUtils.so
