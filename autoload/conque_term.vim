" FILE:     plugin/conque_term.vim {{{
"
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
" **** SYSTEM DETECTION ************************************************************************************
" **********************************************************************************************************

" {{{

function! conque_term#system_fail(feature) " {{{

    " create a new buffer
    new
    setlocal buftype=nofile
    setlocal nonumber
    setlocal foldcolumn=0
    setlocal nowrap
    setlocal noswapfile

    " missing vim features
    if feature == 'has_py'

        call append('$', 'Conque ERROR: Python interface cannot be loaded')
        call append('$', '')
        call append('$', 'Your version of Vim appears to be installed without the Python interface.')

    endif

endfunction " }}}

" **********************************************************************************************************
" PYTHON DETECTION {{{

" choose a python version and define a string unicoding function
let s:py = ''
if g:ConqueTerm_PyVersion == 3
    let s:pytest = 'python3'
else
    let s:pytest = 'python'
    let g:ConqueTerm_PyVersion = 2
endif

" first the requested version
if has(s:pytest)
    echo s:pytest
    if s:pytest == 'python3'
        let s:py = 'py3'
    else
        let s:py = 'py'
    endif

" otherwise use the other version
else
    let s:py_alternate = 5 - g:ConqueTerm_PyVersion
    if s:py_alternate == 3
        let s:pytest = 'python3'
    else
        let s:pytest = 'python'
    endif
    if has(s:pytest)
        echo "alternate " . s:pytest
        echohl WarningMsg | echomsg "Python " . g:ConqueTerm_PyVersion . " interface is not installed, using Python " . s:py_alternate . " instead" | echohl None
        let g:ConqueTerm_PyVersion = s:py_alternate
        if s:pytest == 'python3'
            let s:py = 'py3'
        else
            let s:py = 'py'
        endif
    endif
endif

" test if we actually found a python version
if s:py == ''
    call conque_term#system_fail('has_py')
    finish
endif

" }}}

" **********************************************************************************************************
" OPERATING SYSTEM DETECTION {{{

" quick and dirty platform declaration
if has('unix') == 1
    let s:platform = 'nix'
    sil exe s:py . " CONQUE_PLATFORM = 'nix'"
else
    let s:platform = 'dos'
    sil exe s:py . " CONQUE_PLATFORM = 'dos'"
endif

" }}}

" **********************************************************************************************************
" WINDOWS PYTHON MODULE TEST {{{

if s:platform == 'dos'
    try
        sil exe s:py . " import win32process"
    catch
        call conque_term#system_fail('has_pywin32')
        finish
    endtry
endif

" }}}

" }}}

" **********************************************************************************************************
" **** WINDOWS VK CODES ************************************************************************************
" **********************************************************************************************************

" Windows Virtual Key Codes  {{{
let s:windows_vk = {
\    'VK_ADD' : 107,
\    'VK_APPS' : 93,
\    'VK_ATTN' : 246,
\    'VK_BACK' : 8,
\    'VK_BROWSER_BACK' : 166,
\    'VK_BROWSER_FORWARD' : 167,
\    'VK_CANCEL' : 3,
\    'VK_CAPITAL' : 20,
\    'VK_CLEAR' : 12,
\    'VK_CONTROL' : 17,
\    'VK_CONVERT' : 28,
\    'VK_CRSEL' : 247,
\    'VK_DECIMAL' : 110,
\    'VK_DELETE' : 46,
\    'VK_DIVIDE' : 111,
\    'VK_DOWN' : 40,
\    'VK_END' : 35,
\    'VK_EREOF' : 249,
\    'VK_ESCAPE' : 27,
\    'VK_EXECUTE' : 43,
\    'VK_EXSEL' : 248,
\    'VK_F1' : 112,
\    'VK_F10' : 121,
\    'VK_F11' : 122,
\    'VK_F12' : 123,
\    'VK_F13' : 124,
\    'VK_F14' : 125,
\    'VK_F15' : 126,
\    'VK_F16' : 127,
\    'VK_F17' : 128,
\    'VK_F18' : 129,
\    'VK_F19' : 130,
\    'VK_F2' : 113,
\    'VK_F20' : 131,
\    'VK_F21' : 132,
\    'VK_F22' : 133,
\    'VK_F23' : 134,
\    'VK_F24' : 135,
\    'VK_F3' : 114,
\    'VK_F4' : 115,
\    'VK_F5' : 116,
\    'VK_F6' : 117,
\    'VK_F7' : 118,
\    'VK_F8' : 119,
\    'VK_F9' : 120,
\    'VK_FINAL' : 24,
\    'VK_HANGEUL' : 21,
\    'VK_HANGUL' : 21,
\    'VK_HANJA' : 25,
\    'VK_HELP' : 47,
\    'VK_HOME' : 36,
\    'VK_INSERT' : 45,
\    'VK_JUNJA' : 23,
\    'VK_KANA' : 21,
\    'VK_KANJI' : 25,
\    'VK_LBUTTON' : 1,
\    'VK_LCONTROL' : 162,
\    'VK_LEFT' : 37,
\    'VK_LMENU' : 164,
\    'VK_LSHIFT' : 160,
\    'VK_LWIN' : 91,
\    'VK_MBUTTON' : 4,
\    'VK_MEDIA_NEXT_TRACK' : 176,
\    'VK_MEDIA_PLAY_PAUSE' : 179,
\    'VK_MEDIA_PREV_TRACK' : 177,
\    'VK_MENU' : 18,
\    'VK_MODECHANGE' : 31,
\    'VK_MULTIPLY' : 106,
\    'VK_NEXT' : 34,
\    'VK_NONAME' : 252,
\    'VK_NONCONVERT' : 29,
\    'VK_NUMLOCK' : 144,
\    'VK_NUMPAD0' : 96,
\    'VK_NUMPAD1' : 97,
\    'VK_NUMPAD2' : 98,
\    'VK_NUMPAD3' : 99,
\    'VK_NUMPAD4' : 100,
\    'VK_NUMPAD5' : 101,
\    'VK_NUMPAD6' : 102,
\    'VK_NUMPAD7' : 103,
\    'VK_NUMPAD8' : 104,
\    'VK_NUMPAD9' : 105,
\    'VK_OEM_CLEAR' : 254,
\    'VK_PA1' : 253,
\    'VK_PAUSE' : 19,
\    'VK_PLAY' : 250,
\    'VK_PRINT' : 42,
\    'VK_PRIOR' : 33,
\    'VK_PROCESSKEY' : 229,
\    'VK_RBUTTON' : 2,
\    'VK_RCONTROL' : 163,
\    'VK_RETURN' : 13,
\    'VK_RIGHT' : 39,
\    'VK_RMENU' : 165,
\    'VK_RSHIFT' : 161,
\    'VK_RWIN' : 92,
\    'VK_SCROLL' : 145,
\    'VK_SELECT' : 41,
\    'VK_SEPARATOR' : 108,
\    'VK_SHIFT' : 16,
\    'VK_SNAPSHOT' : 44,
\    'VK_SPACE' : 32,
\    'VK_SUBTRACT' : 109,
\    'VK_TAB' : 9,
\    'VK_UP' : 38,
\    'VK_VOLUME_DOWN' : 174,
\    'VK_VOLUME_MUTE' : 173,
\    'VK_VOLUME_UP' : 175,
\    'VK_XBUTTON1' : 5,
\    'VK_XBUTTON2' : 6,
\    'VK_ZOOM' : 251
\   }
" }}}

" **********************************************************************************************************
" **** VIM FUNCTIONS ***************************************************************************************
" **********************************************************************************************************

" launch conque
function! conque_term#open(...) "{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])

    " bare minimum validation
    if s:py == ''
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

    " set buffer window options
    let g:ConqueTerm_BufName = substitute(command, ' ', '\\ ', 'g') . "\\ -\\ " . g:ConqueTerm_Idx
    call conque_term#set_buffer_settings(command, hooks)
    let b:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx
    let g:ConqueTerm_Var = 'ConqueTerm_' . g:ConqueTerm_Idx
    let g:ConqueTerm_Idx += 1

    " open command
    try
        let l:config = '{"color":' . string(g:ConqueTerm_Color) . ',"TERM":"' . g:ConqueTerm_TERM . '"}'
        if s:platform == 'nix'
            execute s:py . ' ' . b:ConqueTerm_Var . ' = Conque()'
            execute s:py . ' ' . b:ConqueTerm_Var . ".open('" . conque_term#python_escape(command) . "', " . l:config . ")"
        else
            " find python.exe and communicator
            let py_exe = conque_term#python_escape(conque_term#find_python_exe())
          echo conque_term#find_conque_term_vim()
            let ct_vim = conque_term#python_escape(conque_term#find_conque_term_vim())
            if py_exe == '' || ct_vim == ''
                return 0
            endif
            execute s:py . ' ' . b:ConqueTerm_Var . ' = ConqueSole()'
            execute s:py . ' ' . b:ConqueTerm_Var . ".open('" . conque_term#python_escape(command) . "', " . l:config . ", '" . py_exe . "', '" . ct_vim . "')"
        endif
    catch
        echohl WarningMsg | echomsg "Unable to open command: " . command | echohl None
    endtry

    " set buffer mappings and auto commands 
    call conque_term#set_mappings('start')

    startinsert!
    return 1
endfunction "}}}

" set buffer options
function! conque_term#set_buffer_settings(command, pre_hooks) "{{{

    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        sil exe h
    endfor
    sil exe "edit ++enc=utf-8 " . g:ConqueTerm_BufName

    " showcmd gets altered by nocompatible
    let sc_save = &showcmd

    " buffer settings 
    setlocal fileencoding=utf-8 " file encoding, even tho there's no file
    setlocal nocompatible      " conque won't work in compatible mode
    setlocal nopaste           " conque won't work in paste mode
    setlocal buftype=nofile    " this buffer is not a file, you can't save it
    setlocal nonumber          " hide line numbers
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
    call conque_term#on_focus(1)

endfunction " }}}

" set key mappings and auto commands
function! conque_term#set_mappings(action) "{{{

    " set action {{{
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
    " }}}

    " auto commands {{{
    if l:action == 'stop'
        execute 'autocmd! ' . b:ConqueTerm_Var

    else
        execute 'augroup ' . b:ConqueTerm_Var

        " handle unexpected closing of shell, passes HUP to parent and all child processes
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufUnload <buffer> ' . s:py . ' ' . b:ConqueTerm_Var . '.proc.close()'

        " check for resized/scrolled buffer when entering buffer
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufEnter <buffer> ' . s:py . ' ' . b:ConqueTerm_Var . '.update_window_size()'
        execute 'autocmd ' . b:ConqueTerm_Var . ' VimResized ' . s:py . ' ' . b:ConqueTerm_Var . '.update_window_size()'

        " set/reset updatetime on entering/exiting buffer
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufEnter <buffer> call conque_term#on_focus()'
        execute 'autocmd ' . b:ConqueTerm_Var . ' BufLeave <buffer> call conque_term#on_blur()'

        " reposition cursor when going into insert mode
        execute 'autocmd ' . b:ConqueTerm_Var . ' InsertEnter <buffer> ' . s:py . ' ' . b:ConqueTerm_Var . '.insert_enter()'

        " read more output when this isn't the current buffer
        if g:ConqueTerm_ReadUnfocused == 1
            execute 'autocmd ' . b:ConqueTerm_Var . ' CursorHold * call conque_term#read_all()'
        endif

        " poll for more output
        sil execute 'autocmd ' . b:ConqueTerm_Var . ' CursorHoldI <buffer> ' . s:py . ' ' .  b:ConqueTerm_Var . '.auto_read()'
    endif
    " }}}

    " map ASCII 1-31 {{{
    for c in range(1, 31)
        " <Esc>
        if c == 27 || c == 3
            continue
        endif
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-' . nr2char(64 + c) . '> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(chr(' . c . '))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-' . nr2char(64 + c) . '>'
        endif
    endfor
    " bonus mapping: send <C-c> in normal mode to terminal as well for panic interrupts
    if l:action == 'start'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-c> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(chr(3))<CR>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> <C-c> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(chr(3))<CR>'
    else
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <C-c>'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> <C-c>'
    endif

    " leave insert mode
    if !exists('g:ConqueTerm_EscKey') || g:ConqueTerm_EscKey == '<Esc>'
        " use <Esc><Esc> to send <Esc> to terminal
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc><Esc> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(chr(27))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc><Esc>'
        endif
    else
        " use <Esc> to send <Esc> to terminal
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> ' . g:ConqueTerm_EscKey . ' <Esc>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Esc> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(chr(27))<CR>'
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
    " }}}

    " map ASCII 33-127 {{{
    for i in range(33, 127)
        " <Bar>
        if i == 124
            if l:action == 'start'
                sil exe "i" . map_modifier . "map <silent> <buffer> <Bar> <C-o>:" . s:py . ' ' . b:ConqueTerm_Var . ".write(chr(124))<CR>"
            else
                sil exe "i" . map_modifier . "map <silent> <buffer> <Bar>"
            endif
            continue
        endif
        if l:action == 'start'
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i) . " <C-o>:" . s:py . ' ' . b:ConqueTerm_Var . ".write(chr(" . i . "))<CR>"
        else
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i)
        endif
    endfor
    " }}}

    " map ASCII 128-255 {{{
    for i in range(128, 255)
        if l:action == 'start'
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i) . " <C-o>:" . s:py . ' ' . b:ConqueTerm_Var . ".write(unichr(" . i . "))<CR>"
        else
            sil exe "i" . map_modifier . "map <silent> <buffer> " . nr2char(i)
        endif
    endfor
    " }}}

    " Special keys {{{
    if l:action == 'start'
        if s:platform == 'nix'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <BS> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x08"))<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Space> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(" ")<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Up> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x1b[A"))<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Down> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x1b[B"))<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Right> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x1b[C"))<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Left> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x1b[D"))<CR>'
        else
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <BS> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(u("\x08"))<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Space> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write(" ")<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Up> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write_vk(' . s:windows_vk.VK_UP . ')<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Down> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write_vk(' . s:windows_vk.VK_DOWN . ')<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Right> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write_vk(' . s:windows_vk.VK_RIGHT . ')<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Left> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write_vk(' . s:windows_vk.VK_LEFT . ')<CR>'
            sil exe 'i' . map_modifier . 'map <silent> <buffer> <Del> <C-o>:' . s:py . ' ' . b:ConqueTerm_Var . '.write_vk(' . s:windows_vk.VK_DELETE . ')<CR>'
        endif
    else
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <BS>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Space>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Up>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Down>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Right>'
        sil exe 'i' . map_modifier . 'map <silent> <buffer> <Left>'
    endif
    " }}}

    " send selected text into conque {{{
    if l:action == 'start'
        sil exe 'v' . map_modifier . 'map <silent> ' . g:ConqueTerm_SendVisKey . ' :<C-u>call conque_term#send_selected(visualmode())<CR>'
    else
        sil exe 'v' . map_modifier . 'map <silent> ' . g:ConqueTerm_SendVisKey
    endif
    " }}}

    " remap paste keys {{{
    if l:action == 'start'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> p :' . s:py . ' ' . b:ConqueTerm_Var . '.write(unicode(vim.eval("@@"), "utf-8"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> P :' . s:py . ' ' . b:ConqueTerm_Var . '.write(unicode(vim.eval("@@"), "utf-8"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> ]p :' . s:py . ' ' . b:ConqueTerm_Var . '.write(unicode(vim.eval("@@"), "utf-8"))<CR>a'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> [p :' . s:py . ' ' . b:ConqueTerm_Var . '.write(unicode(vim.eval("@@"), "utf-8"))<CR>a'
    else
        sil exe 'n' . map_modifier . 'map <silent> <buffer> p'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> P'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> ]p'
        sil exe 'n' . map_modifier . 'map <silent> <buffer> [p'
    endif
    if has('gui_running') == 1
        if l:action == 'start'
            sil exe 'i' . map_modifier . 'map <buffer> <S-Insert> <Esc>:' . s:py . ' ' . b:ConqueTerm_Var . ".write(unicode(vim.eval('@+'), 'utf-8'))<CR>a"
        else
            sil exe 'i' . map_modifier . 'map <buffer> <S-Insert>'
        endif
    endif
    " }}}

    " disable other normal mode keys which insert text {{{
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
    " }}}

    " pause or resume terminal input {{{
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
    " }}}

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
    sil exe s:py . ' ' . g:ConqueTerm_Var . '.paste_selection()'

    " reset original values
    let @@ = reg_save
    sil exe 'set switchbuf=' . sb_save

    " scroll buffer left
    startinsert!
    normal 0zH
endfunction "}}}

" read from all known conque buffers
function! conque_term#read_all() "{{{
    " don't run this if we're in a conque buffer
    if exists('b:ConqueTerm_Var')
        return
    endif

    try
        for i in range(1, g:ConqueTerm_Idx - 1)
            execute s:py . ' ' ConqueTerm_' . string(i) . '.read(1, False)'
        endfor
    catch
        " probably a deleted buffer
    endtry

    " restart updatetime
    call feedkeys("f\e")
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
function! conque_term#on_focus(...) " {{{

    let startup = get(a:000, 0, 0)

    " Disable NeoComplCache. It has global hooks on CursorHold and CursorMoved :-/
    let s:NeoComplCache_WasEnabled = exists(':NeoComplCacheLock')
    if s:NeoComplCache_WasEnabled == 2
        NeoComplCacheLock
    endif
 
    " set poll interval to 50ms   
    let s:save_updatetime = &updatetime
    set updatetime=50

    if startup == 0
        sil exe s:py . ' ' . g:ConqueTerm_Var . '.resume()'
    endif

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
 
    sil exe s:py . ' ' . g:ConqueTerm_Var . '.idle()'

    " reset poll interval
    if g:ConqueTerm_ReadUnfocused == 1
        set updatetime=1000
    elseif exists('s:save_updatetime')
        exe 'set updatetime=' . s:save_updatetime
    else
        set updatetime=2000
    endif
endfunction " }}}

" bell event (^G)
function! conque_term#bell() " {{{
    echohl WarningMsg | echomsg "BELL!" | echohl None
endfunction " }}}

" find python.exe in windows
function! conque_term#find_python_exe() " {{{

    " first check configuration for custom value
    if g:ConqueTerm_PyExe != '' && executable(g:ConqueTerm_PyExe)
        return g:ConqueTerm_PyExe
    endif

    let sys_paths = split($PATH, ';')

    " get exact python version
    sil exe ':' . s:py . ' import sys, vim'
    sil exe ':' . s:py . ' vim.command("let g:ConqueTerm_PyVersion = " + str(sys.version_info[0]) + str(sys.version_info[1]))'

    " ... and add to path list
    call add(sys_paths, 'C:\Python' . g:ConqueTerm_PyVersion)
    call reverse(sys_paths)

    " check if python.exe is in paths
    for path in sys_paths
        let cand = path . '\' . 'python.exe'
        if executable(cand)
            return cand
        endif
    endfor

    echohl WarningMsg | echomsg "Unable to find python.exe, see :help ConqueTerm_PythonExe for more information" | echohl None

    return ''

endfunction " }}}

" find autoload/conque_term.vim for windows
function! conque_term#find_conque_term_vim() " {{{

    " search config path
    if g:ConqueTerm_AutoloadDir != ''
        let ct_vim = globpath(g:ConqueTerm_AutoloadDir, "**/autoload/conque_sole_communicator.py")
        if ct_vim != ''
            return ct_vim
        endif
    endif

    " then search vim paths
    let ct_vim = globpath(&rtp, "**/autoload/conque_sole_communicator.py")
    if ct_vim == ''
        echohl WarningMsg | echomsg "Unable to find conque_term.vim" | echohl None
    endif

    return ct_vim

endfunction " }}}


" **********************************************************************************************************
" **** PYTHON **********************************************************************************************
" **********************************************************************************************************

let conque_py_dir = substitute(findfile('autoload/conque_term.vim', &rtp), 'conque_term.vim', '', '')
exec s:py . "file " . conque_py_dir . "conque_globals.py"
exec s:py . "file " . conque_py_dir . "Conque.py"
exec s:py . "file " . conque_py_dir . "ConqueScreen.py"
exec s:py . "file " . conque_py_dir . "ConqueSubprocess.py"
if s:platform == 'dos'
    exec s:py . "file " . conque_py_dir . "ConqueSole.py"
    exec s:py . "file " . conque_py_dir . "ConqueSoleWrapper.py"
endif

