

CURPS_DB = [
  'AAAA00000HDFAAA01',
  'BBBB00000HDFBBB02',
  'CCCC00000HDFCCC03',
]

def getKeyPair(curp):

  if curp in CURPS_DB:
    return True
  else:
    return False

  

