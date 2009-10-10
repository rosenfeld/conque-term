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
function! conque#open(...)"{{{
    let command = get(a:000, 0, '')
    let hooks   = get(a:000, 1, [])

    call s:log.debug('<open command>')
    call s:log.debug('command: ' . command)

    if empty(command)
        echohl WarningMsg | echomsg "No command found" | echohl None
        call s:log.warn('command not found: ' . command)
        return 0
    endif

    " configure shell buffer display and key mappings
    call s:set_buffer_settings(command, hooks)

    " set global environment variables
    call s:set_environment()

    " open command
    try
        let b:subprocess = subprocess#new()
        call b:subprocess.open(command)
        call s:log.info('opening command: ' . command . ' with ptyopen')
    catch 
        let l:error = printf('Unable to open command: ', command)
        echohl WarningMsg | echomsg l:error | echohl None
        return 0
    endtry

    " Set variables.
    let b:command_history = []
    let b:prompt_history = {}
    let b:fold_history = {}
    let b:current_command = ''
    let b:command_position = 0

    " read welcome message from command
    call s:read(500)

    call s:log.debug('</open command>')

    startinsert!
    return 1
endfunction"}}}

" set shell environment vars
" XXX - probably should delegate this to logic in .bashrc?
function! s:set_environment()"{{{
    let $TERM = "dumb"
    "let $TERMCAP = "COLUMNS=" . winwidth(0)
    let $COLUMNS = winwidth(0) - 8 " these get reset by terminal anyway
    let $LINES = winheight(0)
    
    call s:log.debug('<env>')
    call s:log.debug('winwidth: ' .winwidth(0) . ' winheight: ' . winheight(0))
    call s:log.debug('</env>')
endfunction"}}}

" buffer settings, layout, key mappings, and auto commands
function! s:set_buffer_settings(command, pre_hooks)"{{{
    " optional hooks to execute, e.g. 'split'
    for h in a:pre_hooks
        execute h
    endfor

    execute "edit " . substitute(a:command, ' ', '_', 'g') . "@" . string(bufnr('$', 1)+1)
    setlocal buftype=nofile  " this buffer is not a file, you can't save it
    setlocal nonumber        " hide line numbers
    setlocal foldcolumn=1    " reasonable left margin
    setlocal nowrap          " default to no wrap (esp with MySQL)
    setlocal noswapfile      " don't bother creating a .swp file
    setfiletype conque       " useful
    execute "setlocal syntax=".g:Conque_Syntax
    setlocal foldmethod=manual

    " run the current command
    nnoremap <buffer><silent><CR>        :<C-u>call conque#run()<CR>
    inoremap <buffer><silent><CR>        <ESC>:<C-u>call conque#run()<CR>
    " don't backspace over prompt
    inoremap <buffer><silent><expr><BS>  <SID>delete_backword_char()
    " clear current line
    inoremap <buffer><silent><C-u>       <ESC>:<C-u>call conque#kill_line()<CR>
    " tab complete
    inoremap <buffer><silent><Tab>       <ESC>:<C-u>call <SID>tab_complete()<CR>
    " previous/next command
    inoremap <buffer><silent><Up>        <ESC>:<C-u>call <SID>previous_command()<CR>
    inoremap <buffer><silent><Down>      <ESC>:<C-u>call <SID>next_command()<CR>
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

    " handle unexpected closing of shell
    " passes HUP to main and all child processes
    augroup conque
        autocmd BufUnload <buffer>   call conque#hang_up()
    augroup END
endfunction"}}}

" controller to execute current line
function! conque#run()"{{{
    call s:log.debug('<keyboard triggered run>')
    if !exists('b:subprocess')
        return
    endif

    call s:log.debug('status: ' . string(b:subprocess.get_status()))

    call conque#write(1)
    call s:read(g:Conque_Read_Timeout)

    call s:log.debug('</keyboard triggered run>')
endfunction"}}}

" execute current line, but return output as string instead of printing to buffer
function! conque#run_return(timeout)"{{{
    call s:log.debug('<keyboard triggered run return>')
    call conque#write(0)
    let l:output = conque#read_return_raw(a:timeout)
    call s:log.debug('</keyboard triggered run return>')
    let l:output_string = join(l:output, "\n")

    " strip bells, leave whistles
    if l:output_string =~ nr2char(7)
        let l:output_string = substitute(l:output_string, nr2char(7), '', 'g')
        echohl WarningMsg | echomsg "!!!BELL!!!" | echohl None
    endif

    " strip backspaces out of output
    while l:output_string =~ '\b'
        let l:output_string = substitute(l:output_string, '[^\b]\b', '', 'g')
        let l:output_string = substitute(l:output_string, '^\b', '', 'g')
    endwhile

    return l:output_string
endfunction"}}}

" write current line to pty
function! conque#write(add_newline)"{{{
    call s:log.debug('<write>')

    " pull command from the buffer
    let l:in = s:get_command()
    
    " waiting
    if l:in == '...'
        call append(line('$'), '...')
        return
    endif

    " run the command!
    try
        call s:log.debug('about to write command: "' . l:in . '" to pid')
        if a:add_newline == 1
            call b:subprocess.write(l:in . "\<NL>")
        else
            call b:subprocess.write(l:in)
        endif
    catch
        call s:log.warn('write fail: "' . l:in . '"')
        echohl WarningMsg | echomsg 'No process' | echohl None
        call conque#exit()
        return
    endtry
    
    " record command history
    let l:hc = ''
    if exists("b:prompt_history['".line('.')."']")
        call s:log.debug('command history from getline')
        let l:hc = getline('.')
        let l:hc = l:hc[len(b:prompt_history[line('.')]) : ]
    else
        call s:log.debug('command history from l:in')
        let l:hc = l:in
    endif
    if l:hc != '' && l:hc != '...' && l:hc !~ '\t$'
        let b:fold_history[line('.')] = 1
        call add(b:command_history, l:hc)
    endif
    let b:current_command = l:in
    let b:command_position = 0

    " we're doing something
    if a:add_newline == 1
        if g:Conque_Use_Filler == 1
            call append(line('$'), '...')
        else
            call append(line('$'), '')
        endif
    endif

    normal! G$
    call s:log.debug('</write>')
endfunction"}}}

" parse current line to remove prompt and return command.
" also manages multi-line commands.
function! s:get_command()"{{{
  call s:log.debug('<get_command>')
  let l:in = getline('.')

  if l:in == ''
    " Do nothing.

  elseif l:in == '...'
    " Working

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
        let l:in = l:in . getline(i)
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
endfunction"}}}

" read from pty and write to buffer
function! s:read(timeout)"{{{
    call s:log.debug('<read>')

    try
        let l:output = b:subprocess.read(a:timeout)
    catch
        call s:log.warn('read exception')
        echohl WarningMsg | echomsg 'no process' | echohl None
        call conque#exit()
        return
    endtry

    call s:print_buffer(l:output)
    redraw

    " record prompt used on this line
    let b:prompt_history[line('.')] = getline('.')

    " ready to insert now
    normal! G$
    startinsert!
    call s:log.debug('</read>')
endfunction"}}}

" read from pty and return output as string
function! conque#read_return_raw(timeout)"{{{
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
    call s:log.debug('</read return raw>')
    return l:output
endfunction"}}}

" parse output from pty and update buffer
function! s:print_buffer(read_lines)"{{{
    let l:string = join(a:read_lines, "\n")

    if l:string == ''
        return
    endif

    " Convert encoding for system().
    let l:string = iconv(l:string, 'utf-8', &encoding) 

    " check for Bells
    if l:string =~ nr2char(7)
        let l:string = substitute(l:string, nr2char(7), '', 'g')
        echohl WarningMsg | echomsg "For shame!" | echohl None
    endif

    " strip backspaces out of output
    while l:string =~ '\b'
        let l:string = substitute(l:string, '[^\b]\b', '', 'g')
        let l:string = substitute(l:string, '^\b', '', 'g')
    endwhile

    " Strip <CR>.
    let l:string = substitute(substitute(l:string, '\r', '', 'g'), '\n$', '', '')
    let l:lines = split(l:string, '\n', 1)

    " strip off command repeated by the ECHO terminal flag
    if l:lines[0] == b:current_command
        let l:lines = l:lines[1:]
    " will usually get rid of ugly trash produced by ECHO + super long commands
    elseif len(b:current_command) > winwidth(0) - 20 && l:lines[0][0:20] == b:current_command[0:20] && l:lines[0][-5:] == b:current_command[-5:]
        let l:lines = l:lines[1:]
    endif

    " special case: first line in buffer
    if line('$') == 1 && empty(getline('$'))
        call setline(line('$'), l:lines[0])
        let l:lines = l:lines[1:]
    endif

    " write to buffer
    let l:pos = 1
    for eline in l:lines
        if l:pos == 1
            call setline(line('$'), eline)
        else
            call append(line('$'), eline)
        endif
        call conque#highlight()
        let l:pos = l:pos + 1
    endfor

    " Set cursor.
    normal! G$

    " fold output
    if g:Conque_Folding == 1
        if !exists('b:fold_history[line("$")-1]') && max(keys(b:fold_history)) < line("$")-1 && len(keys(b:fold_history)) > 0 && getline(line('$')) != getline(line('$')-1)
            let l:fold_command = max(keys(b:fold_history)) . "," . (line("$")-1) . "fo"
            call s:log.debug('fold command: ' . l:fold_command)
            execute l:fold_command
            normal! kzoG$
        endif
    endif
endfunction"}}}

function! conque#on_exit() "{{{
    call s:log.debug('<on_exit>')
    augroup conque 
        autocmd! * <buffer>
    augroup END

    setfiletype sh
    unlet b:subprocess

    call s:log.debug('</on_exit>')
endfunction "}}}

" kill process pid with SIGTERM
" since most shells ignore SIGTERM there's a good chance this will do nothing
function! conque#exit()"{{{
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
endfunction"}}}

" kill process pid with SIGKILL
" undesirable, but effective
function! conque#force_exit()"{{{
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
endfunction"}}}

" kill process pid with SIGHUP
" this gets called if the buffer is unloaded before the program has been exited
" it should pass the signall to all children before killing the parent process
function! conque#hang_up()"{{{
    call s:log.debug('<hang up>')

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
endfunction"}}}

" load previous command
" XXX - we should probably use native history instead, although it's slower
function! s:previous_command()"{{{
    " If this is the first up arrow use, save what's been typed in so far.
    if b:command_position == 0
        let b:current_working_command = strpart(getline('.'), len(b:prompt_history[line('.')]))
    endif
    " If there are no more previous commands.
    if len(b:command_history) == b:command_position
        echohl WarningMsg | echomsg "End of history" | echohl None
        startinsert!
        return
    endif
    let b:command_position = b:command_position + 1
    let l:prev_command = b:command_history[len(b:command_history) - b:command_position]
    call setline(line('.'), b:prompt_history[max(keys(b:prompt_history))] . l:prev_command)
    startinsert!
endfunction"}}}

" load next command
" XXX - we should probably use native history instead, although it's slower
function! s:next_command()"{{{
    " If we're already at the last command.
    if b:command_position == 0
        echohl WarningMsg | echomsg "End of history" | echohl None
        startinsert!
        return
    endif
    let b:command_position = b:command_position - 1
    " Back at the beginning, put back what had been typed.
    if b:command_position == 0
        call setline(line('.'), b:prompt_history[max(keys(b:prompt_history))] . b:current_working_command)
        startinsert!
        return
    endif
    let l:next_command = b:command_history[len(b:command_history) - b:command_position]
    call setline(line('.'), b:prompt_history[max(keys(b:prompt_history))] . l:next_command)
    startinsert!
endfunction"}}}

" catch <BS> to prevent deleting prompt
" if tab completion has initiated, prevent deleting partial command already sent to pty
function! s:delete_backword_char()"{{{
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
endfunction"}}}

" tab complete current line
" TODO: integrate multiple options with Vim auto-complete menu?
" XXX XXX XXX: The stupidity of this function is spiraling out of control
function! s:tab_complete()"{{{
    " this stuff only really works with pty
    if b:subprocess.get_library_name() != 'pty'
        echohl WarningMsg | echomsg "Tab complete disabled when using 'popen' library" | echohl None
        return
    endif

    " Insert <TAB>.
    if exists('b:tab_complete_history[line(".")]')
        let l:prompt = b:tab_complete_history[line('.')]
    elseif exists('b:prompt_history[line(".")]')
        let l:prompt = b:prompt_history[line('.')]
    else
        let l:prompt = ''
    endif
    call s:log.debug('prompt is ' . l:prompt)

    if !exists('b:tab_count')
        let b:tab_count = 1
    endif

    let l:working_line = getline('.')
    let l:working_command = l:working_line[len(l:prompt) : len(l:working_line)]

    for i in range(1, b:tab_count)
        call setline(line('.'), getline('.') . "\<TAB>")
    endfor

    let l:candidate = conque#run_return(g:Conque_Tab_Timeout)
    call setline(line('.'), l:working_line)
    let l:extra = l:candidate
    let l:wlen = len(l:working_command)
    if l:candidate[0 : l:wlen - 1] == l:working_command
        let l:extra = l:candidate[l:wlen :]
    endif

    call s:log.debug('tab complete candidate: "' . l:extra . '" == "' . nr2char(7) . '"')
    if l:extra == nr2char(7) || l:extra == ''
        call s:log.debug('tab complete miss')
        call setline(line('.'), l:working_line)
        "let b:tab_complete_history[line('.')] = getline(line('.'))
        startinsert!
        echohl WarningMsg | echomsg "No completion found" | echohl None
        call b:subprocess.write("\<C-u>")
        let l:throwaway = conque#read_return_raw(0.001)
        let b:prompt_history[line('$')] = l:prompt
        let b:tab_count = 2
        return
    endif

    let b:tab_count = 1

    let l:extra = substitute(l:extra, '\r', '', 'g')
    let l:extra_lines = split(l:extra, '\n', 1)

    " automatically squash extended listing
    if l:extra =~ '(y or n)$'
        call append(line('$'), l:extra_lines)
        call append(line('$'), '... Conque has kill extended listing until a later version ...')
        call b:subprocess.write("n")
        call b:subprocess.write("\<C-u>")
        let l:throwaway = conque#read_return_raw(0.001)
        call append(line('$'), l:working_line)
        let b:prompt_history[line('$')] = l:prompt
        normal G$
        startinsert!
        return
    endif

    let l:pos = 1
    for l:line in l:extra_lines
        if l:pos == 1
            call setline(line('$'), getline(line('$')) . l:line)
        else
            call append(line('$'), l:line)
        endif
        let l:pos = l:pos + 1
    endfor

    "let b:tab_complete_history[line('$')] = getline(line('$'))

    let l:last_line = getline(line('$'))
    call s:log.debug("-->".l:last_line."=".l:working_line."<--")
    "if l:last_line =~ '^' . l:working_line
        call s:log.debug('ayay')
        call b:subprocess.write("\<C-u>")
        let l:throwaway = conque#read_return_raw(0.001)
        let b:prompt_history[line('$')] = l:prompt
    "endif

    normal G$
    startinsert!
endfunction"}}}

" implement <C-u>
" especially useful to clear a tab completion line already sent to pty
function! conque#kill_line()"{{{
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
endfunction"}}}

" implement <C-c>
" should send SIGINT to proc
function! conque#sigint()"{{{
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
    call s:read(500)
    call s:log.debug('</sigint>')
endfunction"}}}

" implement <Esc>
" should send <Esc> to proc
" Useful if Vim is launched inside of conque
function! conque#escape()"{{{
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
    call s:read(500)
    call s:log.debug('</escape>')
endfunction"}}}

" implement <C-z>
" should suspend foreground process
function! conque#suspend()"{{{
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
    call s:read(500)
    call s:log.debug('</suspend>')
endfunction"}}}

" implement <C-d>
" should send EOF
function! conque#eof()"{{{
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
    call s:read(500)
    call s:log.debug('</eof>')
endfunction"}}}

" implement <C-\>
" should send QUIT
function! conque#quit()"{{{
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
    call s:read(500)
    call s:log.debug('</quit>')
endfunction"}}}

" Copied directly from http://github.com/Shougo/vimshell/
function! conque#highlight()"{{{
    let l:escape_colors = [
                 \'#3c3c3c', '#ff6666', '#66ff66', '#ffd30a', '#1e95fd', '#ff13ff', '#1bc8c8', '#C0C0C0',
                 \'#686868', '#ff6666', '#66ff66', '#ffd30a', '#6699ff', '#f820ff', '#4ae2e2', '#ffffff'
                 \]

    let l:register_save = @"
    let l:color_table = [ 0x00, 0x5F, 0x87, 0xAF, 0xD7, 0xFF ]
    let l:grey_table = [
                \0x08, 0x12, 0x1C, 0x26, 0x30, 0x3A, 0x44, 0x4E, 
                \0x58, 0x62, 0x6C, 0x76, 0x80, 0x8A, 0x94, 0x9E, 
                \0xA8, 0xB2, 0xBC, 0xC6, 0xD0, 0xDA, 0xE4, 0xEE
                \]

    while search("\<ESC>\\[[0-9;]*m", 'c')
        normal! dfm

        let [lnum, col] = getpos('.')[1:2]
        if len(getline('.')) == col
            let col += 1
        endif
        let syntax_name = 'EscapeSequenceAt_' . bufnr('%') . '_' . lnum . '_' . col
        execute 'syntax region' syntax_name 'start=+\%' . lnum . 'l\%' . col . 'c+ end=+\%$+' 'contains=ALL'

        let highlight = ''
        for color_code in split(matchstr(@", '[0-9;]\+'), ';')
            if color_code == 0"{{{
                let highlight .= ' cterm=NONE ctermfg=NONE ctermbg=NONE gui=NONE guifg=NONE guibg=NONE'
            elseif color_code == 1
                let highlight .= ' cterm=BOLD gui=BOLD'
            elseif color_code == 4
                let highlight .= ' cterm=UNDERLINE gui=UNDERLINE'
            elseif color_code == 7
                let highlight .= ' cterm=REVERSE gui=REVERSE'
            elseif color_code == 8
                let highlight .= ' ctermfg=0 ctermbg=0 guifg=#000000 guibg=#000000'
            elseif 30 <= color_code && color_code <= 37 
                " Foreground color.
                let highlight .= printf(' ctermfg=%d guifg=%s', color_code - 30, l:escape_colors[color_code - 30])
            elseif color_code == 38
                " Foreground 256 colors.
                let l:color = split(matchstr(@", '[0-9;]\+'), ';')[2]
                if l:color >= 232
                    " Grey scale.
                    let l:gcolor = l:grey_table[(l:color - 232)]
                    let highlight .= printf(' ctermfg=%d guifg=#%02x%02x%02x', l:color, l:gcolor, l:gcolor, l:gcolor)
                elseif l:color >= 16
                    " RGB.
                    let l:gcolor = l:color - 16
                    let l:red = l:color_table[l:gcolor / 36]
                    let l:green = l:color_table[(l:gcolor % 36) / 6]
                    let l:blue = l:color_table[l:gcolor % 6]

                    let highlight .= printf(' ctermfg=%d guifg=#%02x%02x%02x', l:color, l:red, l:green, l:blue)
                else
                    let highlight .= printf(' ctermfg=%d guifg=%s', l:color, l:escape_colors[l:color])
                endif
                break
            elseif color_code == 39
                " TODO
            elseif 40 <= color_code && color_code <= 47 
                " Background color.
                let highlight .= printf(' ctermbg=%d guibg=%s', color_code - 40, l:escape_colors[color_code - 40])
            elseif color_code == 48
                " Background 256 colors.
                let l:color = split(matchstr(@", '[0-9;]\+'), ';')[2]
                if l:color >= 232
                    " Grey scale.
                    let l:gcolor = l:grey_table[(l:color - 232)]
                    let highlight .= printf(' ctermbg=%d guibg=#%02x%02x%02x', l:color, l:gcolor, l:gcolor, l:gcolor)
                elseif l:color >= 16
                    " RGB.
                    let l:gcolor = l:color - 16
                    let l:red = l:color_table[l:gcolor / 36]
                    let l:green = l:color_table[(l:gcolor % 36) / 6]
                    let l:blue = l:color_table[l:gcolor % 6]

                    let highlight .= printf(' ctermbg=%d guibg=#%02x%02x%02x', l:color, l:red, l:green, l:blue)
                else
                    let highlight .= printf(' ctermbg=%d guibg=%s', l:color, l:escape_colors[l:color])
                endif
                break
            elseif color_code == 49
                " TODO
            endif"}}}
        endfor
        if highlight != ''
            execute 'highlight link' syntax_name 'Normal'
            execute 'highlight' syntax_name highlight
        endif
    endwhile
    let @" = l:register_save
endfunction"}}}


" Logging {{{
if exists('g:Conque_Logging') && g:Conque_Logging == 1
    let s:log = log#getLogger(expand('<sfile>:t'))
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
endif
" }}}

" vim: foldmethod=marker
