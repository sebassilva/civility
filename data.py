from hashlib import sha256
import json, time, copy
from utils import calculate_average
from ECC import verify, voteToJson, getPublicKey


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.transactions = transactions


    def compute_hash(self):
        """
        A function that return the hash of the block contents.
        """
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()



class Blockchain:
    # difficulty of our PoW algorithm
    difficulty = 2

    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []

    def create_genesis_block(self):
        """
        A function to generate genesis block and appends it to
        the chain. The block has index 0, previous_hash as 0, and
        a valid hash.
        """
        genesis_block = Block(0, [], 0, "0")
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_block(self, block, proof):
        """
        A function that adds the block to the chain after verification.
        Verification includes:
        * Checking if the proof is valid.
        * The previous_hash referred in the block and the hash of latest block
          in the chain match.
        """
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    @staticmethod
    def proof_of_work(block):
        """
        Function that tries different values of nonce to get a hash
        that satisfies our difficulty criteria.
        """
        block.nonce = 0

        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()

        return computed_hash

    def add_new_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    @classmethod
    def is_valid_proof(cls, block, block_hash):
        """
        Check if block_hash is valid hash of block and satisfies
        the difficulty criteria.
        """
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.compute_hash())

    @classmethod
    def check_chain_validity(cls, chain):
        result = True
        previous_hash = "0"

        for block in chain:
            block_hash = block.hash
            # remove the hash field to recompute the hash again
            # using `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block_hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result

    def mine(self, peers):
        """
        This function serves as an interface to add the pending
        transactions to the blockchain by adding them to the block
        and figuring out Proof Of Work.
        """
        if not self.unconfirmed_transactions:
            return "No hay transacciones que minar"

        last_block = copy.deepcopy(self.last_block)

        # Recorremos el arreglo de transacciones que no se han minado
        for tx in self.unconfirmed_transactions:
            print('verify signature: ', self.verifySignature(tx, peers))
            if self.verifySignature(tx, peers):
              if tx.get('person') == tx.get('user'):
                  return "Un usuario no puede votar por si mismo."
              if int(tx.get('last_grade')) < 0 or int(tx.get('last_grade')) > 5:
                  return "La calificacion debe estar entre 0 y 5"
              
            # Buscamos a la persona en el bloque anterior, si existe, promediamos:
  

            found_previous = False
            print("last_block.transactions: ", last_block.transactions)
            for previous_tx in last_block.transactions:
                if previous_tx.get('person') == tx.get('person'):
                    print("Se ha encontrado el usuario en transacciones anteriores")
                    avg = calculate_average(previous_tx.get('average_grade'), previous_tx.get('last_grade'), tx.get('last_grade'))
                    print(avg, previous_tx.get('average_grade'), previous_tx.get('last_grade'), tx.get('last_grade'))

                    # Update tx values
                    previous_tx['average_grade'] = avg
                    previous_tx['votes'] = int(previous_tx.get('votes')) + 1
                    previous_tx['last_comment'] =tx.get('last_comment')
                    previous_tx['last_grade'] =tx.get('last_grade')
                    found_previous = True
                    
                else:
                    print("No se ha enontrado el usuario en transacciones pasadas")
            
           
            if not found_previous:
                last_block.transactions.append(tx)


        new_block = Block(index=last_block.index + 1,
                        transactions=last_block.transactions,
                        timestamp=time.time(),
                        previous_hash=last_block.hash)

        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof)
        self.unconfirmed_transactions = []

        return "Success"

    def verifySignature(self, vote, peers):
      signature = vote.get('signature')
      user = vote.get('user')

      # Si la cadena la genera el propio blockchain, no existe firma. Al menos todavia
      if user == 'BLOCKHAIN_GENERATED':
          return True
      
      public_key = self.getPublicKey(user, peers)

      vote_copy = {
        'person':  vote.get("person"),
        'last_comment':  vote.get("last_comment"),
        'user':  vote.get("user"),
        'last_grade' : vote.get("last_grade")
      }

      response = verify(voteToJson(vote_copy), signature, public_key)

      return True if response else False

    def getPublicKey(self, user, peers):
      """
      Return public key from peers list in last block
      """
      return getPublicKey(user, peers)

    #   block = self.chain[len(self.chain) - 1].transactions
    #   if len(txs) > 0:
    #     peers = txs[-1]['peers']
    #     user = list(filter(lambda d: d['user'] in user, peers))
    #     print(user)
      
    #   return user[1] if user else None
