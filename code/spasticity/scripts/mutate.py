"""MUTATION TEST -- predictions written BEFORE running.

Ground truth for the base case:
  C:\\Users\\maurice\\Desktop\\spasticity_paper\\scone\\kv_zero\\SPAS01_s2_on
  config declares KV = 0.100 on soleus_l and gastroc_l; the generator instantiates the block
  TWICE, so the model actually receives KV = 0.200 on each. Unmutated expected rho ~ 2.0.

Each mutation edits ONLY the config text; the .sto (the delivered reality) is held fixed.
So `declared` moves and `delivered` does not -- exactly the situation the oracle must resolve.
"""
import os, sys, shutil, re, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from delivered_gain import verify, fmt

SRC = r"C:\Users\maurice\Desktop\spasticity_paper\scone\kv_zero\SPAS01_s2_on"
STO = os.path.join(SRC, "0265_0.821_0.804.par.sto")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mut")
CFG = open(os.path.join(SRC, "config.scone"), encoding="utf-8").read()

INJ = re.search(r"\t+ReflexController \{\n\t+name = SpasticL.*?\n\t+\}\n", CFG, re.S).group(0)

# ---------------------------------------------------------------- pre-specified mutations
def m_none(c):      return c
def m_half(c):      return c.replace("KV = 0.100", "KV = 0.050")
def m_double(c):    return c.replace("KV = 0.100", "KV = 0.200")
def m_wrongmus(c):  return c.replace("target = soleus_l", "target = tib_ant_l")
def m_wrongside(c): return c.replace("target = soleus_l", "target = soleus_r")
def m_delay(c):     return c.replace("target = soleus_l\n\t\t\t\t\tdelay = 0.020",
                                     "target = soleus_l\n\t\t\t\t\tdelay = 0.100")
def m_absent(c):    return c.replace(INJ, "")
def m_negv(c):      return c.replace("allow_neg_V = 0", "allow_neg_V = 1")
def m_v0(c):        return c.replace("KV = 0.100", "KV = 0.100\n\t\t\t\t\tV0 = 0.5")
def m_extraKL(c):   return c.replace("KV = 0.100", "KV = 0.100\n\t\t\t\t\tKL = 1.0")
def m_nomuscle(c):  return c.replace("target = soleus_l", "target = soleus_x")
def m_free(c):      return c.replace("KV = 0.100", 'KV = "~0.1<0,1>"')

MUT = [
 ("M0  unmutated (ground truth: delivered 2x)", m_none,
  "FAIL, rho~2.0 on both muscles, copies=2.000000"),
 ("M1  declared gain HALVED (0.100->0.050)", m_half,
  "FAIL, rho~4.0 -- rho scales inversely with the declared gain, which is the magnitude test"),
 ("M2  declared gain DOUBLED (0.100->0.200)", m_double,
  "PASS, rho~1.0 -- CANNOT be detected: this config declares exactly what is delivered"),
 ("M3  wrong muscle (soleus_l -> tib_ant_l)", m_wrongmus,
  "FAIL: rho~0 on tib_ant_l AND soleus_l flagged by the global leak sweep"),
 ("M4  wrong side  (soleus_l -> soleus_r)", m_wrongside,
  "FAIL: rho~0 on soleus_r AND soleus_l flagged by the global leak sweep"),
 ("M5  delay 0.020 -> 0.100", m_delay,
  "rho ~unchanged (integral estimator is delay-blind); caught ONLY by the lag diagnostic"),
 ("M6  injected block deleted from the config", m_absent,
  "FAIL: leak sweep finds undeclared drive on soleus_l and gastroc_l"),
 ("M7  allow_neg_V 0 -> 1", m_negv,
  "predictor becomes the unclamped velocity whose trial integral is ~0 -> rho explodes; "
  "must NOT silently pass"),
 ("M8  V0 0 -> 0.5", m_v0,
  "FAIL: predictor shrinks, rho rises well above 2"),
 ("M9  undelivered KL=1.0 added to the declaration", m_extraKL,
  "FAIL: rho[KL]~0"),
 ("M10 target renamed to a nonexistent muscle", m_nomuscle,
  "ABSTAIN (fail closed) -- no such .input channel"),
 ("M11 KV declared as a FREE parameter", m_free,
  "ABSTAIN (fail closed) -- the declared amount is not a number"),
]

os.makedirs(WORK, exist_ok=True)
for name, fn, pred in MUT:
    d = os.path.join(WORK, name.split()[0])
    os.makedirs(d, exist_ok=True)
    c2 = fn(CFG)
    if c2 == CFG and not name.startswith("M0"):
        print("!!! mutation %s did not change the config -- test invalid" % name); continue
    open(os.path.join(d, "config.scone"), "w", encoding="utf-8").write(c2)
    r = verify(d, STO, allow_external_sto=True)
    print("-" * 100)
    print(name)
    print("   PREDICTED : " + pred)
    print("   OBSERVED  : " + fmt(r).split("\n", 1)[1] if "\n" in fmt(r) else "")
    print("   VERDICT   : " + r["verdict"])
    for x in r["reasons"]:
        print("      ! " + x)

# ---- M12 mispaired .sto (config from SPAS01 KV=0.100, .sto from SPAS005 delivering 2x0.05)
print("-" * 100)
print("M12 MISPAIRED .sto (SPAS005_s3_on output judged against the SPAS01_s2_on config)")
print("   PREDICTED : PASS with rho~1.0 -- a FALSE PASS the oracle cannot detect from content;"
      " prevented only by refusing an external .sto")
d = os.path.join(WORK, "M12"); os.makedirs(d, exist_ok=True)
shutil.copy(os.path.join(SRC, "config.scone"), os.path.join(d, "config.scone"))
alt = r"C:\Users\maurice\Desktop\spasticity_paper\scone\kv_zero\SPAS005_s3_on\0337_0.683_0.667.par.sto"
r = verify(d, alt, allow_external_sto=True)
print("   OBSERVED  :\n" + fmt(r))
print("   with the guard ON (default):")
r2 = verify(d, alt)
print("      " + r2["verdict"] + " :: " + "; ".join(r2["reasons"]))

# ---- M13 corrupted .sto
print("-" * 100)
print("M13 CORRUPTED .sto (one row truncated)")
print("   PREDICTED : ABSTAIN (fail closed)")
d = os.path.join(WORK, "M13"); os.makedirs(d, exist_ok=True)
shutil.copy(os.path.join(SRC, "config.scone"), os.path.join(d, "config.scone"))
lines = open(STO, encoding="utf-8").read().splitlines()
lines[500] = "\t".join(lines[500].split("\t")[:-3])
bad = os.path.join(d, "corrupt.sto")
open(bad, "w", encoding="utf-8").write("\n".join(lines))
r = verify(d)
print("   OBSERVED  : " + r["verdict"] + " :: " + "; ".join(r["reasons"]))

# ---- M14 truncated run (early termination)
print("-" * 100)
print("M14 EARLY-TERMINATED run (.sto cut to the first 250 samples)")
print("   PREDICTED : same rho ~2.0 -> the oracle is insensitive to trial length; it does NOT "
      "flag an early fall")
d = os.path.join(WORK, "M14"); os.makedirs(d, exist_ok=True)
shutil.copy(os.path.join(SRC, "config.scone"), os.path.join(d, "config.scone"))
hdr = lines[:8]
open(os.path.join(d, "short.sto"), "w", encoding="utf-8").write(
    "\n".join(open(STO, encoding="utf-8").read().splitlines()[:8 + 250]))
r = verify(d)
print("   OBSERVED  :\n" + fmt(r))
