# Assignment 4 –Molecule Webserver Application

## Executing program
- Compiling the program:
1. Run export LD_LIBRARY_PATH=$LD_LIBRARY_PATH: into the command line
```
> export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:
```
2. run make into the command line
```
> make
```
* Expected output:
```
clang -Wall -std=c99 -pedantic -c mol.c -fPIC -o mol.o
clang mol.o -shared -o libmol.so
swig3.0 -python molecule.i
clang -Wall -std=c99 -pedantic -c molecule_wrap.c -I /usr/include/python3.7m -fPIC -o molecule_wrap.o
clang -Wall -std=c99 -pedantic -shared molecule_wrap.o -L. -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -lpython3.7 -lmol -dynamiclib -o _molecule.so
clang: warning: argument unused during compilation: '-dynamiclib' [-Wunused-command-line-argument]
python3 molsql.py
```
- Running Server
```
> python3 server.py 56760
```

## Accessing server locally:
- Type http://localhost:56760/home_page.html into local browser


## Author Information
- Name: Derek Duong
- Email: dduong03@uoguelph.ca
- Student ID: 1186760

