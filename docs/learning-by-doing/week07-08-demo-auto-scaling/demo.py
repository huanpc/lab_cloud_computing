__author__ = 'huanpc'
import time
from time import gmtime, strftime
from influxdb.influxdb08 import InfluxDBClient
import httplib
import json
import os
from sys import argv

###
CPU_THRESHOLD_UP = 0.1
CPU_THRESHOLD_DOWN = 0.001
MEM_THRESHOLD_UP = 15700000.0
MEM_THRESHOLD_DOWN = 2097152.0
HOST = 'localhost'
PORT = 8086
USER = 'root'
PASS = 'root'
DATABASE = 'cadvisor'
SELECT_CPU = 'derivative(cpu_cumulative_usage)'
SELECT_MEMORY = 'median(memory_usage)'
SERIES = '"stats"'
APP_NAME = 'demo-server'
NAME = ''
WHERE_BEGIN = 'container_name =~ /.*'
WHERE_END = '.*/ and time>now()-5m'
GROUP_BY = "time(10s), container_name"
CONDITION = " limit 1 "
##
JSON_APP_DEFINE = './demo_web_server.json'
APP_ID = 'demo-server'
MARATHON_URI = 'localhost:8080'
HEADER = {'Content-Type': 'application/json'}
METHOD = 'PUT'
SCALE_LINK = '/v2/apps/'+APP_ID+'?force=true'
##
def getListTaskForApp():
    taskId =[]
    header = {'Content-Type': 'application/json','Accept':'application/json'}
    con = httplib.HTTPConnection(MARATHON_URI)
    con.request("GET",'/v2/apps/'+APP_NAME+'/tasks','',header)
    response = con.getresponse()
    data =response.read().decode()
    data =json.loads(data)
    for js in data['tasks']:
        taskId.append(js["id"])
    return taskId

def deployApplication(jsonFile):
    data = open(jsonFile)
    con = httplib.HTTPConnection(MARATHON_URI)
    con.request('POST','/v2/apps',data.read(),HEADER)
    response = con.getresponse()
    print(response.read().decode())
    return True

def scaling(numOfInstance):
    data = '{"instances": '+ str(numOfInstance) +'}'
    con = httplib.HTTPConnection(MARATHON_URI)
    con.request(METHOD,SCALE_LINK,data,HEADER)
    response = con.getresponse()
    print('scale result: '+response.read().decode())
    time.sleep(10)
    updateHaproxy()
def checkMemoryBasedRule(container,mem,numOfInstance):
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if(mem>MEM_THRESHOLD_UP and mem!= 0):
        numOfInstance +=1
        print('--------------------------------------------------------------')
        print (currentTime+'|'+container+'|MEMORY_USAGE|'+str(mem)+"|scalling up, add 1 instance")
        print('App has '+str(numOfInstance)+' instances')
        scaling(numOfInstance)
        print('--------------------------------------------------------------')
        return True
    elif(mem<=MEM_THRESHOLD_DOWN and mem!= 0):
        if numOfInstance>1:
            numOfInstance -=1
            print('--------------------------------------------------------------')
            print (currentTime+'|'+container+'|MEMORY_USAGE|'+str(mem)+"|scalling down, turn off 1 instance")
            print('App has '+str(numOfInstance)+' instances')
            scaling(numOfInstance)
            print('--------------------------------------------------------------')
            return True
    else:
        return False

def checkCpuBasedRule(container,Cpu,numOfInstance):
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if(Cpu>CPU_THRESHOLD_UP and Cpu!= 0):
        numOfInstance +=1
        print('--------------------------------------------------------------')
        print (currentTime+'|'+container+'|CPU_USAGE|'+str(Cpu)+"|scalling up, add 1 instance")
        print('App has '+str(numOfInstance)+' instances')
        scaling(numOfInstance)
        print('--------------------------------------------------------------')
        return True
    elif(Cpu<=CPU_THRESHOLD_DOWN and Cpu!= 0):
        if numOfInstance>1:
            numOfInstance -=1
            print('--------------------------------------------------------------')
            print (currentTime+'|'+container+'|CPU_USAGE|'+str(Cpu)+"|scalling down, turn off 1 instance")
            print('App has '+str(numOfInstance)+' instances')
            scaling(numOfInstance)
            print('--------------------------------------------------------------')
            return True
    else:
        return False

def updateHaproxy():

    sudoPassword = '******'
    command = 'sudo python ./servicerouter.py --marathon http://localhost:8080 --haproxy-config /etc/haproxy/haproxy.cfg'
    os.system('echo %s|sudo -S %s' % (sudoPassword, command))

def main():

    # if (deployApplication(JSON_APP_DEFINE)):
        client = InfluxDBClient(HOST,PORT,USER,PASS,DATABASE)
        # time.sleep(10)
        updateHaproxy()

        while True:

            taskIdList = getListTaskForApp()
            containerNameList = []
            containerCpuUsageList =[]
            containerMemUsageList =[]
            num = len(taskIdList)

            print('################')
            print(str(num)+ " instances")
            print('TASK_ID @@ CONTAINER_ID')
            for i in range(num):
                ##GET CONTAINER ID THROUGH TASK ID FROM MAPPING TABLE
                query = 'select container_name from mapping where'+' mesos_task_id =~/.'+'*'+taskIdList[i]+'.*/ limit 1'
                result = client.query(query)
                containerName = result[0]['points'][0][2]
                print(taskIdList[i]+' @@ '+containerName)
                containerNameList.append(containerName)

                ##GET TASK CONTAINER USAGE FROM INFLUXDB
                #CPU
                query = "select "+SELECT_CPU+" from "+SERIES+" where "+WHERE_BEGIN+containerName+WHERE_END+" group by "+GROUP_BY+CONDITION
                result = client.query(query)
                if len(result) >0 :
                    cpuUsage = result[0][u'points'][0][1]/10**9/4
                else:
                    cpuUsage =0
                containerCpuUsageList.append(cpuUsage)
                #MEMORY
                query= "select "+SELECT_MEMORY+" from "+SERIES+" where "+WHERE_BEGIN+containerName+WHERE_END+" group by "+GROUP_BY+CONDITION
                result = client.query(query)
                if len(result) >0 :
                    memUsage = result[0]['points'][0][1]
                else:
                    memUsage = 0
                containerMemUsageList.append(memUsage)
            #CHECK INSTANCES ONE BY ONE AND SCALE
            print('################')
            numOfInstance = num
            for i in range(num):
                if(checkMemoryBasedRule(containerNameList[i],containerMemUsageList[i],numOfInstance)):
                    continue
                else:
                    checkCpuBasedRule(containerNameList[i],containerCpuUsageList[i],numOfInstance)

            time.sleep(2)

if __name__ == '__main__':
    main()
