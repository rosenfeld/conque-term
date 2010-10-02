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
" **** CROSS-TERMINAL SETTINGS *****************************************************************************
" **********************************************************************************************************

" Extra key codes
let s:input_extra = {}
let s:input_extra_num = {}

let s:t_handle = { 'idx' : 1, 'var' : '', 'is_buffer' : 1, 'active' : 1 }
let s:terminal_handles = {}

let s:save_updatetime = &updatetime

augroup ConqueTerm
autocmd ConqueTerm VimLeave * call conque_term#close_all()

" read more output when this isn't the current buffer
if g:ConqueTerm_ReadUnfocused == 1
    autocmd ConqueTerm CursorHold * call conque_term#read_all(0)
endif

" **********************************************************************************************************
" **** VIM FUNCTIONS ***************************************************************************************
" **********************************************************************************************************

" launch conque
function! conque_term#open(...) "{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])
    let return_to_current  = get(a:000, 2, 0)
    let is_buffer  = get(a:000, 3, 1)

    " switch to buffer if needed
    if is_buffer && return_to_current
      let save_sb = &switchbuf

      "use an agressive sb option
      sil set switchbuf=usetab

      " current buffer name
      let current_buffer = bufname("%")
    endif

    " bare minimum validation
    if !has('python')
        echohl WarningMsg | echomsg "Conque requires the Python interface to be installed" | echohl None
        return 0
    endif
    if empty(command)
        echohl WarningMsg | echomsg "No command found" | echohl None
        return 0
    else
        let l:cargs = split(command, '\s')
        if !executable(l:cargs[0])
            echohl WarningMsg | echomsg "Not an executable: " . l:cargs[0] | echohl None
            return 0
        endif
    endif

    let g:ConqueTerm_Idx += 1
    let g:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx
    let g:ConqueTerm_BufName = substitute(command, ' ', '\\ ', 'g') . "\\ -\\ " . g:ConqueTerm_Idx

    " set buffer window options
    if is_buffer
        call conque_term#set_buffer_settings(command, hooks)

        let b:ConqueTerm_Idx = g:ConqueTerm_Idx
        let b:ConqueTerm_Var = g:ConqueTerm_Var
    endif

    " save handle
    let handle = conque_term#create_handle(g:ConqueTerm_Idx, is_buffer)
    let s:terminal_handles[g:ConqueTerm_Idx] = handle

    " open command
    try
        let l:config = '{"color":' . string(g:ConqueTerm_Color) . ',"TERM":"' . g:ConqueTerm_TERM . '"}'
        execute 'python ' . g:ConqueTerm_Var . ' = Conque()'
        execute "python " . g:ConqueTerm_Var . ".open('" . conque_term#python_escape(command) . "', " . l:config . ")"
    catch 
        echohl WarningMsg | echomsg "Unable to open command: " . command | echohl None
        return 0
    endtry

    " set buffer mappings and auto commands 
    if is_buffer
        call conque_term#set_mappings('start')
    endif

    " switch to buffer if needed
    if is_buffer && return_to_current
        " jump back to code buffer
        sil exe ":sb " . current_buffer
        sil exe ":set switchbuf=" . save_sb
    elseif is_buffer
        startinsert!
    endif

    return handle
endfunction "}}}

" open(), but no buffer
function! conque_term#subprocess(command) " {{{
    
    let handle = conque_term#open(a:command, [], 0, 0)
    if !exists('b:ConqueTerm_Var')
        call conque_term#on_blur()
    endif
    return handle

endfunction " }}}

" set buffer options
function! conque_term#set_buffer_settings(command, pre_hooks) "{{{

    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        sil exe h
    endfor
    sil exe "edit " . g:ConqueTerm_BufName

    " showcmd gets altered by nocompatible
    let sc_save = &showcmd

    " buffer settings 
    setlocal nocompatible      " conque won't work in compatible mode
    setlocal nopaste           " conque won't work in paste mode
    setlocal buftype=nofile    " this buffer is not a file, you can't save it
    setlocal nonumber          " hide line numbers
    if v:version >= 703
        setlocal norelativenumber " hide relative line numbers (VIM >= 7.3)
    endif
    setlocal foldcolumn=0      " reasonable left margin
    setlocal nowrap            " default to no wrap (esp with MySQL)
    setlocal noswapfile        " don't bother creating a .swp file
    setlocal scrolloff=0       " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal sidescrolloff=0   " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal sidescroll=1      " don't use buffer lines. it makes the 'clear' command not work as expected
    setlocal foldmethod=manual " don't fold on {{{}}} and stuff
    setlocal bufhidden=hide    " when buffer is no longer displayed, don't wipe it out
    setfiletype conque_term    " useful
    sil exe "setlocal syntax=" . g:ConqueTerm_Syntax

    " reset showcmd
    if sc_save
      set showcmd
    else
      set noshowcmd
    endif

    " temporary global settings go in here
    call conque_term#on_focus()

endfunction " }}}

" set key mappings and auto commands
function! conque_term#set_mappings(action) "{{{

    " set action
    if a:action == 'toggle'
        if exists('b:conque_on') && b:conque_on == 1
            let l:action = 'stop'
            echohl WarningMsg | echomsg "Terminal is paused" | echohl None
        else
            let l:action = 'start'
            echohl WarningMsg | echomsg "Terminal is resumed" | echohl None
        endif
    else
        let l:action = a:action
    endif

    " if mappings are being removed, add 'un'
    let map_modifier = 'nore'
    if l:action == 'stop'
        let map_modifier = 'un'
    endif

    " remove all auto commands
    if l:action == 'stop'
        execute 'autocmd! ' . b:ConqueTerm_Var

    else
        execute 'augroup ' . b:ConqueTerm_Var

        " handle unexpected closing of shell, passes HUP to parent and all child processes
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufUnload <buffer> python ' . b:ConqueTerm_Var . '.proc.signal(1)'

        " check for resized/scrolled buffer when entering buffer
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufEnter <buffer> python ' . b:ConqueTerm_Var . '.update_window_size()'
        execute 'autocmd ' . b:ConqueTerm_Var . ' VimResized python ' . b:ConqueTerm_Var . '.update_window_size()'

        " set/reset updatetime on entering/exiting buffer
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufEnter <buffer> call conque_term#on_focus()'
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufLeave <buffer> call conque_term#on_blur()'

        " reposition cursor when going into insert mode
        execute 'autocmd ' . b:ConqueTerm_Var . ' InsertEnter <buffer> python ' . b:ConqueTerm_Var . '.insert_enter()'

        " poll for more output
        sil execute 'autocmd ' . b:ConqueTerm_Var . ' CursorHoldI <buffer> python ' .  b:ConqueTerm_Var . '.auto_read()'
    endif

    " map ASCII 1-31
    for c in range(1, 31)
        " <Esc>
        if c == 27
            continue
        endif
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-' . nr2char(64 + c) . '> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(' . c . '))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-' . nr2char(64 + c) . '>'
        endif
    endfor
    if l:action == 'start'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> <C-c> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(3))<CR>'
    else
        sil exe 'n' . map_modifier . 'map <silent> <buffer> <C-c>'
    endif

    " leave insert mode
    if !exists('g:ConqueTerm_EscKey') || g:ConqueTerm_EscKey == '<Esc>'
        " use <Esc><Esc> to send <Esc> to terminal
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc><Esc> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(27))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc><Esc>'
        endif
    else
        " use <Esc> to send <Esc> to terminal
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . g:ConqueTerm_EscKey . ' <Esc>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc> <C-o>:python ' . b:ConqueTerm_Var . '.write(chr(27))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . g:ConqueTerm_EscKey
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc>'
        endif
    endif

    " Map <C-w> in insert mode
    if exists('g:ConqueTerm_CWInsert') && g:ConqueTerm_CWInsert == 1
        inoremap <silent> <buffer> <C-w>j <Esc><C-w>j
        inoremap <silent> <buffer> <C-w>k <Esc><C-w>k
        inoremap <silent> <buffer> <C-w>h <Esc><C-w>h
        inoremap <silent> <buffer> <C-w>l <Esc><C-w>l
        inoremap <silent> <buffer> <C-w>w <Esc><C-w>w
    endif

    " map ASCII 33-127
    for i in range(33, 127)
        " <Bar>
        if i == 124
            if l:action == 'start'
                sil exe "i" . map_modifier . "map <silent> <buffer> <Bar> <C-o>:python " . b:ConqueTerm_Var . ".write(chr(124))<CR>"
            else
                sil exe "i" . map_modifier . "map <silent> <buffer> <Bar>"
            endif
            continue
        endif
        if l:action == 'start'
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i) . " <C-o>:python " . b:ConqueTerm_Var . ".write(chr(" . i . "))<CR>"
        else
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i)
        endif
    endfor

    " map ASCII 128-255
    for i in range(128, 255)
        if l:action == 'start'
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i) . " <C-o>:python " . b:ConqueTerm_Var . ".write('" . nr2char(i) . "')<CR>"
        else
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i)
        endif
    endfor

    " Special cases
    if l:action == 'start'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <BS> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u0008")<CR>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Space> <C-o>:python ' . b:ConqueTerm_Var . '.write(" ")<CR>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Up> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[A")<CR>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Down> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[B")<CR>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Right> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[C")<CR>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Left> <C-o>:python ' . b:ConqueTerm_Var . '.write(u"\u001b[D")<CR>'
    else
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <BS>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Space>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Up>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Down>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Right>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Left>'
    endif

    " send selected text into conque
    if l:action == 'start'
        sil exe 'v' . map_modifier . 'map <silent> ' . g:ConqueTerm_SendVisKey . ' :<C-u>call conque_term#send_selected(visualmode())<CR>'
    else
        sil exe 'v' . map_modifier . 'map <silent> ' . g:ConqueTerm_SendVisKey
    endif

    " remap paste keys
    if l:action == 'start'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> p :python ' . b:ConqueTerm_Var . '.write(vim.eval("@@"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> P :python ' . b:ConqueTerm_Var . '.write(vim.eval("@@"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> ]p :python ' . b:ConqueTerm_Var . '.write(vim.eval("@@"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> [p :python ' . b:ConqueTerm_Var . '.write(vim.eval("@@"))<CR>a'
    else
        sil exe 'n' . map_modifier . 'map <silent> <buffer> p'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> P'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> ]p'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> [p'
    endif
    if has('gui_running')
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <buffer> <S-Insert> <Esc>:<C-u>python ' . b:ConqueTerm_Var . ".write(vim.eval('@+'))<CR>a"
        else
            sil exe 'i' . map_modifier . 'map <buffer> <S-Insert>'
        endif
    endif

    " disable other normal mode keys which insert text
    if l:action == 'start'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> r :echo "Replace mode disabled in shell."<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> R :echo "Replace mode disabled in shell."<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> c :echo "Change mode disabled in shell."<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> C :echo "Change mode disabled in shell."<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> s :echo "Change mode disabled in shell."<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> S :echo "Change mode disabled in shell."<CR>'
    else
        sil exe 'n' . map_modifier . 'map <silent> <buffer> r'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> R'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> c'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> C'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> s'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> S'
    endif

    " user defined mappings
    for user_key in keys(s:input_extra)
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . user_key . ' <C-o>:python ' . b:ConqueTerm_Var . ".write('" . s:input_extra[user_key] . "')<CR>"
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . user_key
        endif
    endfor

    for user_key in keys(s:input_extra_num)
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . user_key . ' <C-o>:python ' . b:ConqueTerm_Var . ".write(unichr(" . s:input_extra_num[user_key] . "))<CR>"
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . user_key
        endif
    endfor

    " set conque as on or off
    if l:action == 'start'
        let b:conque_on = 1
    else
        let b:conque_on = 0
    endif

    " map command to start stop the shell
    if a:action == 'start'
        nnoremap <F5> :<C-u>call conque_term#set_mappings('toggle')<CR>
    endif

endfunction " }}}

" send selected text from another buffer
function! conque_term#send_selected(type) "{{{
    let reg_save = @@

    " save user's sb settings
    let sb_save = &switchbuf
    set switchbuf=usetab

    " yank current selection
    sil exe "normal! `<" . a:type . "`>y"

    " format yanked text
    let @@ = substitute(@@, '^[\r\n]*', '', '')
    let @@ = substitute(@@, '[\r\n]*$', '', '')

    " execute yanked text
    sil exe ":sb " . g:ConqueTerm_BufName
    sil exe 'python ' . g:ConqueTerm_Var . '.paste_selection()'

    " reset original values
    let @@ = reg_save
    sil exe 'set switchbuf=' . sb_save

    " scroll buffer left
    startinsert!
    normal 0zH
endfunction "}}}

" read from all known conque buffers
function! conque_term#read_all(insert_mode) "{{{

    for i in range(1, g:ConqueTerm_Idx)
        try
            if !s:terminal_handles[i].active
                continue
            endif

            let output = s:terminal_handles[i].read(1)

            if !s:terminal_handles[i].is_buffer && exists('*s:terminal_handles[i].callback')
                call s:terminal_handles[i].callback(output)
            endif
        catch
            " probably a deleted buffer
        endtry
    endfor

    " restart updatetime
    if a:insert_mode
        call feedkeys("\<C-o>f\e", "n")
    else
        call feedkeys("f\e", "n")
    endif

endfunction "}}}

" close all subprocesses
function! conque_term#close_all() "{{{

    for i in range(1, g:ConqueTerm_Idx)
        try
            call s:terminal_handles[i].close()
        catch
            " probably a deleted buffer
        endtry
    endfor

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

" gets called when user enters conque buffer.
" Useful for making temp changes to global config
function! conque_term#on_focus() " {{{
    " Disable NeoComplCache. It has global hooks on CursorHold and CursorMoved :-/
    let s:NeoComplCache_WasEnabled = exists(':NeoComplCacheLock')
    if s:NeoComplCache_WasEnabled == 2
        NeoComplCacheLock
    endif
 
    if g:ConqueTerm_ReadUnfocused == 1
        autocmd! ConqueTerm CursorHoldI *
        autocmd! ConqueTerm CursorHold *
    endif

    " set poll interval to 50ms
    set updatetime=50

    " if configured, go into insert mode
    if g:ConqueTerm_InsertOnEnter == 1
        startinsert!
    endif

endfunction " }}}

" gets called when user exits conque buffer.
" Useful for resetting changes to global config
function! conque_term#on_blur() " {{{
    " re-enable NeoComplCache if needed
    if exists('s:NeoComplCache_WasEnabled') && exists(':NeoComplCacheUnlock') && s:NeoComplCache_WasEnabled == 2
        NeoComplCacheUnlock
    endif
 
    " reset poll interval
    if g:ConqueTerm_ReadUnfocused == 1
        set updatetime=1000
        autocmd ConqueTerm CursorHoldI * call conque_term#read_all(1)
        autocmd ConqueTerm CursorHold * call conque_term#read_all(0)
    elseif exists('s:save_updatetime')
        exe 'set updatetime=' . s:save_updatetime
    else
        set updatetime=2000
    endif
endfunction " }}}

function! conque_term#bell() " {{{
    echohl WarningMsg | echomsg "BELL!" | echohl None
endfunction " }}}

" **********************************************************************************************************
" **** "API" functions *************************************************************************************
" **********************************************************************************************************

" Write to a conque terminal buffer
"
" Use this function to send text to ConqueTerm. If you are updating a remote
" buffer you may want to set the config option g:ConqueTerm_ReadUnfocused so
" the terminal will continue updating.
"
" Example usage:
"
"   let conque_buff = conque_term#open('mysql -u joe LunchBucket', ['belowright split', 'resize 20'], 1)
"   call conque_buff.write('SELECT NOW() AS "Lunch time";' . "\n")
"
" Or with minimal options:
"
"   call let conque_buff = conque_term#open('bash')
"   call conque_buff.writeln('cd ' . make_path)
"   call conque_buff.writeln('make')
"
" @param text String The text to write.
function! s:t_handle.write(text) dict " {{{

    " if we're not in terminal buffer, pass flag to not position the cursor
    sil exe 'python ' . self.var . '.write(vim.eval("a:text"), False, False)'

endfunction " }}}

" Write to a conque terminal buffer, add a new line to end of input
"
" See conque_term#write() for details
function! s:t_handle.writeln(text) dict " {{{

    call self.write(a:text . "\n")

endfunction " }}}


" Read data from conque terminal buffer
"
" Retrieve an array of lines of text from the terminal. This really doesn't 
" provide any special functionality other than locating the correct buffer.
" 
" @param read_time Integer (Optional) The number of milliseconds to wait for output before returning to your code buffer.
" @param update_buffer Bool (Optional) If set to 0 then the text read will never be displayed in the terminal buffer.
function! s:t_handle.read(...) dict " {{{

    let read_time = get(a:000, 0, 1)
    let update_buffer = get(a:000, 1, self.is_buffer)

    if update_buffer 
        let up_py = 'True'
    else
        let up_py = 'False'
    endif

    " figure out if we're in the buffer we're updating
    if exists('b:ConqueTerm_Var') && b:ConqueTerm_Var == self.var
        let in_buffer = 1
    else
        let in_buffer = 0
    endif

    let output = ''

    " read!
    sil exec ":python conque_tmp = " . self.var . ".read(timeout = " . read_time . ", set_cursor = False, return_output = True, update_buffer = " . up_py . ")"

    " ftw!
    python << EOF
if conque_tmp:
    conque_tmp = re.sub('\\\\', '\\\\\\\\', conque_tmp) 
    conque_tmp = re.sub('"', '\\\\"', conque_tmp)
    vim.command('let output = "' + conque_tmp + '"')
EOF

    return output

endfunction " }}}

function! s:t_handle.set_callback(callback_func) dict " {{{

    let s:terminal_handles[self.idx].callback = function(a:callback_func)

endfunction " }}}

function! s:t_handle.close() dict " {{{

    sil exe 'python ' . self.var . '.proc.signal(1)'

endfunction " }}}

function! conque_term#create_handle(...) " {{{

    " find conque buffer to update
    let buf_num = get(a:000, 0, 0)
    if buf_num > 0
        let pvar = 'ConqueTerm_' . buf_num
    elseif exists('b:ConqueTerm_Var')
        let pvar = b:ConqueTerm_Var
        let buf_num = b:ConqueTerm_Idx
    else
        let pvar = g:ConqueTerm_Var
        let buf_num = g:ConqueTerm_Idx
    endif

    " is ther a buffer?
    let is_buffer = get(a:000, 1, 1)

    let l:handle = copy(s:t_handle)
    let l:handle.is_buffer = is_buffer
    let l:handle.idx = buf_num
    let l:handle.var = pvar

    return l:handle

endfunction " }}}

function! conque_term#get_handle(...) " {{{

    " find conque buffer to update
    let buf_num = get(a:000, 0, 0)

    if exists('s:terminal_handles[buf_num]')
        
    elseif exists('b:ConqueTerm_Var')
        let buf_num = b:ConqueTerm_Idx
    else
        let buf_num = g:ConqueTerm_Idx
    endif

    return s:terminal_handles[buf_num]

endfunction " }}}

" **********************************************************************************************************
" **** PYTHON **********************************************************************************************
" **********************************************************************************************************

let conque_py_dir = substitute(findfile('autoload/conque_term.vim', &rtp), 'conque_term.vim', '', '')
exec "pyfile " . conque_py_dir . "Conque.py"
exec "pyfile " . conque_py_dir . "ConqueSubprocess.py"
exec "pyfile " . conque_py_dir . "ConqueScreen.py"

