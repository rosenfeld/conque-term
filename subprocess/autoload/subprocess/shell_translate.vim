" FILE:     autoload/subprocess/shell_translate.vim
" AUTHOR:   Nico Raffo <nicoraffo@gmail.com>
" MODIFIED: __MODIFIED__
" VERSION:  __VERSION__, for Vim 7.0
" LICENSE:  MIT License "{{{
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
"
" Translate shell escape/control characters into Vim formatting

" Control sequences {{{
let s:control_sequences = { 
\ 'G' : 'Bell',
\ 'H' : 'Backspace',
\ 'I' : 'Horizontal Tab',
\ 'J' : 'Line Feed or New Line',
\ 'K' : 'Vertical Tab',
\ 'L' : 'Form Feed or New Page',
\ 'M' : 'Carriage Return'
\ } 
" }}}

" Escape sequences {{{
let s:escape_sequences = [ 
\ {'code':'[\(\d*;\)*\d*m', 'name':'font', 'description':'Font manipulation'},
\ {'code':']0;.*'.nr2char(7), 'name':'title', 'description':'Change Title'},
\ {'code':'[\d*J', 'name':'clear_screen', 'description':'Clear in screen'},
\ {'code':'[\d*K', 'name':'clear_line', 'description':'Clear in line'},
\ {'code':'[\d*@', 'name':'add_spaces', 'description':'Add n spaces'},
\ {'code':'[\d*A', 'name':'cursor_up', 'description':'Cursor up n spaces'},
\ {'code':'[\d*B', 'name':'cursor_down', 'description':'Cursor down n spaces'},
\ {'code':'[\d*C', 'name':'cursor_right', 'description':'Cursor right n spaces'},
\ {'code':'[\d*D', 'name':'cursor_left', 'description':'Cursor back n spaces'},
\ {'code':'[\d*G', 'name':'cursor_to_column', 'description':'Move cursor to column'},
\ {'code':'[\d*H', 'name':'cursor', 'description':'Move cursor to x;y'},
\ {'code':'[\d*;\d*H', 'name':'cursor', 'description':'Move cursor to x;y'},
\ {'code':'[\d*L', 'name':'insert_lines', 'description':'Insert n lines'},
\ {'code':'[\d*M', 'name':'delete_lines', 'description':'Delete n lines'},
\ {'code':'[\d*P', 'name':'delete_chars', 'description':'Delete n characters'},
\ {'code':'[\d*d', 'name':'cusor_vpos', 'description':'Cursor vertical position'},
\ {'code':'[\d*;\d*f', 'name':'xy_pos', 'description':'x;y position'},
\ {'code':'[\d*g', 'name':'tab_clear', 'description':'Tab clear'},
\ {'code':'(.', 'name':'char_set', 'description':'Character set'},
\ {'code':'[?\d*l', 'name':'cursor_settings', 'description':'Misc cursor'},
\ {'code':'[?\d*h', 'name':'cursor_settings', 'description':'Misc cursor'}
\ ] 
" }}}

" Font codes {{{
let s:font_codes = {
\ '0': {'description':'Normal (default)', 'attributes': {'cterm':'NONE','ctermfg':'NONE','ctermbg':'NONE','gui':'NONE','guifg':'NONE','guibg':'NONE'}, 'normal':1},
\ '00': {'description':'Normal (default) alternate', 'attributes': {'cterm':'NONE','ctermfg':'NONE','ctermbg':'NONE','gui':'NONE','guifg':'NONE','guibg':'NONE'}, 'normal':1},
\ '1': {'description':'Bold', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':0},
\ '01': {'description':'Bold', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':0},
\ '4': {'description':'Underlined', 'attributes': {'cterm':'UNDERLINE','gui':'UNDERLINE'}, 'normal':0},
\ '04': {'description':'Underlined', 'attributes': {'cterm':'UNDERLINE','gui':'UNDERLINE'}, 'normal':0},
\ '5': {'description':'Blink (appears as Bold)', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':0},
\ '05': {'description':'Blink (appears as Bold)', 'attributes': {'cterm':'BOLD','gui':'BOLD'}, 'normal':0},
\ '7': {'description':'Inverse', 'attributes': {'cterm':'REVERSE','gui':'REVERSE'}, 'normal':0},
\ '07': {'description':'Inverse', 'attributes': {'cterm':'REVERSE','gui':'REVERSE'}, 'normal':0},
\ '8': {'description':'Invisible (hidden)', 'attributes': {'ctermfg':'0','ctermbg':'0','guifg':'#000000','guibg':'#000000'}, 'normal':0},
\ '08': {'description':'Invisible (hidden)', 'attributes': {'ctermfg':'0','ctermbg':'0','guifg':'#000000','guibg':'#000000'}, 'normal':0},
\ '22': {'description':'Normal (neither bold nor faint)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':1},
\ '24': {'description':'Not underlined', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':1},
\ '25': {'description':'Steady (not blinking)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':1},
\ '27': {'description':'Positive (not inverse)', 'attributes': {'cterm':'NONE','gui':'NONE'}, 'normal':1},
\ '28': {'description':'Visible (not hidden)', 'attributes': {'ctermfg':'NONE','ctermbg':'NONE','guifg':'NONE','guibg':'NONE'}, 'normal':1},
\ '30': {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'16','guifg':'#000000'}, 'normal':0},
\ '31': {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'1','guifg':'#ff0000'}, 'normal':0},
\ '32': {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'2','guifg':'#00ff00'}, 'normal':0},
\ '33': {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'3','guifg':'#ffff00'}, 'normal':0},
\ '34': {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'4','guifg':'#0000ff'}, 'normal':0},
\ '35': {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'5','guifg':'#990099'}, 'normal':0},
\ '36': {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'6','guifg':'#009999'}, 'normal':0},
\ '37': {'description':'Set foreground color to White', 'attributes': {'ctermfg':'7','guifg':'#ffffff'}, 'normal':0},
\ '39': {'description':'Set foreground color to default (original)', 'attributes': {'ctermfg':'NONE','guifg':'NONE'}, 'normal':1},
\ '40': {'description':'Set background color to Black', 'attributes': {'ctermbg':'16','guibg':'#000000'}, 'normal':0},
\ '41': {'description':'Set background color to Red', 'attributes': {'ctermbg':'1','guibg':'#ff0000'}, 'normal':0},
\ '42': {'description':'Set background color to Green', 'attributes': {'ctermbg':'2','guibg':'#00ff00'}, 'normal':0},
\ '43': {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'3','guibg':'#ffff00'}, 'normal':0},
\ '44': {'description':'Set background color to Blue', 'attributes': {'ctermbg':'4','guibg':'#0000ff'}, 'normal':0},
\ '45': {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'5','guibg':'#990099'}, 'normal':0},
\ '46': {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'6','guibg':'#009999'}, 'normal':0},
\ '47': {'description':'Set background color to White', 'attributes': {'ctermbg':'7','guibg':'#ffffff'}, 'normal':0},
\ '49': {'description':'Set background color to default (original).', 'attributes': {'ctermbg':'NONE','guibg':'NONE'}, 'normal':1},
\ '90': {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'16','guifg':'#000000'}, 'normal':0},
\ '91': {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'1','guifg':'#ff0000'}, 'normal':0},
\ '92': {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'2','guifg':'#00ff00'}, 'normal':0},
\ '93': {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'3','guifg':'#ffff00'}, 'normal':0},
\ '94': {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'4','guifg':'#0000ff'}, 'normal':0},
\ '95': {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'5','guifg':'#990099'}, 'normal':0},
\ '96': {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'6','guifg':'#009999'}, 'normal':0},
\ '97': {'description':'Set foreground color to White', 'attributes': {'ctermfg':'7','guifg':'#ffffff'}, 'normal':0},
\ '100': {'description':'Set background color to Black', 'attributes': {'ctermbg':'16','guibg':'#000000'}, 'normal':0},
\ '101': {'description':'Set background color to Red', 'attributes': {'ctermbg':'1','guibg':'#ff0000'}, 'normal':0},
\ '102': {'description':'Set background color to Green', 'attributes': {'ctermbg':'2','guibg':'#00ff00'}, 'normal':0},
\ '103': {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'3','guibg':'#ffff00'}, 'normal':0},
\ '104': {'description':'Set background color to Blue', 'attributes': {'ctermbg':'4','guibg':'#0000ff'}, 'normal':0},
\ '105': {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'5','guibg':'#990099'}, 'normal':0},
\ '106': {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'6','guibg':'#009999'}, 'normal':0},
\ '107': {'description':'Set background color to White', 'attributes': {'ctermbg':'7','guibg':'#ffffff'}, 'normal':0}
\ } 
" }}}

function! subprocess#shell_translate#process_lines(line, col, input) " {{{
    " don't want to pass these around in every function arg
    let s:line = a:line
    let s:col = a:col
    
    for line in a:input
        call subprocess#shell_translate#process_line(line)
    endfor
endfunction " }}}

function! subprocess#shell_translate#process_current_line(...) "{{{
    call s:log.profile_start('process_current_line')
	  let start = reltime()

    " init vars
    let l:line_nr = line('.')
    let l:current_line = getline(l:line_nr)

    call s:log.debug('XBEFORE: ' . l:current_line)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    " REMOVE REDUNDANT/IGNORED ESCAPE SEQUENCES. 
    " This often removes the requirement to parse the line char by char, which is a huge performance hit.

    " remove trailing <CR>s. conque assumes cursor will be at col 0 for new lines
    let l:current_line = substitute(l:current_line, '\r\+$', '', '')
    " remove character set escapes. they would be ignored
    let l:current_line = substitute(l:current_line, '\e(.', '', 'g')
    " remove initial color escape if it is setting color to normal. conque always starts lines in normal syntax
    let l:current_line = substitute(l:current_line, '^\(\e[0\?m\)*', '', '')
    " remove trailing color escapes. syntax changes are limited to one line
    let l:current_line = substitute(l:current_line, '\(\e[\(\d*;\)*\d*m\)*$', '', '')
    " remove all normal color escapes leading up to the first non-normal color escape
    while l:current_line =~ '^[^\e]\+\e[\(39;49\)\?m'
        call s:log.debug('found initial normal')
        let l:current_line = substitute(l:current_line, '\e[\(39;49\)\?m', '', '')
    endwhile

    call s:log.debug('XAFTER: ' . l:current_line)

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    " SHORT CIRCUIT
    " If there are no escape sequences or mid-line <CR>s, skip char-by-char processing
    if l:current_line !~ "\e" && l:current_line !~ "\r"
        call s:log.debug('short circ')

        " control characters
        while l:current_line =~ '\b'
            let l:current_line = substitute(l:current_line, '[^\b]\b', '', 'g')
            "let l:current_line = substitute(l:current_line, '^\b', '', 'g')
        endwhile

        " strip trailing spaces
        let l:current_line = substitute(l:current_line, '\s\s\+$', ' ', '')

        " check for Bells, leave whistles
        if l:current_line =~ nr2char(7)
            let l:current_line = substitute(l:current_line, nr2char(7), '', 'g')
            echohl WarningMsg | echomsg "For shame!" | echohl None
        endif

        call setline(line('.'), l:current_line)
        normal $
        startinsert!
        call s:log.profile_end('process_current_line')
        return
    endif

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    " PROCESS LINE CHARACTER BY CHARACTER

    " the number of chars to be processed, mutable
    let l:line_len = strlen(l:current_line)

    " string of characters representing post-processed output of this line
    let final_chars = []

    " highlighting for this line
    let l:color_changes = []

    " if cursor moves to a different row, these will contain the line and column of the new cursor position
    let l:next_line = 0
    let l:next_line_start = 0

    " column to start iterating at
    let idx = get(a:000, 0, 0)

    " output column
    let line_pos = 0

    call s:log.debug('starting to process line ' . l:current_line . ' at char ' . idx)

    " if we begin character processing beyond column 0, push characters up to that point onto final output array
    if idx > 0
        for i in range(idx)
            call add(final_chars, l:current_line[i])
        endfor
    endif

    while idx < l:line_len " {{{2
        "call s:log.debug("checking char " . idx)
        let c = l:current_line[idx]
        " first, escape sequences
        if c == "\<Esc>"
            "call s:log.debug('looking for a match')
            " start looking for a match
            let l:seq = ''
            let l:seq_pos = 1
            let l:finished = 0
            while idx + l:seq_pos < l:line_len && l:finished == 0
                if l:current_line[idx + l:seq_pos] == "\<Esc>"
                    break
                endif
                let l:seq = l:seq . l:current_line[idx + l:seq_pos]
                "call s:log.debug('evaluating sequence ' . l:seq)
                for esc in s:escape_sequences " {{{3
                    if l:seq =~ esc.code
                        " do something
                        "call s:log.debug(l:seq)
                        if esc.name == 'font'
                            call add(l:color_changes, {'col':line_pos,'esc':esc,'val':l:seq})
                        elseif esc.name == 'clear_line'
                            if line_pos == 0
                                let final_chars = []
                            else
                                let final_chars = final_chars[:line_pos - 1]
                            endif
                        elseif esc.name == 'cursor_right'
                            if l:seq =~ '\d'
                                let l:delta = substitute(l:seq, 'C', '', '')
                                let l:delta = substitute(l:delta, '[', '', '')
                                call s:log.debug('moving right chars ' . l:delta)
                            else
                                let l:delta = 1
                            endif 
                            let line_pos = line_pos + l:delta
                        elseif esc.name == 'cursor_left'
                            if l:seq =~ '\d'
                                let l:delta = substitute(l:seq, 'D', '', '')
                                let l:delta = substitute(l:delta, '[', '', '')
                                call s:log.debug('moving left chars ' . l:delta)
                            else
                                let l:delta = 1
                            endif 
                            let line_pos = line_pos - l:delta
                        elseif esc.name == 'cursor_to_column'
                            call s:log.debug('cursor to column: ' . l:seq)
                            let l:col = substitute(l:seq, '^\[', '', '')
                            let l:col = substitute(l:col, 'G$', '', '')
                            let line_pos = l:col - 1
                        elseif esc.name == 'cursor_up' " holy crap we're screwed
                            " first, ship off the rest of the string  to the line above and pray to God they used the [C escape
                            let l:next_line = line('.') - 1
                            let l:next_line_start = len(getline(l:next_line))
                            call setline(l:next_line, getline(l:next_line) . l:current_line[idx + strlen(l:seq) + 1 :])
                            call s:log.debug('setting previous line ' . l:next_line . ' with value ' . getline(l:next_line) . l:current_line[idx + strlen(l:seq) + 1 :])
                            " then abort processing of this line
                            let l:line_len = idx
                        elseif esc.name == 'clear_screen'
                            let line_pos = 0
                            let final_chars = []
                        elseif esc.name == 'delete_chars'
                            if l:seq =~ '\d'
                                let l:delta = substitute(l:seq, 'P', '', '')
                                let l:delta = substitute(l:delta, '[', '', '')
                                call s:log.debug('moving left chars ' . l:delta)
                            else
                                let l:delta = 1
                            endif 
                            let final_chars = extend(final_chars[ : line_pos], final_chars[line_pos + l:delta + 1 : ])
                        elseif esc.name == 'add_spaces'
                            if l:seq =~ '\d'
                                let l:delta = substitute(l:seq, '@', '', '')
                                let l:delta = substitute(l:delta, '[', '', '')
                            else
                                let l:delta = 1
                            endif 
                            call s:log.debug('adding ' . l:delta . ' spaces')
                            let l:spaces = []
                            for sp in range(l:delta)
                                call add(l:spaces, ' ')
                            endfor
                            call s:log.debug('spaces: ' . string(l:spaces))
                            let final_chars = extend(extend(final_chars[ : line_pos], l:spaces), final_chars[line_pos + 1 : ])
                        endif
                        let l:finished = 1
                        let idx = idx + strlen(l:seq)
                        break
                    endif
                endfor " }}}
                let l:seq_pos += 1
            endwhile
            if l:finished == 0
                if line_pos >= len(final_chars)
                    call add(final_chars, c)
                else
                    let final_chars[line_pos] = c
                endif
                let line_pos += 1
            endif
        elseif c == "\<CR>"
            call s:log.debug('<CR> found at column ' . line_pos . ' with $COLUMNS ' . b:COLUMNS)
            " weird condition where terminal is trying to deal with line wrapping
            if line_pos > b:COLUMNS && line_pos % b:COLUMNS == floor(line_pos / b:COLUMNS)
                " do nothing
            else
                let line_pos = 0
            endif
        elseif c == "\b"
            let line_pos = line_pos - 1
            "let final_chars[line_pos] = ''
        elseif c == nr2char(7)
            echohl WarningMsg | echomsg "For shame!" | echohl None
        else
            "call s:log.debug('adding ' . c . ' to final chars at line position ' . line_pos . ' comparing to ' . len(final_chars))
            if line_pos >= len(final_chars)
                call add(final_chars, c)
            else
                let final_chars[line_pos] = c
            endif
            let line_pos += 1
        endif
        let idx += 1
    endwhile " }}}

    let l:final_line = join(final_chars, '')
    "call s:log.debug(string(final_chars))

    " strip trailing spaces
    let l:final_line = substitute(l:final_line, '\s\+$', '', '')
    call s:log.debug('final line pos ' . line_pos . ' with line len ' . len(l:final_line))
    if line_pos > len(l:final_line)
        let l:final_line = l:final_line . ' '
    endif

    call setline(line('.'), l:final_line)

    let l:hi_ct = 1
    let l:found_color = 0
    for cc in l:color_changes
        call s:log.debug(cc.val)
        let l:color_code = cc.val
        let l:color_code = substitute(l:color_code, '^\[', '', 1)
        let l:color_code = substitute(l:color_code, 'm$', '', 1)
        if l:color_code == ''
            let l:color_code = '0'
        endif
        let l:color_params = split(l:color_code, ';', 1)
        let l:highlight = ''
        for param in l:color_params
            if exists('s:font_codes['.param.']')
                for attr in keys(s:font_codes[param].attributes)
                    let l:highlight = l:highlight . ' ' . attr . '=' . s:font_codes[param].attributes[attr]
                endfor
                if s:font_codes[param].normal == 0
                    let l:found_color = 1
                endif
            endif
        endfor

        if l:found_color == 0
            continue
        endif

        let syntax_name = ' EscapeSequenceAt_' . bufnr('%') . '_' . l:line_nr . '_' . l:hi_ct
        let syntax_region = 'syntax match ' . syntax_name . ' /\%' . l:line_nr . 'l\%' . (cc.col + 1) . 'c.*$/ contains=ALL oneline'
        "let syntax_link = 'highlight link ' . syntax_name . ' Normal'
        let syntax_highlight = 'highlight ' . syntax_name . l:highlight

        execute syntax_region
        "execute syntax_link
        execute syntax_highlight

        "call s:log.debug(syntax_name)
        "call s:log.debug(syntax_region)
        "call s:log.debug(syntax_link)
        "call s:log.debug(syntax_highlight)

        let l:hi_ct += 1
    endfor

    " \%15l\%>2c.*\%<6c

    "call s:log.debug(string(l:color_changes))
    "call s:log.debug("start line: " . l:current_line)
    "call s:log.debug("final line: " . l:final_line)
    "call s:log.debug('FUNCTION TIME: '.reltimestr(reltime(start)))

    " if we have another line to process, go there
    if l:next_line != 0
        execute l:next_line
        call s:log.debug('now processing line ' . line('.'))
        call subprocess#shell_translate#process_current_line(l:next_line_start)
    endif

    normal $
    startinsert!

    call s:log.profile_end('process_current_line')
endfunction
"}}}

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
