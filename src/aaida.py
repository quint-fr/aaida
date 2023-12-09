#! /usr/bin/env python3

ERROR_MSG = """Usage : $ aaida"""

import requests as req

import sys
import csv
import random as rnd
import json
import re
import time
import json

#"""await fetch("https://aaida.restosducoeur.org/pickup/add", {
#    "credentials": "include",
#    "headers": {
#        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0",
#        "Accept": "*/*",
#        "Accept-Language": "en-US,en;q=0.5",
#        "Sec-Fetch-Dest": "empty",
#        "Sec-Fetch-Mode": "cors",
#        "Sec-Fetch-Site": "same-origin"
#    },
#    "referrer": "https://aaida.restosducoeur.org/pickups",
#    "method": "GET",
#    "mode": "cors"
#});"""

#d = {"url" : 'https://aaida.restosducoeur.org/pickup/add',
#  "header" : {
#    'User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
#    'Accept: */*',
#     'Accept-Language: en-US,en;q=0.5',
#    'Accept-Encoding: gzip, deflate, br',
#    'Referer: https://aaida.restosducoeur.org/pickups',
#    'Connection: keep-alive',
#    'Cookie: PHPSESSID=oj4ffhcjfh7hq0ltoh7a3k6b2q'
#  }
#}

def get_csrf():
  url = "https://aaida.restosducoeur.org/"
  res = req.get(url)
  r = re.findall('''input type="hidden" name="_csrf_token"
                        value="(.*)"''', res.text)
  return r[0]

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
    for l in csv.DictReader(f, delimiter=";"):
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

## Used to retrieve providers codes
def get_providers(cookie):
  url = "https://aaida.restosducoeur.org/providers"
  r = req.get(url, headers={"Cookie": "PHPSESSID={}".format(cookie)})
  s = r.text
  ns = re.findall('''"Nom">([^<]*)</td>''', s)
  ps = re.findall('''/provider/([0-9]+)/''', s)
  res = [_ for _ in zip(ns, ps)]
  print(res)
  return ns, ps

def load_providers():
  with open("prov.db") as f:
    return json.load(f)

def add_pickup(cookie):
  """GET : Let's get it started."""
  url = "https://aaida.restosducoeur.org/pickup/add"
  res = req.get(url, headers={"Cookie": "PHPSESSID={}".format(cookie)})
  csrf = re.findall("name=\\\\u0022_token\\\\u0022 value=\\\\u0022(.*)\\\\u0022", res.text)[0]
  return csrf

def post_pickup(cookie, csrf, d):
  """POST : Don't mess up the input."""
  data = '\
createdAt={}&\
provider={}\
providerToAdd%5Bname%5D=&providerToAdd%5Baddress%5D=&providerToAdd%5Bcontact%5D=&declaredWeight={}\
&realWeight={}\
&dispatchableWeight={}\
&_token={}'.format(
    d["date"],
    d["code"],
    d["decl"],
    d["real"],
    d["disp"],
    csrf
  )
  print("Supposedly posted pickup :", data, "with id", "FUCK OFF")
  #r = req.post(url, headers={"Cookie": "PHPSESSID={}".format(cookie)}, data=data)
  r = {"success" : "test", "id": "ImJustSnacking"}
  return r

def add_distrib(cookie, csrf, d):
  """GET : Under the radar."""
  url = "https://aaida.restosducoeur.org/pickup/distribute/{}".format(d["rid"])
  #res = req.get(url, headers={"Cookie": "PHPSESSID={}".format(cookie)})
  #token = re.findall("""name="distribution[_token]" value="([^"]*)""", res.text)[0]
  return token

def post_distrib(cookie, csrf, d):
  """POST : I hope it works."""
  url = "https://aaida.restosducoeur.org/pickup/distribute/{}".format(d["rid"])
  data = "\
distribution%5Baxis%5D%5B0%5D%5Bweight%5D={}\
&distribution%5Baxis%5D%5B1%5D%5Bweight%5D={}\
&distribution%5Baxis%5D%5B2%5D%5Bweight%5D={}\
&distribution%5Baxis%5D%5B3%5D%5Bweight%5D={}\
&distribution%5Baxis%5D%5B4%5D%5Bweight%5D={}\
&distribution%5B_token%5D={}".format(
  d["prot"],
  d["side"],
  d["diar"],
  d["dess"],
  d["misc"],
  csrf
)
  #res = req.post(url, headers={"Cookie": "PHPSESSID={}".format(cookie)}, data)
  r = {"result" : "test"}
  return res.text

if __name__ == "__main__":
  name = sys.argv[1]
  cookie = sys.argv[2]

  # Read inputs
  d = get_input(name)
  providers = load_providers()
  #print(providers)

  # Check inputs
  # get_providers(cookie)
  codes = set(providers.values())
  for l in d:
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
    token = add_distrib(cookie, csrf, l)
    print("token", token)
    time.sleep(sleeping_time)
    res = post_distrib(cookie, csrf, l)
    print("Uplodaded :", res.text)
    time.sleep(sleeping_time)

  ##res = get_pickups(csrf, cookie)
  ##print(res.json())
