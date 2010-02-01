#!/bin/bash

sed -i 's#^pyfile .*$##' autoload/conque_term.vim
echo "python << EOF" >> autoload/conque_term.vim
cat autoload/conque.py >> autoload/conque_term.vim
cat autoload/conque_subprocess.py >> autoload/conque_term.vim
cat autoload/conque_screen.py >> autoload/conque_term.vim
echo "EOF" >> autoload/conque_term.vim
echo "" >> autoload/conque_term.vim

sed -i 's#^.*logging.*$##' autoload/conque_term.vim
sed -i 's#^.*debug.*$##' autoload/conque_term.vim
sed -i 's#^.*LOG_FILENAME.*$##' autoload/conque_term.vim

