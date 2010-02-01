#!/bin/bash

sed -i 's#^pyfile .*$##' conque_term.vim
echo "python << EOF" >> conque_term.vim
cat conque.py >> conque_term.vim
cat conque_subprocess.py >> conque_term.vim
cat conque_screen.py >> conque_term.vim
echo "EOF" >> conque_term.vim
echo "" >> conque_term.vim

sed -i 's#^.*logging.*$##' conque_term.vim
sed -i 's#^.*debug.*$##' conque_term.vim

