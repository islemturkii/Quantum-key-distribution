import sys, os, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.bit_generator import generate_bits
from src.basis_generator import generate_bases, format_bases
from src.noise import apply_channel_noise
from src.eve_attack import intercept_resend_attack
from src.measurement import measure_bits
from src.sifting import sift_key
from src.error_analysis import calculate_error_rate
from src.information_reconciliation import reconcile_keys
from src.privacy_amplification import privacy_amplification
from src.hybrid_encryption import encrypt_message, decrypt_message, run_hybrid_demo
from src.bb84_protocol import run_bb84
import os as _os

P  = "\033[92mPASS\033[0m"
F  = "\033[91mFAIL\033[0m"
res = [0, 0]

def chk(name, expr):
    ok = bool(expr)
    print(f"  [{'PASS' if ok else 'FAIL'}]  {name}")
    res[0 if ok else 1] += 1

def nochk(name, fn):
    raised = False
    try: fn()
    except: raised = True
    chk(name, raised)

print("\n=== BB84 Unit Test Suite ===\n")
print("-- bit_generator --")
chk("length",        len(generate_bits(100)) == 100)
chk("binary vals",   set(np.unique(generate_bits(1000))).issubset({0,1}))
nochk("invalid n",   lambda: generate_bits(-1))

print("\n-- basis_generator --")
chk("length",        len(generate_bases(50)) == 50)
chk("values 0/1",    set(np.unique(generate_bases(200))).issubset({0,1}))
chk("format symbols",format_bases(np.array([0,1,-1])) == ["+","x","-"])

print("\n-- noise --")
b0 = np.zeros(200,dtype=int)
chk("zero noise unchanged", np.array_equal(apply_channel_noise(b0,0.0), b0))
chk("full noise flips all", np.all(apply_channel_noise(b0.copy(),1.0)==1))
nochk("invalid rate",       lambda: apply_channel_noise(b0,1.5))

print("\n-- eve_attack --")
bits=generate_bits(100); bases=generate_bases(100)
tx,evb=intercept_resend_attack(bits,bases,0.0)
chk("zero interception",    np.array_equal(tx,bits) and np.all(evb==-1))
_,evb2=intercept_resend_attack(bits,bases,1.0)
chk("full interception",    np.all(evb2!=-1))
nochk("invalid rate",       lambda: intercept_resend_attack(bits,bases,2.0))

print("\n-- measurement --")
res2=measure_bits(np.array([0,1,0,1]),np.array([0,0,1,1]),np.array([0,0,1,1]))
chk("same basis correct",   np.array_equal(res2,np.array([0,1,0,1])))

print("\n-- sifting --")
ab=np.array([0,1,0,1,0]); abases=np.array([0,1,0,0,1])
bb=np.array([0,0,0,1,1]); br_=np.array([0,0,0,0,0])
a,b,mask=sift_key(ab,abases,bb,br_)
chk("matching kept",        len(a)==int(np.sum(mask)) and np.array_equal(a,[0,0,0]))

print("\n-- error_analysis --")
chk("zero errors",  calculate_error_rate(np.array([0,1,1,0]),np.array([0,1,1,0]))[0]==0.0)
chk("all errors",   calculate_error_rate(np.zeros(4,dtype=int),np.ones(4,dtype=int))[0]==1.0)
chk("empty key",    calculate_error_rate(np.array([]),np.array([]))[0]==0.0)

print("\n-- information_reconciliation --")
alice=np.array([0,1,0,1,1,0,0,1,1,0,1,0,0,1,0,1,1,0,1,0])
bob=alice.copy(); bob[3]^=1; bob[10]^=1; bob[17]^=1
_,brec,corr=reconcile_keys(alice,bob)
qa,_=calculate_error_rate(alice,brec)
chk("fixes 3 errors",       qa==0.0 and corr>=3)

print("\n-- privacy_amplification --")
key=np.random.randint(0,2,128)
chk("output 16 bytes",      len(privacy_amplification(key))==16)
chk("deterministic",        privacy_amplification(key)==privacy_amplification(key))
nochk("empty raises",       lambda: privacy_amplification(np.array([])))

print("\n-- hybrid_encryption --")
akey=_os.urandom(16); msg="Quantum rocks!"
nonce,ct=encrypt_message(akey,msg)
chk("roundtrip",            decrypt_message(akey,nonce,ct)==msg)
hkey=privacy_amplification(np.random.randint(0,2,128))
hr=run_hybrid_demo(hkey,hkey,"Test message")
chk("demo match",           hr["keys_match"] and hr["decryption_success"])

print("\n-- integration --")
r=run_bb84(256,0.0,0.0,"Integration OK",verbose=False)
chk("no Eve secure+decrypt",r["qber"]==0.0 and r["secure"] and r["decryption_success"])
detected=sum(1 for _ in range(5) if run_bb84(512,0.0,1.0,"t",verbose=False)["qber"]>0.11)
chk("full Eve detected 4/5",detected>=4)

total=res[0]+res[1]
print(f"\n{'='*40}")
print(f"  {res[0]} passed / {res[1]} failed / {total} total")
if res[1]==0: print("  All tests passed!")
print(f"{'='*40}\n")
