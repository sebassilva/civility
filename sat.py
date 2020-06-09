from ECC import genKeyPair

CURPS_DB = [
  'AAAA00000HDFAAA01',
  'BBBB00000HDFBBB02',
  'CCCC00000HDFCCC03',
]

def getKeyPair(username, curp):
  if curp in CURPS_DB:
    private_key, public_key = genKeyPair()
    newPeer = {'username': username, 'pubKey': public_key}
    # Save new peer
    return (private_key, public_key)
  else:
    return None

  

