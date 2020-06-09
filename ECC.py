from Crypto.PublicKey import ECC
from Crypto.Hash import SHA256
from Crypto.Signature import DSS
import json

# https://pycryptodome.readthedocs.io/en/latest/src/signature/dsa.html?highlight=ecdsa%20key
# https://pycryptodome.readthedocs.io/en/latest/src/public_key/ecc.html?highlight=ecdsa%20key

''' Key generation '''
def genKeyPair():
  private_key = ECC.generate(curve='P-256')
  public_key = private_key.public_key()

  return (private_key, public_key)

''' Key exporting '''
def saveKey(key, filename):
  f = open(filename,'wt')
  # f.write(key.export_key(format='PEM'))
  f.write(key)
  f.close()

def saveKeys(private_key, public_key, user):
  saveKey(public_key, '{}_public.pem'.format(user))
  saveKey(private_key, '{}_private.pem'.format(user))

''' Key importing '''
def getPrivateKey(user):
  return ECC.import_key(open('{}_private.pem'.format(user)).read())

def getPublicKey(user, peers):
  return ECC.import_key(peers[user]['public_key'])


''' Sign & Verify '''
def sign(vote, private_key):
  print('VOTE: ', vote)
  h = SHA256.new(vote.encode("utf8"))
  print('h', h)
  signer = DSS.new(private_key, 'fips-186-3')
  print('signer', signer)
  signature = signer.sign(h)
  print('signature', signature)
  return signature

def verify(vote, signature, public_key):
  print('vote', 'signature', 'publick_key')
  print(vote, signature, public_key)
  signature = bytes.fromhex(signature)
  print(vote, signature, public_key)

  h = SHA256.new(vote.encode("utf8"))
  verifier = DSS.new(public_key, 'fips-186-3')
  try:
    verifier.verify(h, signature)
    return True
  except ValueError:
    return False

def voteToJson(vote):
  return json.dumps(vote)
''' USE EXAMPLE '''
'''
# USER REQUEST TO GETKEYS from SAT
public_key, private_key = genKeyPair()

# USER SAVES KEYS
saveKeys(public_key, private_key)

# SAT SAVES KEY TO BLOCKCHAIN


# USER EMITS VOTE & REQUEST SIGNATURE
vote = {'grade': 7, 'votedUser': 'Pedro', 'votedBy': 'Aaron'}
vote_json = json.dumps(vote)

private_key = getPrivateKey()
signature = sign(vote_json, private_key)

# MINER VERIFYES SIGNATURE
public_key = getPublicKey()
response = verify(vote_json, signature, public_key)
print(response)
'''