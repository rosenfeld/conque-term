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


" **********************************************************************************************************
" **** VIM FUNCTIONS ***************************************************************************************
" **********************************************************************************************************

" launch conque
function! conque_term#open(...) "{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])

    " bare minimum validation
    if empty(command)
        echohl WarningMsg | echomsg "No command found" | echohl None
        return 0
    else
        let l:cargs = split(command, '\s')
        if !executable(l:cargs[0])
            echohl WarningMsg | echomsg "Not an executable" | echohl None
            return 0
        endif
    endif

    " set buffer window options
    let g:Conque_BufName = substitute(command, ' ', '\\ ', 'g') . "\\ -\\ " . g:ConqueTerm_Idx
    call conque_term#set_buffer_settings(command, hooks)
    let b:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx
    let g:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx
    let g:ConqueTerm_Idx += 1

    " open command
    try
        let l:config = '{"color":' . string(g:ConqueTerm_Color) . ',"TERM":"' . g:ConqueTerm_TERM . '"}'
        execute 'python ' . b:ConqueTerm_Var . ' = Conque()'
        execute "python " . b:ConqueTerm_Var . ".open('" . conque_term#python_escape(command) . "', " . l:config . ")"
    catch 
        echohl WarningMsg | echomsg "Unable to open command: " . command | echohl None
        return 0
    endtry

    " set buffer mappings and auto commands 
    call conque_term#set_mappings()

    startinsert!
    return 1
endfunction "}}}

" set buffer options
function! conque_term#set_buffer_settings(command, pre_hooks) "{{{

    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        silent execute h
    endfor
    silent execute "edit " . g:Conque_BufName

    " buffer settings 
    setlocal nocompatible      " conque won't work in compatible mode
    setlocal buftype=nofile    " this buffer is not a file, you can't save it
    setlocal nonumber          " hide line numbers
    setlocal foldcolumn=0      " reasonable left margin
    setlocal nowrap            " default to no wrap (esp with MySQL)
    setlocal noswapfile        " don't bother creating a .swp file
    setlocal updatetime=50     " trigger cursorhold event after 50ms / XXX - global
    setlocal scrolloff=0       " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal sidescrolloff=0   " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal sidescroll=1      " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal foldmethod=manual " don't fold on {{{}}} and stuff
    setlocal switchbuf=usetab  " switch tabs with the <f9> command
    silent execute "setlocal syntax=" . g:ConqueTerm_Syntax
    setfiletype conque         " useful

endfunction " }}}

" set key mappings and auto commands
function! conque_term#set_mappings() "{{{

    " handle unexpected closing of shell, passes HUP to parent and all child processes
    execute 'autocmd BufUnload <buffer> python ' . b:ConqueTerm_Var . '.proc.signal(1)'

    " check for resized/scrolled buffer when entering buffer
    execute 'autocmd BufEnter <buffer> python ' . b:ConqueTerm_Var . '.update_window_size()'

    " set/reset updatetime on entering/exiting buffer
    autocmd BufEnter <buffer> set updatetime=50
    autocmd BufLeave <buffer> set updatetime=1000

    " check for resized/scrolled buffer when entering insert mode
    " XXX - messed up since we enter insert mode at each updatetime
    "execute 'autocmd InsertEnter <buffer> python ' . b:ConqueTerm_Var . '.screen.align()'

    " read more output when this isn't the current buffer
    if g:ConqueTerm_ReadUnfocused == 1
        autocmd CursorHold * call conque_term#read_all()
    endif

    " use F22 key to get more input
    inoremap <silent> <buffer> <expr> <F22> "\<left>\<right>"
    inoremap <silent> <buffer> <expr> <F23> "\<right>\<left>"
    silent execute 'autocmd CursorHoldI <buffer> python ' .  b:ConqueTerm_Var . '.auto_read()'

    " map ASCII 1-31
    for c in range(1, 31)
        " <Esc>
        if c == 27
            continue
        endif
        silent execute 'inoremap <silent> <buffer> <C-' . nr2char(64 + c) . '> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(' . c . '))<CR>'
    endfor
    silent execute 'inoremap <silent> <buffer> <Esc><Esc> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(27))<CR>'
    silent execute 'nnoremap <silent> <buffer> <C-c> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(3))<CR>'

    " map ASCII 33-127
    for i in range(33, 127)
        " <Bar>
        if i == 124
            silent execute "inoremap <silent> <buffer> <Bar> <C-o>:python " . b:ConqueTerm_Var . ".write(chr(124))<CR>"
            continue
        endif
        silent execute "inoremap <silent> <buffer> " . nr2char(i) . " <C-o>:python " . b:ConqueTerm_Var . ".write(chr(" . i . "))<CR>"
    endfor

    " map ASCII 128-255
    for i in range(128, 255)
        silent execute "inoremap <silent> <buffer> " . nr2char(i) . " <C-o>:python " . b:ConqueTerm_Var . ".write('" . nr2char(i) . "')<CR>"
    endfor

    " Special cases
    silent execute 'inoremap <silent> <buffer> <BS> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u0008")<CR>'
    "silent execute 'inoremap <silent> <buffer> <Tab> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u0009")<CR>'
    silent execute 'inoremap <silent> <buffer> <LF> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u000a")<CR>'
    silent execute 'inoremap <silent> <buffer> <CR> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u000d")<CR>'
    silent execute 'inoremap <silent> <buffer> <Space> <C-o>:python ' . b:ConqueTerm_Var . '.write(" ")<CR>'
    silent execute 'inoremap <silent> <buffer> <Up> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[A")<CR>'
    silent execute 'inoremap <silent> <buffer> <Down> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[B")<CR>'
    silent execute 'inoremap <silent> <buffer> <Right> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[C")<CR>'
    silent execute 'inoremap <silent> <buffer> <Left> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[D")<CR>'

    " meta characters 
    "for c in split(s:chars_meta, '\zs')
    "    silent execute 'inoremap <silent> <buffer> <M-' . c . '> <Esc>:call conque_term#press_key("<C-v><Esc>' . c . '")<CR>a'
    "endfor

    " send selected text into conque
	vnoremap <silent> <F9> :<C-u>call conque_term#send_selected(visualmode())<CR>

    " remap paste keys
    silent execute 'nnoremap <silent> <buffer> p :python ' . b:ConqueTerm_Var . '.paste()<CR>'
    silent execute 'nnoremap <silent> <buffer> P :python ' . b:ConqueTerm_Var . '.paste()<CR>'

    " disable other normal mode keys which insert text
    nnoremap <silent> <buffer> r :echo 'Replace mode disabled in shell.'<CR>
    nnoremap <silent> <buffer> R :echo 'Replace mode disabled in shell.'<CR>
    nnoremap <silent> <buffer> c :echo 'Change mode disabled in shell.'<CR>
    nnoremap <silent> <buffer> C :echo 'Change mode disabled in shell.'<CR>
    nnoremap <silent> <buffer> s :echo 'Change mode disabled in shell.'<CR>
    nnoremap <silent> <buffer> S :echo 'Change mode disabled in shell.'<CR>

    " help message about <Esc>
    "nnoremap <silent> <buffer> <Esc> :echo 'To send an <E'.'sc> to the terminal, press <E'.'sc><E'.'sc> quickly in insert mode. Some programs, such as Vim, will also accept <Ctrl-c> as a substitute for <E'.'sc>'<CR><Esc>

endfunction "}}}

" send selected text from another buffer
function! conque_term#send_selected(type) "{{{
    let reg_save = @@

    " yank current selection
    silent execute "normal! `<" . a:type . "`>y"

    let @@ = substitute(@@, '^[\r\n]*', '', '')
    let @@ = substitute(@@, '[\r\n]*$', '', '')

    silent execute ":sb " . g:Conque_BufName
    silent execute 'python ' . g:ConqueTerm_Var . '.paste_selection()'

    let @@ = reg_save
    startinsert!
endfunction "}}}

" read from all known conque buffers
function! conque_term#read_all() "{{{
    " don't run this if we're in a conque buffer
    if exists('b:ConqueTerm_Var')
        return
    endif

    try
        for i in range(1, g:ConqueTerm_Idx - 1)
            execute 'python ConqueTerm_' . string(i) . '.read(1)'
        endfor
    catch
        " probably a deleted buffer
    endtry

    " TODO - doesn't work
    " restart updatetime
    "call feedkeys("\x80\xFD\x35")
endfunction "}}}

" util function to add enough \s to pass a string to python
function! conque_term#python_escape(input) "{{{
    let l:cleaned = a:input
    let l:cleaned = substitute(l:cleaned, '\\', '\\\\', 'g')
    let l:cleaned = substitute(l:cleaned, '\n', '\\n', 'g')
    let l:cleaned = substitute(l:cleaned, '\r', '\\r', 'g')
    let l:cleaned = substitute(l:cleaned, "'", "\\\\'", 'g')
    return l:cleaned
endfunction "}}}

" **********************************************************************************************************
" **** PYTHON **********************************************************************************************
" **********************************************************************************************************

pyfile ~/.vim/autoload/conque.py
pyfile ~/.vim/autoload/conque_subprocess.py
pyfile ~/.vim/autoload/conque_screen.py

