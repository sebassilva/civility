from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

# https://pycryptodome.readthedocs.io/en/latest/src/examples.html?highlight=key#generate-public-key-and-private-key
# https://pycryptodome.readthedocs.io/en/latest/src/signature/dsa.html?highlight=sign

def genKeyPair():
  key = RSA.generate(2048)

  private_key = key.export_key()
  public_key = key.publickey().export_key()

  return (private_key, public_key)

def saveKey(private_key, public_key):
  file_out = open("pubkey.pem", "wb")
  file_out.write(public_key)
  file_out.close()

  file_out = open("privkey.pem", "wb")
  file_out.write(private_key)
  file_out.close()

def sign(vote):
  # TODO: parse vote to bits
  key = ECC.import_key(open('privkey.pem').read())
  h = SHA256.new(vote)
  signer = DSS.new(key, 'fips-186-3')
  signature = signer.sign(h)
  return signature

def verify(vote):
  # TODO: get pubkey from blockchain peers
  key = ECC.import_key(open('pubkey.pem').read())
  h = SHA256.new(received_message)
  verifier = DSS.new(key, 'fips-186-3')
  try:
    verifier.verify(h, signature)
    return True
  except ValueError:
    return False