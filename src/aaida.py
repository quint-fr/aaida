#! /usr/bin/env python3

import requests as req

import sys
import re
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

CSRF = None
POST_ADD = 'createdAt={}&provider={}&providerToAdd%5Bname%5D=&providerToAdd%5Baddress%5D=&providerToAdd%5Bcontact%5D=&declaredWeight={}&realWeight={}&dispatchableWeight={}&_token=65abba54db31.y81hJ_5qsEryEZnNpLLh2PwVgxuq2infRBLE7a7TheY.of0wQbgExh7GPLS148PYjM5X3Hrp6nOYLkCpgvaa6bP-_xVtv17AFaROoQ'
createdAt = "%Y-%m-%d"
provider = ""
declared = ""
def pp_json(d):
  print(d)
  print(json.dumps(d, indent=2))

def get_csrf():
  url = "https://aaida.restosducoeur.org/"
  res = req.get(url)
  r = re.findall('''input type="hidden" name="_csrf_token"
                        value="(.*)"''', res.text)
  return r[0]

def get_pickups(csrf, cookie, d):
  headers = {"Cookie" : cookie}
  url = "https://aaida.restosducoeur.org/pickup/add"
  # get csrf_token here
  #res = req.get(url, headers=headers)
  d["_token"] = csrf
  res = req.post(url, headers=headers, data=d)

  return res.json()["id"]

if __name__ == "__main__":
  cookie, csrf = sys.argv[1], sys.argv[2]
  res = get_pickups()
  pp_json(res)

