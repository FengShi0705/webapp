from flask import Flask, render_template, make_response, request
import json
import networkx as nx
from networkanalysis.Analysis import Retrievor
from time import gmtime, strftime

app=Flask(__name__)

# Initial Data
# whole retrievor, use whole database as its own graph
myRtr=Retrievor.UndirectedG(nx.read_gpickle('data/undirected(fortest).gpickle'),'fortest')



# Main Page
@app.route('/')
def index():
    return make_response(open('index.html').read())


# get text return nodes number
@app.route('/texttowid/<searchtext>')
def texttowid(searchtext):
    searchtext = searchtext.encode('utf-8')
    ipts = [word.strip() for word in searchtext.split(';')]
    wids=myRtr.input_ids(ipts)
    response=json.dumps(wids)
    return make_response(response)


# receive queries, nodes currently existing in client, and N (the number of nodes to be explored around each queries)
# explore around queries for most N relevent words
# return all nodes to the client, and all edges for client graph, and queries
@app.route('/gdata/<jsondata>')
def gdata(jsondata):
    info=json.loads(jsondata)
    existing_nodes=info["existing_nodes"]
    queries=info["queries"]
    N=info["N"]
    explorenodes=myRtr.get_Rel('Fw',N,queries)["RL_Allipts"]

    localG = myRtr.G.subgraph(set(existing_nodes)|set(explorenodes))  # local
    allnodes=[{"wid":n, "label":localG.node[n]["label"],"N":localG.degree(n,weight="weight"), "n":localG.degree(n)} for n in localG.nodes()]
    alledges=[{"source":source, "target":target, "Fw":Fw} for (source,target,Fw) in localG.edges(data="Fw")]

    dataset={"allnodes":allnodes, "alledges":alledges,"queries":queries}
    datajson=json.dumps(dataset)
    return make_response(datajson)

# get NeighborLevel for a node
@app.route('/neighbor_level/<int:node>')
def neighbor_level(node):
    response=my_localRtr.get_Neib_one(node,None)
    response['disconnected']=set(my_localRtr.G.nodes()).difference(response["AllNb"])
    response.pop("AllNb")
    for key,value in response.iteritems():
        response[key]=list(value)

    response=json.dumps(response)
    return make_response(response)


# WordRank
# Get relevant word list and corresponding path list for a word
@app.route('/wordrank/<int:node>')
def wordrank(node):
    response = my_localRtr.get_Rel_one(node,"Fw", None )
    nodesandpaths=[]
    for n,p in response.iteritems():
        path=p[1]
        nodesandpaths.append([n,path])
    response=json.dumps(nodesandpaths)
    return make_response(response)


