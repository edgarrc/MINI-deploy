'''
MINI-deploy

version    = 1.0.0
maintainer = Edgar - edgarrc@gmail.com
repository = https://github.com/edgarrc/MINI-deploy
homepage   = https://github.com/edgarrc/MINI-deploy

'''


import sys
import json
import subprocess
import os
from datetime import datetime
from waitress import serve
from flask import Flask
from flask import request
from flask import make_response
app = Flask(__name__)


def env_parametros(data):
    '''
        Cria o parametro -e, se houver o array de nested object no atributo envs
    '''

    cmd_env = ""

    if 'envs' in data:

        for env in data["envs"] :
            for data in env:
                cmd_env = cmd_env + ' -e ' + data + '=\"' + env[data] + '\"'

    return cmd_env


@app.route("/log")
def log():

    try:

        fname = "/var/log/deploy.log"
        arquivolog = ""
        if os.path.isfile(fname):
            f = open(fname, "r")
            arquivolog = f.read()
            f.close()

        response = make_response(arquivolog, 200)
        response.mimetype = "text/plain"
        return response

    except Exception as e:
        logging.info('Failed log: '+ repr(e))
        return 'Failed log: '+ repr(e)


@app.route("/publish", methods=['POST'])
def deploy():

    data = str(request.get_data(), "utf-8")
    data = json.loads(data)

    app = data["app"]
    registry = data["registry"]

    cmd_stop = 'sudo docker stop ' + app
    cmd_run = 'sudo '

    if app == "XXX":
        cmd_run = cmd_run + 'docker run --rm -p 3000:80 -d  --name ' + app + ' ' + registry

    elif app == "YYY":
        cmd_run = cmd_run + 'docker run --rm -p 3001:3002 -d --name ' + app + ' ' + registry

    os.system("sudo aws ecr get-login-password --region sa-east-1 | docker login --username AWS --password-stdin REGISTRY.dkr.ecr.sa-east-1.amazonaws.com")

    print("stop")
    os.system(cmd_stop)
    print("run")
    os.system(cmd_run)

    sysdate = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    os.system('echo "[' + sysdate + '] [APP: ' + app + ' REG: ' + registry + ']" >> /var/log/deploy.log')
    os.system('echo ' + cmd_run.replace("sudo", "") + ' > /home/ubuntu/deploy/docker.' + app + '.sh')
    os.system('chmod +x /home/ubuntu/deploy/docker.' + app + '.sh')

    return "OK"


if __name__ == '__main__':

    # Print each command line parameter received
    print("Parameters: " + str(len(sys.argv)) + " values: " + str(sys.argv))

    # Default port to listen
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    print("Starting the service " + str(port))

    # Waitress
    serve(app, host="0.0.0.0", port=port)



