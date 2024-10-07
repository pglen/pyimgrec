#!/bin/bash
for c in $(ls -1 /usr/bin/*gcc.exe); do
    echo "=== compiler:      $c"
    $c -o hello.exe hello.c
    #objdump -p hello.exe | grep -i "cygwin"
	echo -n "    "
    objdump -p hello.exe | grep -i "file format"
    rm hello.exe
done