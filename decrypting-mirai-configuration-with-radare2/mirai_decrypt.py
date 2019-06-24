import r2pipe
import json
import sys

r = r2pipe.open(sys.argv[1])

r.cmd('aaa')
func_start_addr = '0x804d680'
# to load the appropriate value of data structure of in the register
addr_of_halt = '0x804d694'
func_end_addr = '0x0804d6f0'

config_addr_start = '0x0804d700'
config_addr_end = '0x0804e080'

#load and search function signature
func_sig = './mirai_decrypt_func.sdb'
r.cmd('zo '+func_sig)
r.cmd('z/')

def find_decryption_func():

    r.cmd('fs sign')
    func_srch_res = r.cmdj('fj sign')
    srch_res = list(filter(lambda x : x['name'].find('decrypt') > 0, func_srch_res))
    if len(func_srch_res) == 0 or len(srch_res) == 0:
        print('[-] Encryption function signature not found')
        return None
    print('[+] Encryption function signature found')

    func_start_addr = srch_res[0]['offset']
    r.cmd('s '+str(func_start_addr))
    func_info = r.cmdj('afij')[0]

    func_end_addr = func_start_addr + func_info['size']
    halt_addr = r.cmdj('pdj 9')[-1]['offset']
    r.cmd('fs *')
    return func_start_addr, halt_addr, func_end_addr

def find_config_func():
    r.cmd('fs sign')
    func_srch_res = r.cmdj('fj sign')
    print(func_srch_res)
    srch_res = list(filter(lambda x : x['name'].find('config_func') > 0, func_srch_res))
    if len(func_srch_res) == 0 or len(srch_res) == 0:
        print('[-] Configuration function signature not found')
        return None
    print('[+] Configuration function signature found')

    func_start_addr = srch_res[0]['offset']
    r.cmd('s '+str(func_start_addr))
    func_info = r.cmdj('afij')[0]

    func_end_addr = func_start_addr + func_info['size']
    r.cmd('fs *')
    return func_start_addr, func_end_addr

config_addr_start, config_addr_end = find_config_func()
func_start_addr, addr_of_halt , func_end_addr = find_decryption_func()


print('Start addr : {}'.format(hex(func_start_addr)))
print('Halt addr : {}'.format(hex(addr_of_halt)))
print('End addr : {}'.format(hex(func_end_addr)))

def emu_decrypt(str_offset, str_len=100):
    r.cmd('s {}'.format(func_start_addr))
    r.cmd('y {} @ {}'.format(str_len, str_offset))
    r.cmd('aei')
    r.cmd('aeim')
    r.cmd('aeip')
    r.cmd('yy @ 0x100000')
    r.cmd('wx 0x00001000 @ 0x100064')
    r.cmd('wv {} @ 0x100068'.format(str_len))
    #r.cmd('wv `fl @ {}` @ 0x100018'.format(dcrypt_offset))
    r.cmd('aecu {}'.format(addr_of_halt))
    # r.cmd('aecue {}'.format('"0x8054034,[4],eax,="'))
    # r.cmd('aecu {}'.format(addr_of_halt))
    r.cmd('ar ecx=0x100064')
    # r.cmd('aecu {}'.format(func_end_addr))
    # continue the exection till the ret instruction
    # this is the form of rest instruction
    r.cmd('aecu {}'.format('"esp,[4],ebp,=,4,esp+="'))
    return r.cmd('ps @ 0x100000')


print('============>[String method]<=================')

for str_obj in r.cmd('psj 1 @@ str.*').split('\n'):
    if str_obj:
        str_obj = json.loads(str_obj)
        dcrypt_offset = str(str_obj['offset'])
        print(emu_decrypt(dcrypt_offset))

print('=============>[Reference method]<===============')
r.cmd('s {}'.format(config_addr_start))
data_refs = r.cmdj('agaj')
data_refs = map(lambda y : y['title'], data_refs['nodes'])
#print('reference data ', data_refs)
for str_addr in data_refs:
    print(emu_decrypt(str_addr))


print('============>[Assembly search method]<===========')

# adjust the limit of search
r.cmd('e search.from = {}'.format(config_addr_start))
r.cmd('e search.to = '.format(config_addr_end))
push_list = r.cmdj('/atj push')

for inst in push_list:
    if inst['size'] == 5 :
        data_offset = inst['opstr'].replace('push ','')
        print(emu_decrypt(data_offset))
