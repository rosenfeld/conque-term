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
\ {'code':']0;.*__BELL__', 'name':'title', 'description':'Change Title'},
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
\ '0': {'description':'Normal (default)', 'attributes': {'cterm':'NONE','ctermfg':'NONE','ctermbg':'NONE','gui':'NONE','guifg':'NONE','guibg':'NONE'}},
\ '00': {'description':'Normal (default) alternate', 'attributes': {'cterm':'NONE','ctermfg':'NONE','ctermbg':'NONE','gui':'NONE','guifg':'NONE','guibg':'NONE'}},
\ '1': {'description':'Bold', 'attributes': {'cterm':'BOLD','gui':'BOLD'}},
\ '01': {'description':'Bold', 'attributes': {'cterm':'BOLD','gui':'BOLD'}},
\ '4': {'description':'Underlined', 'attributes': {'cterm':'UNDERLINE','gui':'UNDERLINE'}},
\ '04': {'description':'Underlined', 'attributes': {'cterm':'UNDERLINE','gui':'UNDERLINE'}},
\ '5': {'description':'Blink (appears as Bold)', 'attributes': {'cterm':'BOLD','gui':'BOLD'}},
\ '05': {'description':'Blink (appears as Bold)', 'attributes': {'cterm':'BOLD','gui':'BOLD'}},
\ '7': {'description':'Inverse', 'attributes': {'cterm':'REVERSE','gui':'REVERSE'}},
\ '07': {'description':'Inverse', 'attributes': {'cterm':'REVERSE','gui':'REVERSE'}},
\ '8': {'description':'Invisible (hidden)', 'attributes': {'ctermfg':'0','ctermbg':'0','guifg':'#000000','guibg':'#000000'}},
\ '08': {'description':'Invisible (hidden)', 'attributes': {'ctermfg':'0','ctermbg':'0','guifg':'#000000','guibg':'#000000'}},
\ '22': {'description':'Normal (neither bold nor faint)', 'attributes': {'cterm':'NONE','gui':'NONE'}},
\ '24': {'description':'Not underlined', 'attributes': {'cterm':'NONE','gui':'NONE'}},
\ '25': {'description':'Steady (not blinking)', 'attributes': {'cterm':'NONE','gui':'NONE'}},
\ '27': {'description':'Positive (not inverse)', 'attributes': {'cterm':'NONE','gui':'NONE'}},
\ '28': {'description':'Visible (not hidden)', 'attributes': {'ctermfg':'NONE','ctermbg':'NONE','guifg':'NONE','guibg':'NONE'}},
\ '30': {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'16','guifg':'#000000'}},
\ '31': {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'1','guifg':'#ff0000'}},
\ '32': {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'2','guifg':'#00ff00'}},
\ '33': {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'3','guifg':'#ffff00'}},
\ '34': {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'4','guifg':'#0000ff'}},
\ '35': {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'5','guifg':'#990099'}},
\ '36': {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'6','guifg':'#009999'}},
\ '37': {'description':'Set foreground color to White', 'attributes': {'ctermfg':'7','guifg':'#ffffff'}},
\ '39': {'description':'Set foreground color to default (original)', 'attributes': {'ctermfg':'NONE','guifg':'NONE'}},
\ '40': {'description':'Set background color to Black', 'attributes': {'ctermbg':'16','guibg':'#000000'}},
\ '41': {'description':'Set background color to Red', 'attributes': {'ctermbg':'1','guibg':'#ff0000'}},
\ '42': {'description':'Set background color to Green', 'attributes': {'ctermbg':'2','guibg':'#00ff00'}},
\ '43': {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'3','guibg':'#ffff00'}},
\ '44': {'description':'Set background color to Blue', 'attributes': {'ctermbg':'4','guibg':'#0000ff'}},
\ '45': {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'5','guibg':'#990099'}},
\ '46': {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'6','guibg':'#009999'}},
\ '47': {'description':'Set background color to White', 'attributes': {'ctermbg':'7','guibg':'#ffffff'}},
\ '49': {'description':'Set background color to default (original).', 'attributes': {'ctermbg':'NONE','guibg':'NONE'}},
\ '90': {'description':'Set foreground color to Black', 'attributes': {'ctermfg':'16','guifg':'#000000'}},
\ '91': {'description':'Set foreground color to Red', 'attributes': {'ctermfg':'1','guifg':'#ff0000'}},
\ '92': {'description':'Set foreground color to Green', 'attributes': {'ctermfg':'2','guifg':'#00ff00'}},
\ '93': {'description':'Set foreground color to Yellow', 'attributes': {'ctermfg':'3','guifg':'#ffff00'}},
\ '94': {'description':'Set foreground color to Blue', 'attributes': {'ctermfg':'4','guifg':'#0000ff'}},
\ '95': {'description':'Set foreground color to Magenta', 'attributes': {'ctermfg':'5','guifg':'#990099'}},
\ '96': {'description':'Set foreground color to Cyan', 'attributes': {'ctermfg':'6','guifg':'#009999'}},
\ '97': {'description':'Set foreground color to White', 'attributes': {'ctermfg':'7','guifg':'#ffffff'}},
\ '100': {'description':'Set background color to Black', 'attributes': {'ctermbg':'16','guibg':'#000000'}},
\ '101': {'description':'Set background color to Red', 'attributes': {'ctermbg':'1','guibg':'#ff0000'}},
\ '102': {'description':'Set background color to Green', 'attributes': {'ctermbg':'2','guibg':'#00ff00'}},
\ '103': {'description':'Set background color to Yellow', 'attributes': {'ctermbg':'3','guibg':'#ffff00'}},
\ '104': {'description':'Set background color to Blue', 'attributes': {'ctermbg':'4','guibg':'#0000ff'}},
\ '105': {'description':'Set background color to Magenta', 'attributes': {'ctermbg':'5','guibg':'#990099'}},
\ '106': {'description':'Set background color to Cyan', 'attributes': {'ctermbg':'6','guibg':'#009999'}},
\ '107': {'description':'Set background color to White', 'attributes': {'ctermbg':'7','guibg':'#ffffff'}}
\ } 
" }}}

function! subprocess#shell_translate#process_input(line, col, input) "{{{
    let [l:line, l:col, l:input] = [a:line, a:col, a:input]
    while l:line != -1
        let [l:line, l:col, l:input] = s:process(l:line, l:col, l:input)
    endwhile
endfunction "}}}

function! s:process(line, col, input) "{{{
    "call s:log.profile_start('process_input')
    "call s:log.debug('beginning processing input: ' . string(a:input))
    let cpos = a:col
    let lpos = a:line
    let chars = split(a:input, '\zs')

    let s:final_chars = split(getline(lpos), '\zs')
    let next_line = -1
    let s:color_changes = []
    "call s:log.debug('input chars start: ' . string(chars))
    "call s:log.debug('final chars start: ' . string(s:final_chars))

    let i = 0
    while i < len(chars)
        let c = chars[i]
        if c == "\b"
            let cpos = cpos - 1
        elseif c == "\<CR>"
            let cpos = 0
        elseif c == "\n"
            call s:write_buffer(lpos, cpos)
            call append(lpos, '')
            return [lpos + 1, 0, join(chars[i+1:], '')]
        elseif c == "\<Esc>"
            let seq = ''
            let found = 0
            "call s:log.debug('escape sequence triggered')
            for sc in chars[i + 1 :]
                " if we hit another esc, we're done
                if sc == "\<Esc>"
                    break
                endif

                let seq .= substitute(sc, nr2char(7), '__BELL__', '')
                "call s:log.debug('testing ' . seq)

                for esc in s:escape_sequences
                    if seq =~ esc.code
                        "call s:log.debug('found sequence ' . seq)
                        " do something
                        "call s:log.debug(l:seq)
                        let found = 1
                        if esc.name == 'font'
                            call add(s:color_changes, {'col':cpos,'esc':esc,'val':seq})
                        "elseif esc.name == 'clear_line' && cpos == 0
                        "    normal! kdd
                        elseif esc.name == 'clear_line'
                            let s:final_chars = s:final_chars[:cpos - 1]
                        elseif esc.name == 'cursor_right'
                            let cpos = cpos + 1
                        elseif esc.name == 'cursor_left'
                            let cpos = cpos - 1
                        elseif esc.name == 'cursor_to_column'
                            "call s:log.debug('cursor to column: ' . seq)
                            let col = substitute(seq, '^\[', '', '')
                            let col = substitute(col, 'G$', '', '')
                            let cpos = col - 1
                        elseif esc.name == 'cursor_up' " holy crap we're screwed
                            " first, ship off the rest of the string  to the line above and pray to God they used the [C escape
                            call setline(line('.') - 1, getline(line('.') - 1) . l:current_line[idx + strlen(l:seq) :])
                            let l:next_line = line('.') - 1
                            " then abort processing of this line
                            let l:line_len = idx + strlen(l:seq)
                        endif
                        break
                    endif
                endfor
                if found == 1
                    break
                endif
            endfor

            if found == 0
                call s:add_char(c, cpos)
            else
                let i += len(seq)
            endif
        else
            "call s:log.debug('nothing special, adding ' . c)
            call s:add_char(c, cpos)
            let cpos += 1
        endif
        let i += 1
    endwhile

    "call s:log.debug('final chars end: ' . string(s:final_chars))
    call s:write_buffer(lpos, cpos)

    "call s:log.profile_end('process_input')

    return [-1, -1, -1]
endfunction "}}}

function! s:add_char(c, pos) " {{{
    " I really hate vim for making me do this
    if a:pos >= len(s:final_chars)
        call add(s:final_chars, a:c)
    else
        let s:final_chars[a:pos] = a:c
    endif
endfunction " }}}

function! s:write_buffer(line, cpos) " {{{
    "call s:log.profile_start('write_buffer')
    "call s:log.debug('about to write to buffer at line ' . a:line . ' value ' . join(s:final_chars, ''))
    "call s:log.debug(a:cpos . string(s:final_chars))
    if a:cpos == 0
        let l:line = substitute(join(s:final_chars, ''), '\s\+$', '', '')
    else
        let l:line = join(s:final_chars[: a:cpos - 1], '') . substitute(join(s:final_chars[a:cpos :], ''), '\s\+$', '', '')
    endif
    call setline(a:line, l:line)
    call s:add_color(a:line)
    "redraw
    execute a:line
    "call s:log.profile_end('write_buffer')
endfunction " }}}

function! s:add_color(line) "{{{
    "call s:log.profile_start('add_color')
    let l:hi_ct = 1
    for cc in s:color_changes
        "call s:log.debug(cc.val)
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
            endif
        endfor

        let syntax_name = ' EscapeSequenceAt_' . bufnr('%') . '_' . a:line . '_' . l:hi_ct
        let syntax_region = 'syntax match ' . syntax_name . ' /\%' . a:line . 'l\%' . (cc.col + 1) . 'c.*$/ contains=ALL oneline'
        "let syntax_link = 'highlight link ' . syntax_name . ' Normal'
        let syntax_highlight = 'highlight ' . syntax_name . l:highlight

        execute syntax_region
        "execute syntax_link
        execute syntax_highlight

        "call s:log.debug(syntax_name)
        "call s:log.debug(syntax_region)
        "call s:log.debug(syntax_link)
        "call s:log.debug(syntax_highlight)

        let l:hi_ct = l:hi_ct + 1
    endfor
    "call s:log.profile_end('add_color')
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
        "call s:log.debug('PROFILE "' . a:name . '": ' . time)
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
endif
" }}}

" vim: foldmethod=marker
