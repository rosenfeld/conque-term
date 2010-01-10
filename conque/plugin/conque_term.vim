" FILE:     plugin/conque_term.vim
" AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE: {{{
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

" Startup {{{
if exists('g:ConqueTerm_Loaded') || v:version < 700
    finish
endif

setlocal encoding=utf-8

let g:ConqueTerm_Loaded = 1
let g:ConqueTerm_Idx = 1

command! -nargs=+ -complete=shellcmd ConqueTerm call conque_term#open(<q-args>)

pyfile ~/.vim/plugin/conque.py
pyfile ~/.vim/plugin/conque_subprocess.py
pyfile ~/.vim/plugin/conque_screen.py
" }}}

" Open a command in Conque.
" This is the root function that is called from Vim to start up Conque.
function! conque_term#open(...) "{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])

    " bare minimum validation {{{
    if empty(command)
        echohl WarningMsg | echomsg "No command found" | echohl None
        return 0
    else
        let l:cargs = split(command, '\s')
        if !executable(l:cargs[0])
            echohl WarningMsg | echomsg "Not an executable" | echohl None
            return 0
        endif
    endif " }}}

    " configure shell buffer display and key mappings
    call conque_term#set_buffer_settings(command, hooks)

    let b:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx

    " open command {{{
    "try
        execute 'python ' . b:ConqueTerm_Var . ' = Conque()'
        execute "python " . b:ConqueTerm_Var . ".open('" . conque_term#python_escape(command) . "')"
    "catch 
    "    echohl WarningMsg | echomsg "Unable to open command: " . command | echohl None
    "    return 0
    "endtry " }}}

    call conque_term#set_mappings()

    let g:ConqueTerm_Idx += 1

    execute 'python ' . b:ConqueTerm_Var . '.read(500)'

    "startinsert!
    return 1
endfunction "}}}

" buffer settings, layout, key mappings, and auto commands
function! conque_term#set_buffer_settings(command, pre_hooks) "{{{
    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        silent execute h
    endfor

    " buffer settings 
    silent execute "edit " . substitute(a:command, ' ', '\\ ', 'g') . "\\ -\\ " . g:Conque_Idx
    setlocal buftype=nofile  " this buffer is not a file, you can't save it
    setlocal nonumber        " hide line numbers
    setlocal foldcolumn=0    " reasonable left margin
    setlocal nowrap          " default to no wrap (esp with MySQL)
    setlocal noswapfile      " don't bother creating a .swp file
    setlocal updatetime=50   " trigger cursorhold event after 1s
    set scrolloff=0          " don't use buffer lines. it makes the 'clear' command not work as expected
    setfiletype conque       " useful
    silent execute "setlocal syntax=".g:Conque_Syntax
    setlocal foldmethod=manual

endfunction " }}}

function! conque_term#set_mappings() "{{{
    " handle unexpected closing of shell
    " passes HUP to main and all child processes
    execute 'autocmd BufUnload <buffer> python ' . b:ConqueTerm_Var . '.proc.signal(1)'
    "autocmd CursorHoldI <buffer> call conque_term#auto_read()
    "autocmd BufEnter <buffer> call conque_term#update_window_size()

    " map first 256 ASCII chars {{{
    for i in range(33, 255)
        " <Bar>
        if i == 124
            silent execute "inoremap <silent> <buffer> <Bar> <C-o>:python " . b:ConqueTerm_Var . ".write('\\|')<CR>"
            continue
        endif
        silent execute "inoremap <silent> <buffer> " . nr2char(i) . " <C-o>:python " . b:ConqueTerm_Var . ".write('" . conque_term#python_escape(nr2char(i)) . "')<CR>"
    endfor
    " }}}

    " Special cases
    silent execute 'inoremap <silent> <buffer> <BS> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u0008")<CR>'
    silent execute 'inoremap <silent> <buffer> <Tab> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u0009")<CR>'
    silent execute 'inoremap <silent> <buffer> <LF> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u000a")<CR>'
    silent execute 'inoremap <silent> <buffer> <CR> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u000d")<CR>'
    silent execute 'inoremap <silent> <buffer> <Space> <C-o>:python ' . b:ConqueTerm_Var . '.write(" ")<CR>'
    silent execute 'inoremap <silent> <buffer> <Up> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[A")<CR>'
    silent execute 'inoremap <silent> <buffer> <Down> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[B")<CR>'
    silent execute 'inoremap <silent> <buffer> <Right> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[C")<CR>'
    silent execute 'inoremap <silent> <buffer> <Left> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[D")<CR>'

    " use F8 key to get more input
    inoremap <silent> <buffer> <expr> <F7> " \<BS>"
    silent execute 'autocmd CursorHoldI <buffer> python ' .  b:ConqueTerm_Var . '.auto_read()'
    


    return

    inoremap <silent> <buffer> <BS> <Esc>:call conque_term#press_key(nr2char(8))<CR>a
    inoremap <silent> <buffer> <Tab> <Esc>:call conque_term#press_key(nr2char(9))<CR>a
    inoremap <silent> <buffer> <LF> <Esc>:call conque_term#press_key(nr2char(10))<CR>a
    inoremap <silent> <buffer> <CR> <Esc>:call conque_term#press_key(nr2char(13))<CR>a
    inoremap <silent> <buffer> <Space> <Esc>:call conque_term#press_key(nr2char(32))<CR>a
    inoremap <silent> <buffer> <Bar> <Esc>:call conque_term#press_key(nr2char(124))<CR>a
    inoremap <silent> <buffer> <Up> <Esc>:call conque_term#press_key("<C-v><Esc>[A")<CR>a
    inoremap <silent> <buffer> <Down> <Esc>:call conque_term#press_key("<C-v><Esc>[B")<CR>a
    inoremap <silent> <buffer> <Right> <Esc>:call conque_term#press_key("<C-v><Esc>[C")<CR>a
    inoremap <silent> <buffer> <Left> <Esc>:call conque_term#press_key("<C-v><Esc>[D")<CR>a

    " Control / Meta chars {{{
    for c in split(s:chars_control, '\zs')
        silent execute 'inoremap <silent> <buffer> <C-' . c . '> <Esc>:call conque_term#press_key("<C-v><C-' . c . '>")<CR>a'
    endfor

    " meta characters 
    for c in split(s:chars_meta, '\zs')
        silent execute 'inoremap <silent> <buffer> <M-' . c . '> <Esc>:call conque_term#press_key("<C-v><Esc>' . c . '")<CR>a'
    endfor
    " }}}

    " other weird stuff {{{

    " use F8 key to get more input
    inoremap <silent> <buffer> <F8> <Esc>:call conque_term#read(1)<CR>a

    " used for auto read
    inoremap <silent> <buffer> <expr> <F7> " \<BS>"

    " remap paste keys
    nnoremap <silent> <buffer> p :call conque_term#paste()<CR>
    nnoremap <silent> <buffer> P :call conque_term#paste()<CR>

    " send selected text into conque
	  vnoremap <silent> <F9> :<C-u>call conque_term#send_selected(visualmode())<CR>

    " send escape
    inoremap <silent> <buffer> <Esc><Esc> <Esc>:call conque_term#press_key("<C-v><Esc>")<CR>a
    nnoremap <silent> <buffer> <Esc> :<C-u>call conque_term#message('To send an <E'.'sc> to the terminal, press <E'.'sc><E'.'sc> quickly in insert mode. Some programs, such as Vim, will also accept <Ctrl-c> as a substitute for <E'.'sc>', 1)<CR>
    nnoremap <silent> <buffer> <C-c> :call conque_term#press_key("<C-v><C-c>")<CR>a

    " }}}

endfunction "}}}


function! conque_term#python_escape(input) "{{{
    let l:cleaned = a:input
    let l:cleaned = substitute(l:cleaned, '\\', '\\\\', 'g')
    let l:cleaned = substitute(l:cleaned, '\n', '\\n', 'g')
    let l:cleaned = substitute(l:cleaned, '\r', '\\r', 'g')
    let l:cleaned = substitute(l:cleaned, "'", "\\\\'", 'g')
    return l:cleaned
endfunction "}}}



