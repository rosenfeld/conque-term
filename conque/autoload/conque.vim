" FILE:     autoload/conque.vim
" AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
"           Shougo Matsushita <Shougo.Matsu@gmail.com> (original VimShell)
"           Yukihiro Nakadaira (vimproc)
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE: {{{
" Conque - pty interaction in Vim
" Copyright (C) 2009 Nico Raffo 
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

" Open a command in Conque.
" This is the root function that is called from Vim to start up Conque.
function! conque#open(...) "{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])

    call s:log.debug('<open command>')
    call s:log.debug('command: ' . command)

    " bare minimum validation
    if empty(command)
        echohl WarningMsg | echomsg "No command found" | echohl None
        call s:log.warn('command not found: ' . command)
        return 0
    else
        let l:cargs = split(command, '\s')
        if !executable(l:cargs[0])
            echohl WarningMsg | echomsg "Not an executable" | echohl None
            call s:log.warn('command not found: ' . l:cargs[0])
            return 0
        endif
    endif

    " configure shell buffer display and key mappings
    call s:set_buffer_settings(command, hooks)

    " set global environment variables
    let $COLUMNS = winwidth(0) - 8
    let $LINES = winheight(0)

    " open command
    try
        let b:subprocess = subprocess#new()
        call b:subprocess.open(command, {'TERM': g:Conque_TERM, 'CONQUE': 1, 'EDITOR': 'unsupported'})
        call s:log.info('opening command: ' . command . ' with ptyopen')
    catch 
        echohl WarningMsg | echomsg "Unable to open command: " . command | echohl None
        return 0
    endtry

    " init variables.
    let b:prompt_history = {}
    let b:current_command = ''
    let b:write_clear = 0

    " save this buffer info
    let g:Conque_BufNr = bufnr("%")
    let g:Conque_BufName = bufname("%")
    let g:Conque_Idx += 1

    " read welcome message from command, give it a full second to start up
    call conque#read(500)

    call s:log.debug('</open command>')

    startinsert!
    return 1
endfunction "}}}

" buffer settings, layout, key mappings, and auto commands
function! s:set_buffer_settings(command, pre_hooks) "{{{
    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        execute h
    endfor

    execute "edit " . substitute(a:command, ' ', '\\ ', 'g') . "\\ -\\ " . g:Conque_Idx
    setlocal buftype=nofile  " this buffer is not a file, you can't save it
    setlocal nonumber        " hide line numbers
    setlocal foldcolumn=0    " reasonable left margin
    setlocal nowrap          " default to no wrap (esp with MySQL)
    setlocal noswapfile      " don't bother creating a .swp file
    set scrolloff=0          " don't use buffer lines. it makes the 'clear' command not work as expected
    setfiletype conque       " useful
    execute "setlocal syntax=".g:Conque_Syntax
    setlocal foldmethod=manual

    " run the current command
    nnoremap <buffer><silent><CR>        :<C-u>call conque#run()<CR>
    inoremap <buffer><silent><CR>        <ESC>:<C-u>call conque#run()<CR>
    nnoremap <buffer><silent><C-j>       <ESC>:<C-u>call conque#run()<CR>
    inoremap <buffer><silent><C-j>       <ESC>:<C-u>call conque#run()<CR>
    " don't backspace over prompt
    inoremap <buffer><silent><expr><BS>  <SID>delete_backword_char()
    " clear current line
    inoremap <buffer><silent><C-u>       <ESC>:<C-u>call conque#kill_line()<CR>
    " tab complete
    inoremap <buffer><silent><Tab>       <ESC>:<C-u>call <SID>tab_complete()<CR>
    nnoremap <buffer><silent><Tab>       <ESC>:<C-u>call <SID>tab_complete()<CR>
    " previous/next command
    inoremap <buffer><silent><Up>        <ESC>:<C-u>call <SID>previous_command()<CR>
    inoremap <buffer><silent><Down>      <ESC>:<C-u>call <SID>next_command()<CR>
    inoremap <buffer><silent><C-p>       <ESC>:<C-u>call <SID>previous_command()<CR>
    inoremap <buffer><silent><C-n>       <ESC>:<C-u>call <SID>next_command()<CR>
    " interrupt
    nnoremap <buffer><silent><C-c>       :<C-u>call conque#sigint()<CR>
    inoremap <buffer><silent><C-c>       <ESC>:<C-u>call conque#sigint()<CR>
    " escape
    nnoremap <buffer><silent><C-e>       :<C-u>call conque#escape()<CR>
    inoremap <buffer><silent><C-e>       <ESC>:<C-u>call conque#escape()<CR>
    " eof
    nnoremap <buffer><silent><C-d>       :<C-u>call conque#eof()<CR>
    inoremap <buffer><silent><C-d>       <ESC>:<C-u>call conque#eof()<CR>
    " suspend
    nnoremap <buffer><silent><C-z>       :<C-u>call conque#suspend()<CR>
    inoremap <buffer><silent><C-z>       <ESC>:<C-u>call conque#suspend()<CR>
    " quit
    nnoremap <buffer><silent><C-\>       :<C-u>call conque#quit()<CR>
    inoremap <buffer><silent><C-\>       <ESC>:<C-u>call conque#quit()<CR>
    " clear
    nnoremap <buffer><silent><C-l>       :<C-u>call conque#send('clear')<CR>
    inoremap <buffer><silent><C-l>       <ESC>:<C-u>call conque#send('clear')<CR>
    " inject selected text into conque
	  vnoremap <silent> <F9> :<C-u>call conque#inject(visualmode(), 0)<CR>

    " handle unexpected closing of shell
    " passes HUP to main and all child processes
    augroup conque
        autocmd BufUnload <buffer>   call conque#hang_up()
    augroup END
endfunction "}}}

" controller to execute current line
function! conque#run() "{{{
    call s:log.debug('<keyboard triggered run>')
    call s:log.profile_start('run')

    " check if subprocess still exists
    if !exists('b:subprocess')
        return
    endif

    call s:log.debug('status: ' . string(b:subprocess.get_status()))

    " write current line to subprocess
    let l:write_status = conque#write(1)

    " if write was successful, read output
    if l:write_status == 1
        call conque#read(g:Conque_Read_Timeout)
        " special case
        if b:current_command == 'clear'
            normal Gzt
            startinsert!
        endif
    endif

    call s:log.profile_end('run')
    call s:log.debug('</keyboard triggered run>')
endfunction "}}}

" write current line to pty
function! conque#write(add_newline) "{{{
    call s:log.debug('<write>')
    call s:log.profile_start('write')

    " pull command from the buffer
    let l:in = s:get_command()

    " check for hijacked commands
    if a:add_newline && (l:in =~ '^man ' || l:in =~ '^vim\? ')
        call conque#special(l:in)
        return 0
    endif
    
    " run the command!
    try
        call s:log.debug('about to write command: "' . l:in . '" to pid')
        if a:add_newline == 1
            call s:subwrite(l:in . "\<NL>")
        else
            call s:subwrite(l:in)
        endif
    catch
        call s:log.warn('write fail: "' . l:in . '"')
        echohl WarningMsg | echomsg 'No process' | echohl None
        call conque#exit()
        return 0
    endtry
    
    " record command history
    let b:current_command = l:in

    normal! G$
    call s:log.profile_end('write')
    call s:log.debug('</write>')
    return 1
endfunction "}}}

" when we actually write a full command to the subprocess, occasionally we need to clear the input line first
" typically after command editing keystrokes such as for tab completion and history navigation
" XXX - hacky
function! s:subwrite(command) "{{{
    call s:log.profile_start('subwrite')
    if b:write_clear == 1 && b:subprocess.get_library_name() == 'pty'
        call s:log.debug('must cleeeeeeeeeeeeeeeeeeeeeear')
        call conque#kill_line()
        let b:write_clear = 0
    endif
    call b:subprocess.write(a:command)
    call s:log.profile_end('subwrite')
endfunction "}}}

" parse current line to remove prompt and return command.
" also manages multi-line commands.
function! s:get_command() "{{{
  call s:log.debug('<get_command>')
  let l:in = getline('.')

  if l:in == ''
    " Do nothing.

  elseif exists("b:prompt_history['".line('.')."']")
    let l:in = l:in[len(b:prompt_history[line('.')]) : ]

  else
    " Maybe line numbering got disrupted, search for a matching prompt.
    let l:prompt_search = 0
    for pnr in reverse(sort(keys(b:prompt_history)))
      let l:prompt_length = len(b:prompt_history[pnr])
      " In theory 0 length or ' ' prompt shouldn't exist, but still...
      if l:prompt_length > 0 && b:prompt_history[pnr] != ' '
        " Does the current line have this prompt?
        if l:in[0 : l:prompt_length - 1] == b:prompt_history[pnr]
          let l:in = l:in[l:prompt_length : ]
          let l:prompt_search = pnr
        endif
      endif
    endfor

    " Still nothing? Maybe a multi-line command was pasted in.
    let l:max_prompt = max(keys(b:prompt_history)) " Only count once.
    if l:prompt_search == 0 && l:max_prompt < line('$')
    for i in range(l:max_prompt, line('$'))
      if i == l:max_prompt
        let l:in = getline(i)
        let l:in = l:in[len(b:prompt_history[i]) : ]
      else
        let l:in = l:in . "\n" . getline(i)
      endif
    endfor
      let l:prompt_search = l:max_prompt
    endif

    " Still nothing? We give up.
    if l:prompt_search == 0
      call s:log.warn('invalid input')
      echohl WarningMsg | echo "Invalid input." | echohl None
      normal! G$
      startinsert!
      return
    endif
  endif

  call s:log.debug('</get_command>')
  return l:in
endfunction "}}}

" read from pty and write to buffer
function! conque#read(timeout) "{{{
    call s:log.debug('<read>')
    call s:log.profile_start('read')

    call s:log.profile_start('subread')
    try
        let l:output = b:subprocess.read(a:timeout)
    catch
        call s:log.warn('read exception')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call s:log.profile_end('subread')

    call s:log.profile_start('printread')
    call s:log.debug('raw output: ' . string(l:output))
    if len(l:output) > 1 || l:output[0] != ''
        call s:print_buffer(l:output)
    endif
    call s:log.profile_end('printread')
    call s:log.profile_start('finishread')

    " ready to insert now
    normal! G$

    " record prompt used on this line
    let b:prompt_history[line('.')] = getline('.')

    startinsert!
    call s:log.profile_end('finishread')
    call s:log.profile_end('read')
    call s:log.debug('</read>')
endfunction "}}}

" read from pty and return output as string
function! conque#read_return_raw(timeout) "{{{
    call s:log.debug('<read return raw>')

    try
        let l:output = b:subprocess.read(a:timeout)
    catch
        call s:log.warn('read return raw ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry

    " ready to insert now
    call s:log.debug(string(l:output))
    call s:log.debug('</read return raw>')
    return l:output
endfunction "}}}

" parse output from pty and update buffer
function! s:print_buffer(read_lines) "{{{
    call s:log.profile_start('print_buffer')
    " clear out our command
    if exists("b:prompt_history['".line('$')."']")
        call s:log.debug('found hist ' . b:prompt_history[line('$')])
        call setline(line('$'), b:prompt_history[line('$')])
    endif

    " maybe put this in config later
    let l:pos = 1
    for eline in a:read_lines
        " write to buffer
        call s:log.debug('about to write: ' . eline)
        if l:pos == 1
            "let eline = substitute(eline, '^\b\+', '', 'g')
            call setline(line('$'), getline(line('$')) . eline)
        else
            call append(line('$'), eline)
        endif

        " translate terminal escape sequences
        normal! G$
        call subprocess#shell_translate#process_current_line()

        let l:pos += 1
        normal G
    endfor

    redraw
    call s:log.profile_start('print_buffer_redraw')
    call s:log.profile_end('print_buffer_redraw')
    call s:log.profile_end('print_buffer')
endfunction "}}}

function! conque#on_exit() "{{{
    call s:log.debug('<on_exit>')
    augroup conque 
        autocmd! * <buffer>
    augroup END

    unlet b:subprocess

    call s:log.debug('</on_exit>')
endfunction "}}}

" kill process pid with SIGTERM
" since most shells ignore SIGTERM there's a good chance this will do nothing
function! conque#exit() "{{{
    call s:log.debug('<exit>')

    if b:subprocess.get_status() == 1
        " Kill process.
        try
            " 15 == SIGTERM
            call b:subprocess.close()
        catch /No such process/
        endtry
    endif

    call append(line('$'), '*Exit*')
    call conque#on_exit()
    normal G
    call s:log.debug('</exit>')
endfunction "}}}

" kill process pid with SIGKILL
" undesirable, but effective
function! conque#force_exit() "{{{
    call s:log.debug('<force exit>')

    if b:subprocess.get_status() == 1
        " Kill processes.
        try
            " 9 == SIGKILL
            call b:subprocess.kill()
            call append(line('$'), '*Killed*')
        catch /No such process/
        endtry
    endif

    call conque#on_exit()
    normal G
    call s:log.debug('</force exit>')
endfunction "}}}

" kill process pid with SIGHUP
" this gets called if the buffer is unloaded before the program has been exited
" it should pass the signall to all children before killing the parent process
function! conque#hang_up() "{{{
    call s:log.debug('<hang up>')

    if !exists('b:subprocess')
        return
    endif

    if b:subprocess.get_status() == 1
        " Kill processes.
        try
            " 1 == HUP
            call b:subprocess.hang_up()
            call append(line('$'), '*Killed*')
        catch /No such process/
        endtry
    endif

    call s:log.debug('</hang up>')
    call conque#on_exit()
endfunction "}}}

" process command editing key strokes. History and tab completion being the most common.
function! s:process_command_edit(char) "{{{
    let l:prompt = b:prompt_history[line('$')]
    let l:working_line = getline('.')
    let l:working_command = l:working_line[len(l:prompt) : len(l:working_line)]

    if b:write_clear == 1 && l:working_command == b:edit_command
        call b:subprocess.write(a:char)
    elseif b:write_clear == 0
        call s:log.debug('first command edit ' . l:working_command . a:char)
        call b:subprocess.write(l:working_command . a:char)
        call setline(line('$'), l:prompt)
    elseif l:working_command[0 : len(b:edit_command) - 1] == b:edit_command
        call s:log.debug('additional command edit ' . l:working_command . a:char)
        call b:subprocess.write(l:working_command[len(b:edit_command) : ] . a:char)
        call setline(line('$'), l:prompt . b:edit_command)
    else
        call s:log.debug('fresh command edit ' . l:working_command . a:char)
        call s:log.debug('edit command ' . b:edit_command)
        call b:subprocess.write("\<C-u>" . l:working_command . a:char)
        call setline(line('$'), l:prompt . b:edit_command)
    endif
    let l:resp = conque#read_return_raw(3)
    call s:log.debug(string(l:resp))
    call s:log.debug('well before: ' . getline(line('$')))
    for i in range(len(l:resp))
        if i == 0
            call setline(line('$'), getline(line('$')) . l:resp[i])
        else
            call append(line('$'), l:resp[i])
        endif
        normal! G$
        call subprocess#shell_translate#process_current_line()
    endfor

    call s:log.debug('before: ' . getline(line('$')))

    call s:log.debug('after: ' . getline(line('$'))) 
    let b:prompt_history[line('$')] = l:prompt

    let l:working_line = getline('.')
    let b:edit_command = l:working_line[len(l:prompt) : ]

    let b:write_clear = 1
    normal G$
    startinsert!
    return
endfunction " }}}

" load previous command
function! s:previous_command() "{{{
    call s:process_command_edit("\e[A")
endfunction "}}}

" load next command
function! s:next_command() "{{{
    call s:process_command_edit("\e[B")
endfunction "}}}

" catch <BS> to prevent deleting prompt
" if tab completion has initiated, prevent deleting partial command already sent to pty
function! s:delete_backword_char() "{{{
    " identify prompt
    if exists('b:prompt_history[line(".")]')
        let l:prompt = b:prompt_history[line('.')]
    else
        return "\<BS>"
    endif
    
    if getline(line('.')) != l:prompt
        return "\<BS>"
    else
        return ""
    endif
endfunction "}}}

" tab complete current line
function! s:tab_complete() "{{{
    " pull more data first
    if g:Conque_Tab_More == 1 && exists("b:prompt_history[".line('.')."]") && b:prompt_history[line('.')] == getline(line('.'))
        call conque#read(5)
        return
    endif

    call s:process_command_edit("\<C-i>")
endfunction "}}}

" implement <C-u>
" especially useful to clear a tab completion line already sent to pty
function! conque#kill_line() "{{{
    " send <C-u> to pty
    try
        call b:subprocess.write("\<C-u>")
    catch
        call s:log.warn('kill line ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry

    " we are throwing away the output here, assuming <C-u> never fails to do as expected
    let l:hopefully_just_backspaces = conque#read_return_raw(0.5)

    " restore empty prompt
    call setline(line('.'), b:prompt_history[line('.')])
    normal! G$
    startinsert!
endfunction "}}}

" implement <C-c>
" should send SIGINT to proc
function! conque#sigint() "{{{
    call s:log.debug('<sigint>')
    " send <C-c> to pty
    try
        call b:subprocess.write("\<C-c>")
    catch
        call s:log.warn('sigint ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call conque#read(500)
    call s:log.debug('</sigint>')
endfunction "}}}

" implement <Esc>
" should send <Esc> to proc
" Useful if Vim is launched inside of conque
function! conque#escape() "{{{
    call s:log.debug('<escape>')
    " send <Esc> to pty
    try
        call b:subprocess.write("\<Esc>")
    catch
        call s:log.warn('escape exception')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call conque#read(500)
    call s:log.debug('</escape>')
endfunction "}}}

" implement <C-z>
" should suspend foreground process
function! conque#suspend() "{{{
    call s:log.debug('<suspend>')
    " send <C-z> to pty
    try
        call b:subprocess.write("\<C-z>")
    catch
        call s:log.warn('suspend ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call conque#read(500)
    call s:log.debug('</suspend>')
endfunction "}}}

" implement <C-d>
" should send EOF
function! conque#eof() "{{{
    call s:log.debug('<eof>')
    " send <C-d> to pty
    try
        call b:subprocess.write("\<C-d>")
    catch
        call s:log.warn('eof ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call conque#read(500)
    call s:log.debug('</eof>')
endfunction "}}}

" implement <C-\>
" should send QUIT
function! conque#quit() "{{{
    call s:log.debug('<quit>')
    " send <C-\> to pty
    try
        call b:subprocess.write("\<C-\\>")
    catch
        call s:log.warn('quit ex')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry
    call conque#read(500)
    call s:log.debug('</quit>')
endfunction "}}}

" commands with special implementations
function! conque#special(command) "{{{
    call append(line('$'), b:prompt_history[max(keys(b:prompt_history))])
    normal G$

    if a:command =~ '^man '
        let split_cmd = "split " . substitute(a:command, '\W', '_', 'g')
        call s:log.debug(split_cmd)
        execute split_cmd
        setlocal buftype=nofile
        setlocal nonumber
        setlocal noswapfile
        let cmd = 'read !' . substitute(a:command, '^man ', 'man -P cat ', '')
        call s:log.debug(cmd)
        execute cmd

        " strip backspaces out of output
        try
            while search('\b', 'wncp') > 0
                silent execute '%s/[^\b]\b//g'
                silent execute '%s/^\b//g'
            endwhile
        catch
        endtry
        normal gg0
    elseif a:command =~ '^vim\? '
        let filename = substitute(a:command, '^vim\? ', '', '')
        let filename = b:subprocess.get_env_var('PWD') . '/' . filename
        let split_cmd = "split " . filename
        call s:log.debug(split_cmd)
        execute split_cmd
    endif
endfunction "}}}

" inject command from another buffer
function! conque#inject(type, execute) "{{{
    let reg_save = @@

    " yank current selection
    silent execute "normal! `<" . a:type . "`>y"

    let @@ = substitute(@@, '^[\r\n]*', '', '')
    let @@ = substitute(@@, '[\r\n]*$', '', '')

    execute ":sb " . g:Conque_BufName
    normal! G$p
    normal! G$
    startinsert!

    if a:execute == 1
        call conque#run()
    endif

    let @@ = reg_save
endfunction "}}}

" write command to conque
function! conque#send(command) "{{{
    call setline(line('$'), getline(line('$')) . a:command)
    call conque#run()
endfunction "}}}

" Logging {{{
if exists('g:Conque_Logging') && g:Conque_Logging == 1
    let s:log = log#getLogger(expand('<sfile>:t'))
    let s:profiles = {}
    function! s:log.profile_start(name)
        let s:profiles[a:name] = reltime()
    endfunction
    function! s:log.profile_end(name)
        let time = reltimestr(reltime(s:profiles[a:name]))
        call s:log.debug('PROFILE "' . a:name . '": ' . time)
    endfunction
else
    let s:log = {}
    function! s:log.debug(msg)
    endfunction
    function! s:log.info(msg)
    endfunction
    function! s:log.warn(msg)
    endfunction
    function! s:log.error(msg)
    endfunction
    function! s:log.fatal(msg)
    endfunction
    function! s:log.profile_start(name)
    endfunction
    function! s:log.profile_end(name)
    endfunction
endif
" }}}

" vim: foldmethod=marker
