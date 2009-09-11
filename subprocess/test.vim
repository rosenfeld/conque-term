 
function! TestPty()
     let p = subprocess#new()
 
     call p.open('/bin/bash')
     call append(line('$'), p.read(0.2))
 
     call p.write("stty -a\n")
     call append(line('$'), p.read(0.2))
 
     call p.write("cd ~/.vi\t")
     call append(line('$'), p.read(0.2))
 
     call p.write("/autoload\n")
     call append(line('$'), p.read(0.2))
 
     call p.write("pwd\n")
     call append(line('$'), p.read(0.2))
 endfunction

function! TestPopen()
     let p = subprocess#new()
 
     call p.open('cmd.exe')
     call append(line('$'), p.read(0.2))
     call append(line('$'), '---------------------------------------------------')
 
     call p.write("whoami\n")
     call append(line('$'), p.read(0.2))
     call append(line('$'), '---------------------------------------------------')
 
     call p.write("cd C:\\\n")
     call append(line('$'), p.read(0.2))
     call append(line('$'), '---------------------------------------------------')
 
     call p.write("dir\n")
     call append(line('$'), p.read(0.2))
     call append(line('$'), '---------------------------------------------------')
 endfunction

