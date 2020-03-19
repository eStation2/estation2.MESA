TODO
The C extension FrontUtils.cpp is not compatible for Pyhton 3
Rewrite the code.
Tutotials:
http://python3porting.com/cextensions.html
https://py3c.readthedocs.io/en/latest/guide.html

1. Modify the FrontUtils.cpp to match the correct header files (python-dev has to be installed)
Header files for Python 2.7:
    #include "/usr/include/python2.7/Python.h"
    #include "/usr/include/python2.7/pyconfig.h"
    #include "/usr/share/pyshared/numpy/core/include/numpy/arrayobject.h"

Header files for Python 3.6 (in ubuntu 18.04):
    #include "/usr/include/python3.6/Python.h"
    #include "/usr/include/python3.6/pyconfig.h"
    #include "/usr/local/lib/python3.6/dist-packages/numpy/core/include/numpy/arrayobject.h"

2. Complile for Python 2.7 with:
        gcc -c -fPIC -I /usr/include/python2.7 FrontsUtils.cpp -o FrontsUtils.o

   Complile for Python 3.6 with:
        gcc -c -fPIC -I /usr/include/python3.6 FrontsUtils.cpp -o FrontsUtils.o

3. Create shared library with
        gcc FrontsUtils.o -shared -o FrontsUtils.so
