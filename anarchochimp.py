import getopt, sys, pprint, random, os
from novaclient.v1_1 import client
from models.types import Model
from models.models import get_model

import sys

def main():
    pp = pprint.PrettyPrinter(indent=4)

    shortargs = "u:a:p:l:m:s:r:t:"
    longargs = ["username=", "apikey=", "projectid=", "url=", "model=", "servers=", "repeat=", "tag="]
    try:
        opts, args = getopt.getopt(sys.argv[1:], shortargs, longargs)
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)

    username = os.getenv("NOVA_USERNAME")
    api_key = os.getenv("NOVA_API_KEY")
    project_id = os.getenv("NOVA_PROJECT_ID")
    auth_url = os.getenv("NOVA_URL")

    settings = dict()
    settings['repeat'] = 1

    model = "RANDOM"
    for o, a in opts:
        if o in ("-u", "--username"):
            username = a
        elif o in ("-a", "--apikey"):
            api_key = a
        elif o in ("-p", "--projectid"):
            project_id = a
        elif o in ("-l", "--url"):
            auth_url = a
        elif o in ("-m", "--model"):
            model = a
        elif o in ("-s", "--servers"):
            settings['servers_file'] = a
        elif o in ("-r", "--repeat"):
            settings['repeat'] = int(a)
        elif o in ("-t", "--tag"):
            settings['tag'] = a
        else:
            assert False, "unhandled option"

    model_eval = None
    try:
        model_eval = eval("Model." + model.upper())
    except AttributeError:
        print "You have selected a model that doesn't exist. Defaulting to RANDOM"
        model_eval = Model.RANDOM

    nova = client.Client(username, api_key, project_id, auth_url)

    all_servers = nova.servers.list()
    servers = [x for x in all_servers if x.status == "ACTIVE"]
    if 'tag' in settings:
        servers = [x for x in servers if settings['tag'] in x.metadata and x.metadata[settings['tag']] == '1']

    if len(servers) == 0:
        print "No servers found. Exiting now..."
        sys.exit()

    FailureModel = get_model(model_eval)
    m = FailureModel(nova, servers, settings)
    m.anarchy()
    

if __name__ == "__main__":
    main()
