 
function! TestSubprocessPty()
    let p = subprocess#new()
 
    call p.open('/bin/bash')
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("stty -a\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("cd ~/.vi\t")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("/autoload\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("pwd\n")
    call TestSubprocessAddLines(p.read(0.2))
endfunction

function! TestSubprocessSubprocess()
    let p = subprocess#new()
 
    call p.open('/bin/bash')
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("stty -a\n")
    call TestSubprocessAddLines(p.read(0.2))
 
endfunction

function! TestSubprocessPopenWindows()
    let p = subprocess#new()
 
    call p.open('cmd.exe')
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("whoami\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("cd C:\\\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("dir\n")
    call TestSubprocessAddLines(p.read(0.2))
endfunction

function! TestSubprocessPopenWindows()
    let p = subprocess#new()
 
    call p.open('cmd.exe')
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("whoami\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("cd C:\\\n")
    call TestSubprocessAddLines(p.read(0.2))
 
    call p.write("dir\n")
    call TestSubprocessAddLines(p.read(0.2))
endfunction

function! TestSubprocessAddLines(lines)
    for line in a:lines
        let sublines = split(line, '', 1)
        for pl in range(len(sublines))
            if pl != 0
                call append(line('$'), sublines[pl])
            else
                call setline(line('$'), getline(line('$')) . sublines[pl])
            endif
        endfor
    endfor
endfunction

