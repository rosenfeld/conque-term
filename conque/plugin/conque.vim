" FILE:     plugin/conque.vim
" AUTHOR:   Shougo Matsushita <Shougo.Matsu@gmail.com> (Original)
"           Nico Raffo <nicoraffo@gmail.com> (Modified)
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE: {{{
" Conque - pty interaction in Vim
" Copyright (C) 2009 Nico Raffo 
"
" This program is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
"
" This program is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with this program.  If not, see <http://www.gnu.org/licenses/>.
" }}}

if exists('g:loaded_conque') || v:version < 700
  finish
endif

command! -nargs=+ -complete=shellcmd Conque call conque#open(<q-args>)

let g:loaded_conque = 1

" vim: foldmethod=marker
