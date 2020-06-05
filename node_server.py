import json
import time

from flask import Flask, request
from data import Block, Blockchain
import requests


app = Flask(__name__)

# the node's copy of blockchain
blockchain = Blockchain()
blockchain.create_genesis_block()

# the address to other participating members of the network
peers = dict()


# endpoint to submit a new transaction. This will be used by
# our application to add new data (posts) to the blockchain
@app.route('/new_transaction', methods=['POST'])
def new_transaction():
    tx_data = request.get_json()
    required_fields = ['user', 'person', 'last_grade', 'last_comment']  # firma

    for field in required_fields:
        if not tx_data.get(field):
            return "Favor de llenar todos los campos.", 401

    tx_data["timestamp"] = time.time()

    blockchain.add_new_transaction(tx_data)

    return "Success", 201


# endpoint to return the node's copy of the chain.
# Our application will be using this endpoint to query
# all the posts to display.
@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    
    print(peers)
    return json.dumps({"length": len(chain_data),
                       "chain": chain_data,
                       "peers": peers})


# endpoint to request the node to mine the unconfirmed
# transactions (if any). We'll be using it to initiate
# a command to mine from our application itself.
@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    result = blockchain.mine()
    if result != "Success":
        return result
    else:
        # Making sure we have the longest chain before announcing to the network
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            # announce the recently mined block to the network
            announce_new_block(blockchain.last_block)
        return "Block #{} is mined.".format(blockchain.last_block.index)


# endpoint to add new peers to the network.
@app.route('/register_node', methods=['POST'])
def register_new_peers():
    print("Registrando nuevo nodo...")
    tx_data = request.get_json()
    required_fields = ['user', 'password', 'first_name', 'last_name', 'curp']

    for field in required_fields:
        if not tx_data.get(field):
            return "Favor de llenar todos los campos.", 401


    # Revisamos si no existe otro usuario registrado con el mismo curp
    curp = tx_data.get('curp')
    user = tx_data.get('user')
    node_address = tx_data.get('node_address')
    
    # Hacemos una peticion interna para revisar si ya existe el curp dentro de los camps
    headers = {'Content-Type': "application/json"}
    response = requests.get('{}chain'.format(request.host_url), headers=headers)
    data = json.loads(response.content)
    current_peers = data['peers']
    if curp in current_peers:
        # Mandar error de que este curp ya existe
        print("ESTE CURP YA EXISTE")
    else:
        # Si no existe, llamar a la base de datos del SAT para pedir la llave publica
        # Agregar las llaves publicas a los peers
        print("AGREGANDO EL NUEVO CURP")

        # Add the node to the peer list
        peer = {'curp': curp, 'public_key': '123', 'node_address': node_address}
        peers[peer['curp']] = peer


        # Add user to block chain
        'user', 'person', 'grade', 'comment', 'signature'
        new_user = {
            'user': 'BLOCKHAIN_GENERATED',
            'person': user,
            'last_grade': 2.5, 
            'average_grade': 2.5, 
            'votes': 1, 
            'last_comment': 'BLOCKCHAIN_GENERATED'}
        response = requests.post(
            '{}new_transaction'.format(request.host_url), 
            data=json.dumps(new_user),
            headers=headers)
        print("data: ", response.content)


    # Return the consensus blockchain to the newly registered node
    # so that he can sync
    return get_chain()


@app.route('/register_with', methods=['POST'])
def register_with_existing_node():
    """
    Internally calls the `register_node` endpoint to
    register current node with the node specified in the
    request, and sync the blockchain as well as peer data.
    """
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain


# endpoint to add a block mined by someone else to
# the node's chain. The block is first verified by the node
# and then added to the chain.
@app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201


# endpoint to query unconfirmed transactions
@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    """
    Our naive consnsus algorithm. If a longer valid chain is
    found, our chain is replaced with it.
    """
    global blockchain
    print("Consensus: ")

    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        print(peers[node])
        response = requests.get('http://{}/chain'.format(peers[node].get('node_address')))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    """
    A function to announce to the network once a block has been mined.
    Other blocks can simply verify the proof of work and add it to their
    respective chains.
    """
    for peer in peers:
        url = "http://{}/add_block".format(peers[peer].get('node_address'))
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

# Uncomment this line if you want to specify the port number in the code
#app.run(debug=True, port=8000)
