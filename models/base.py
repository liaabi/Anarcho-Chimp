import json
import random
import paramiko
import time
import sys

__all__ = [
    "FailureModel",
    "RandomFailure"
]

def _exec_command(command, hostname, root_password=None):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname, 22, 'root', password=root_password)
    client.exec_command(command)
    client.close()

class FailureModel(object):
    def __init__(self, nova, servers, settings):
        self.nova = nova
        self.servers = dict()
        for server in servers:
            self.servers[server.id] = server

        self.settings = settings
    def anarchy(self):
        pass

class RandomFailureModel(FailureModel):
    def anarchy(self):
        if self.settings['repeat'] > len(self.servers):
            self.settings['repeat'] = len(self.servers)
            print "Can only repeat %d times." % len(self.servers)

        previousVictims = list()
        print "Repeating %d times:" % self.settings['repeat']
        for i in range(self.settings['repeat']):
            while True:
                nodeVictim = random.choice(list(self.servers.keys()))
                if nodeVictim not in previousVictims:
                    break
            print "Terminating instance %s..." % self.servers[nodeVictim].id
            self.servers[nodeVictim].delete()
            print "%s terminated" % self.servers[nodeVictim].id
            print "Waiting 500 ms"
            time.sleep(0.5)
            previousVictims.append(nodeVictim)

class GraphFailureModel(FailureModel):
    def anarchy(self):
        if 'servers_file' in self.settings:
            try:
                f = open(self.settings['servers_file'], 'r')
            except IOError, e:
                print e

            json_servers = json.loads(f.read())
            for server in json_servers:
                pass
                #public_ip = [x['addr'] for x in self.servers[server['id']].addresses['public'] if x['version'] == 4]

class NetworkFailureModel(FailureModel):
    def anarchy(self):
        self.servers = {x_id:x for x_id,x in self.servers.iteritems() if 'NetworkOutage' not in x.metadata}
        if len(self.servers) == 0:
            print "No servers found. Exiting now..."
            sys.exit()

        if self.settings['repeat'] > len(self.servers):
            self.settings['repeat'] = len(self.servers)
            print "Can only repeat %d times." % len(self.servers)

        json_servers = dict()
        if 'servers_file' in self.settings:
            try:
                f = open(self.settings['servers_file'], 'r')
            except IOError, e:
                print e

            for server in json.loads(f.read()):
                json_servers[server['id']] = server

        previousVictims = list()
        print "Repeating %d times:" % self.settings['repeat']
        for i in range(self.settings['repeat']):
            while True:
                nodeVictim = random.choice(list(self.servers.keys()))
                if nodeVictim not in previousVictims:
                    break

            thisVictim = self.servers[nodeVictim]
            public_ip = [x['addr'] for x in thisVictim.addresses['public'] if x['version'] == 4][0]

            if nodeVictim in json_servers and 'root_password' in json_servers[nodeVictim]:
                password = json_servers[nodeVictim]['root_password']
            else:
                password = None

            print "Simulating a network outage for instance %s..." % thisVictim.id
            _exec_command("sleep 5 && iptables -P INPUT DROP && iptables -P OUTPUT DROP && iptables -P FORWARD DROP &",
                public_ip, password)
            self.nova.servers.set_meta(thisVictim.id, {'NetworkOutage': '1'})
            print "Waiting 500 ms"
            time.sleep(0.5)
            previousVictims.append(nodeVictim)

class ProcessesFailureModel(FailureModel):
    def anarchy(self):
        if 'servers_file' in self.settings:
            try:
                f = open(self.settings['servers_file'], 'r')
            except IOError, e:
                print e

            json_servers = dict()
            for server in json.loads(f.read()):
                json_servers[server['id']] = server

            previousVictims = dict()
            for i in range(self.settings['repeat']):
                nodeVictim = random.choice(list(json_servers.keys()))
                while True:
                    processVictim = random.choice(list(json_servers[nodeVictim]['processes']))
                    if nodeVictim not in previousVictims or processVictim not in previousVictims[nodeVictim]:
                        break

                print "Killing %s on %s..." % processVictim, nodeVictim
                public_ip = [x['addr'] for x in self.servers[nodeVictim].addresses['public'] if x['version'] == 4][0]
                if 'root_password' in json_servers[nodeVictim]:
                    password = json_servers[nodeVictim]['root_password']
                else:
                    password = None
                _exec_command("killall " + processVictim, public_ip, password)
                print "Waiting 500 ms"
                time.sleep(0.5)
                previousVictims.setdefault(nodeVictim, []).append(processVictim)
