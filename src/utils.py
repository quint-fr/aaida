#! /usr/bin/env python3

import sys
import requests as req
import re
import json

## Used to retrieve providers codes
def get_providers(cookie):
  url = "https://aaida.restosducoeur.org/providers"
  r = req.get(url, headers={"Cookie": "PHPSESSID={}".format(cookie)})
  s = r.text
  ns = re.findall('''"Nom">([^<]*)</td>''', s)
  ps = re.findall('''href="/provider/([0-9]+)''', s)
  return ns, ps

if __name__ == "__main__":
  d = get_providers(sys.argv[1])
  res = dict(zip(*d))
  print(json.dumps(res))
