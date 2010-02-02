" FILE:     plugin/conque_term.vim {{{
" AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE:
" Conque - pty interaction in Vim
" Copyright (C) 2009-2010 Nico Raffo 
"
" MIT License
" 
" Permission is hereby granted, free of charge, to any person obtaining a copy
" of this software and associated documentation files (the "Software"), to deal
" in the Software without restriction, including without limitation the rights
" to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
" copies of the Software, and to permit persons to whom the Software is
" furnished to do so, subject to the following conditions:
" 
" The above copyright notice and this permission notice shall be included in
" all copies or substantial portions of the Software.
" 
" THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
" IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
" FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
" AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
" LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
" OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
" THE SOFTWARE.
" }}}

if exists('g:ConqueTerm_Loaded') || v:version < 700
    finish
endif

" **********************************************************************************************************
" **** DOCS ************************************************************************************************
" **********************************************************************************************************

" Usage {{{
"
" Type :ConqueTerm <command> to launch an application in the current buffer. E.g.
" 
"   :ConqueTerm bash
"   :ConqueTerm mysql -h localhost -u joe_lunchbox Menu
"   :ConqueTerm man top
"
" Keys pressed in insert mode will be sent to the shell, along with output from put commands.
"
" Press <F9> in any buffer to send a visual selection to the shell.
"
" Press the <Esc> key twice to send a single <Esc> to the shell. Pressing this key once will leave insert mode like normal.
"
" }}}

" Options {{{
"
" Set the following in your .vimrc (default values shown)
"
"   " Enable colors. Setting this to 0 will make your terminal faster.
"   let g:ConqueTerm_Color = 1
"
"   " Set your terminal type. I strong recommend leaving this as vt100, however more features may be enabled with xterm.
"   let g:ConqueTerm_TERM = 'vt100'
"
"   " Set buffer syntax. Conque has highlighting for MySQL, but not much else.
"   let g:ConqueTerm_Syntax = 'conque'
"
"   " Continue updating shell when it's not the current, focused buffer
"   let g:ConqueTerm_ReadUnfocused = 1
"
" }}}

" Minimum Requirements {{{
"   - Vim 7.1
"   - Python 2.3
"   - Supported operating systems: *nix, Mac, or Cygwin, anything with python pty module (Not Windows)
"
"     Tested on:
"      - Vim 7.2 / Python 2.6 / Ubuntu 9.10 (Gnome & GTK)
"      - Vim 7.2 / Python 2.6 / FreeBSD 8.0 (GTK)
"      - Vim 7.1 / Python 2.6 / FreeBSD 8.0 (GTK)
"      x Vim 7.0 / Python 2.6 / FreeBSD 8.0 (GTK)
"          * feedkeys() doesn't restart updatetime
"      - Vim 7.2 / Python 2.4 / OpenSolaris 2009.06 (Gnome)
"      - Vim 7.2 / Python 2.4 / CentOS 5.3 (no GUI)
"      - Vim 7.1 / Python 2.3 / RHEL 4 (no GUI)
"      - Vim 7.2 / Python 2.5 / Cygwin (Windows Vista 64b)
"      - MacVim 7.2 / Python 2.3 / OS X 10.6.2
" }}}

" Known bugs {{{
"
"  * Font/color highlighting is imperfect and slow. If you don't care about color in your shell, set g:ConqueTerm_Color = 0 in your .vimrc
"  * Conque only supports the extended ASCII character set for input.
"  * VT100 escape sequence support is not complete.
"  * Alt/Meta key support in Vim isn't great in general, and conque is no exception. Pressing <Esc><Esc>x or <Esc><M-x> instead of <M-x> works in most cases.
"
" }}}

" Todo {{{
"
"  * Fix pasting from named registers
"  * Polling unfucused conque buffers (Top explodes when window resizes)
"  * Enable graphics character set
"  * Consider supporting xterm escapes
"  * Improve color logic
"  * Find a graceful solution to UTF-8 input (impossible without mapping each key?)
"  * Find a graceful solution to Meta key input
"  * Find a graceful alternative to updatetime polling
"  * Windows support (See PyConsole http://www.vim.org/scripts/script.php?script_id=1974)
"
" }}}

" Contribute {{{
"
" The two contributions most in need are improvements to Vim itself. I currently use hacks to simulate 
" a key press event and repeating CursorHold event. The Vim todo.txt document lists proposed improvements to 
" give users this behavior without hacks. Having a key press event should allow Conque to work with multi-byte
" input. If you are a Vim developer, please consider prioritizing these two items:
"
"   * todo.txt (Autocommands, line ~3137)
"       8   Add an event like CursorHold that is triggered repeatedly, not just once
"           after typing something.
"
"   * todo.txt (Autocommands, proposed event list, line ~3189)
"       InsertCharPre   - user typed character Insert mode, before inserting the
"           char.  Pattern is matched with text before the cursor.
"           Set v:char to the character, can be changed.
"           (not triggered when 'paste' is set).
" 
" Bugs, suggestions and patches are all welcome.
"
" Get the developement source code at http://conque.googlecode.com or email nicoraffo@gmail.com
"
" }}}

" **********************************************************************************************************
" **** CONFIG **********************************************************************************************
" **********************************************************************************************************

" Enable color {{{
if !exists('g:ConqueTerm_Color')
    let g:ConqueTerm_Color = 1
endif " }}}

" TERM environment setting {{{
if !exists('g:ConqueTerm_TERM')
    let g:ConqueTerm_TERM =  'vt100'
endif " }}}

" Syntax for your buffer {{{
if !exists('g:ConqueTerm_Syntax')
    let g:ConqueTerm_Syntax = 'conque_term'
endif " }}}

" Read when unfocused {{{
if !exists('g:ConqueTerm_ReadUnfocused')
    let g:ConqueTerm_ReadUnfocused = 1
endif " }}}

" Use this regular expression to highlight prompt {{{
if !exists('g:ConqueTerm_PromptRegex')
    let g:ConqueTerm_PromptRegex = '^\w\+@[0-9A-Za-z_.-]\+:[0-9A-Za-z_./\~,:-]\+\$'
endif " }}}

" **********************************************************************************************************
" **** Startup *********************************************************************************************
" **********************************************************************************************************

" Startup {{{
setlocal encoding=utf-8

let g:ConqueTerm_Loaded = 1
let g:ConqueTerm_Idx = 1

command! -nargs=+ -complete=shellcmd ConqueTerm call conque_term#open(<q-args>)
command! -nargs=+ -complete=shellcmd ConqueTermSplit call conque_term#open(<q-args>, ['split'])
command! -nargs=+ -complete=shellcmd ConqueTermVSplit call conque_term#open(<q-args>, ['vsplit'])

" }}}

