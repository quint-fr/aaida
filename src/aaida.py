#! /usr/bin/env python3

ERROR_MSG = """Usage : $ aaida filename cookie
  filename : path to the semi-Colon Separated Value (.csv) file
  cookie : cookie name for current session
"""

# input
import sys
import csv
import json
import re

# craft
import random as rnd

# net
import requests as req
import time

HEADERS = {
    "Accept"            : "*/*",
    "Accept-Language"   : "en-US,en;q=0.5",
    "Accept-Encoding"   : "gzip, deflate",
    "Referer"           : "https://aaida.restosducoeur.org/pickups",
    "Content-Type"      : "application/x-www-form-urlencoded;charset=UTF-8",
    "Origin"            : "https://aaida.restosducoeur.org",
    "Sec-Fetch-Dest"    : "empty",
    "Sec-Fetch-Mode"    : "cors",
    "Sec-Fetch-Site"    : "same-origin",
    "TE"                : "trailers"
}

def assign_input_spec(d, t, c):
  if d[t]:
    return d[t]
  tot = int(int(d["disp"]) * rnd.randint(*c) / 100)
  d[t] = str(tot)
  return tot

def get_input(name):
  """Retrieve donations value from csv"""
  with open(name) as f:
    res = []
    for l in csv.DictReader(f, delimiter=","):
      if not l["real"]:
        l["real"] = l["decl"]
      if not l["disp"]:
        l["disp"] = l["real"]
      tot = int(l["real"])
      for t in ("prot", "side", "diar", "dess"):
        # empirical assign
        tot -= assign_input_spec(l, t, (10, 30))
      # we don't do misc unless specifics (go manual)
      l["misc"] = 0
      # side is at least 10%<>70%
      l["side"] = int(float(l["side"])) + tot
      res.append(l)
  return res

def load_providers():
  with open("prov.db") as f:
    return json.load(f)

def load_translations():
  with open("tran.db") as f:
    return json.load(f)

def add_pickup(cookie):
  """GET : Let's get it started."""
  url = "https://aaida.restosducoeur.org/pickup/add"
  HEADERS["Cookie"] = "PHPSESSID={}".format(cookie)
  res = req.get(url, headers=HEADERS)
  csrf = re.findall("name=\\\\u0022_token\\\\u0022 value=\\\\u0022(.*)\\\\u0022", res.text)[0]
  return csrf

def post_pickup(cookie, csrf, d):
  """POST : Don't mess up the input."""
  url = """https://aaida.restosducoeur.org/pickup/add"""
  data = """\
createdAt={}&\
provider={}&\
providerToAdd%5Bname%5D=&providerToAdd%5Baddress%5D=&providerToAdd%5Bcontact%5D=&declaredWeight={}&\
realWeight={}&\
dispatchableWeight={}&\
_token={}""".format(
    d["date"],
    d["code"],
    d["decl"],
    d["real"],
    d["disp"],
    csrf
  )
  HEADERS["Cookie"] = "PHPSESSID={}".format(cookie)
  res = req.post(url, data=data, headers=HEADERS)
  res = res.json()
  return res["id"]

def add_distrib(cookie, csrf, d):
  """GET : Under the radar."""
  url = "https://aaida.restosducoeur.org/pickup/distribute/{}".format(d["rid"])
  HEADERS["Cookie"] = "PHPSESSID={}".format(cookie)
  res = req.get(url, headers=HEADERS)
  # don't try this at home :
  csrf = re.findall("""ion\\[_token\\]\\\\u0022 value=\\\\u0022([^\\\\]*)""", res.text)[0]
  return csrf

def post_distrib(cookie, csrf, d):
  """POST : I hope it works."""
  url = "https://aaida.restosducoeur.org/pickup/distribute/{}".format(d["rid"])
  data = "\
distribution%5Baxis%5D%5B0%5D%5Bweight%5D={}&\
distribution%5Baxis%5D%5B1%5D%5Bweight%5D={}&\
distribution%5Baxis%5D%5B2%5D%5Bweight%5D={}&\
distribution%5Baxis%5D%5B3%5D%5Bweight%5D={}&\
distribution%5Baxis%5D%5B4%5D%5Bweight%5D={}&\
distribution%5B_token%5D={}".format(
  d["prot"],
  d["side"],
  d["diar"],
  d["dess"],
  d["misc"],
  csrf
)
  HEADERS["Cookie"] = "PHPSESSID={}".format(cookie)
  res = req.post(url, headers=HEADERS, data=data)
  return res.text

if __name__ == "__main__":
  name = sys.argv[1]
  cookie = sys.argv[2]

  # Read inputs
  d = get_input(name)
  providers = load_providers()
  # get translation table
  tt = load_translations()
  # Check inputs
  codes = set(providers.values())
  for l in d:
    print("preshoted :", l["code"], "exists as", tt.get(l["code"]))
    l["code"] = tt.get(l["code"], l["code"])
    if l["code"] in providers:
      l["code"] = providers[l["code"]]
    if l["code"] not in codes:
      print("Pebcaked :", l)
      exit(57)

  # Sleep between each requests to avoid DDoS
  sleeping_time = 3
  print("Retrieved", len(d), "collect(s).")
  for l in d:
    print("Adding", l)
    # Request new row
    csrf = add_pickup(cookie)
    print("csrf :", csrf)
    time.sleep(sleeping_time)
    rid = post_pickup(cookie, csrf, l)
    l["rid"] = rid
    print("rid :", rid)
    time.sleep(sleeping_time)
    csrf = add_distrib(cookie, csrf, l)
    print("token", csrf)
    time.sleep(sleeping_time)
    res = post_distrib(cookie, csrf, l)
    print("Uploaded :", res)
    time.sleep(sleeping_time)

  ##res = get_pickups(csrf, cookie)
  ##print(res.json())
