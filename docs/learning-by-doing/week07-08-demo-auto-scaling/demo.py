import os

__author__ = 'huanpc'
import time
from time import gmtime, strftime
from influxdb.influxdb08 import InfluxDBClient
import http.client
import json

###
CPU_THRESHOLD_UP = 0.002
CPU_THRESHOLD_DOWN = 0.001
MEM_THRESHOLD_UP = 9437184.0
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
GROUP_BY = "time(5s), container_name"
CONDITION = " limit 1 "
##
APP_ID = 'demo-server'
MARATHON_URI = 'localhost:8080'
HEADER = {'Content-Type': 'application/json'}
METHOD = 'PUT'
LINK = '/v2/apps/'+APP_ID+'?force=true'
##
def getListTaskForApp():
    taskId =[]
    header = {'Content-Type': 'application/json','Accept':'application/json'}
    con = http.client.HTTPConnection(MARATHON_URI)
    con.request("GET",'/v2/apps/'+APP_NAME+'/tasks','',header)
    response = con.getresponse()
    data =response.read().decode()
    data =json.loads(data)
    for js in data['tasks']:
        taskId.append(js["id"])
    return taskId

def main():
    client = InfluxDBClient(HOST,PORT,USER,PASS,DATABASE)

    while True:

        taskIdList = getListTaskForApp()
        containerNameList = []
        containerCpuUsageList =[]
        containerMemUsageList =[]
        num = len(taskIdList)

        #print("Application has "+str(num)+' instances')
        print('################')
        print(str(num)+ "instances")
        print('TASK_ID @@ CONTAINER_ID')
        for i in range(num):
            ##GET CONTAINER ID THROUGH TASK ID FROM MAPPING TABLE
            query = 'select container_name from mapping where'+' mesos_task_id =~/.'+'*'+taskIdList[i]+'.*/ limit 1'
            result = client.query(query)
            containerName = result[0]['points'][0][2]
            print(taskIdList[i]+' @@ '+containerName)
            containerNameList.append(containerName)

            ##GET TASK CONTAINER USAGE FROM INFLUXDB
            query = "select "+SELECT_CPU+" from "+SERIES+" where "+WHERE_BEGIN+containerName+WHERE_END+" group by "+GROUP_BY+CONDITION
            result = client.query(query)
            cpuUsage = result[0][u'points'][0][1]/10**9/4
            containerCpuUsageList.append(cpuUsage)

            query= "select "+SELECT_MEMORY+" from "+SERIES+" where "+WHERE_BEGIN+containerName+WHERE_END+" group by "+GROUP_BY+CONDITION
            result = client.query(query)
            memUsage = result[0]['points'][0][1]
            containerMemUsageList.append(memUsage)
        #CHECK INSTANCES ONE BY ONE AND SCALE
        print('################')
        for i in range(num):
            currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            if(containerMemUsageList[i]>MEM_THRESHOLD_UP):
                num = num+1
                print('--------------------------------------------------------------')
                print (currentTime+'|'+containerNameList[i]+'|MEMORY_USAGE|'+str(containerMemUsageList[i])+"|scalling up, add 1 instance")
                print('App has '+str(num)+' instances')
                data = '{"instances": '+ str(num) +'}'
                json_data = json.dumps(data)
                con = http.client.HTTPConnection(MARATHON_URI)
                con.request(METHOD,LINK,json_data,HEADER)
                response = con.getresponse()
                print('scale result: '+response.read().decode())
                os.system("sudo ./servicerouter.py --marathon http://localhost:8080 --haproxy-config /etc/haproxy/haproxy.cfg")
                print('--------------------------------------------------------------')
                continue

            elif(containerMemUsageList[i]<=MEM_THRESHOLD_DOWN):
                num = num-1
                print('--------------------------------------------------------------')
                print (currentTime+'|'+containerNameList[i]+'|MEMORY_USAGE|'+str(containerMemUsageList[i])+"|scalling down, turn off 1 instance")
                print('App has '+str(num)+' instances')
                data = '{"instances": '+ str(num) +'}'
                json_data = json.dumps(data)
                con = http.client.HTTPConnection(MARATHON_URI)
                con.request(METHOD,LINK,json_data,HEADER)
                response = con.getresponse()
                print('scale result'+response.read().decode())
                os.system("sudo ./servicerouter.py --marathon http://localhost:8080 --haproxy-config /etc/haproxy/haproxy.cfg")
                print('--------------------------------------------------------------')
                continue
        time.sleep(5)

if __name__ == '__main__':
    main()