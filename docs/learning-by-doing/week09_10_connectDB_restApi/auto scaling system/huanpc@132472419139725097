__author__ = 'huanpc'

import time
from time import gmtime, strftime
from influxdb.influxdb08 import InfluxDBClient
import http.client
import os
import constant
import logging
import sys
from marathon import MarathonClient
import Model

def init():
    '''

    :return:
    '''
    global  logger, influxdb_client, marathon_client
    logger = logging.getLogger('auto_scaling_system')
    logging.basicConfig(stream=sys.stderr, level=getattr(logging, 'INFO'))
    influxdb_client = InfluxDBClient(constant.HOST, constant.PORT, constant.USER, constant.PASS, constant.DATABASE)
    marathon_client = MarathonClient('http://localhost:8080')

    global app, cpu_policy, mem_policy
    app = Model.get_app(constant.APP_NAME)
    policies = Model.get_policy_by_app_uuid(app.app_uuid)
    for policy in policies:
        if policy.metric_type ==0:
            cpu_policy = policy
        else:
            mem_policy = policy

def getListTaskForApp(app_name):
    '''
    get all tasks of application by name
    :param app_name:
    :return:
    '''
    task_list = []
    raw_data = marathon_client.list_tasks(app_name)
    for id in raw_data:
        index = str(id).find('::')+2
        task_list.append(str(id)[index:])
    return task_list

def get_list_container_for_app(task_list):
    '''
    get app containers of application based on list of tasks
    :param task_list:
    :return:
    '''
    containerNameList = []
    for task_id in task_list:
        query = 'select container_name from mapping where' + ' mesos_task_id =~/.' + '*' + task_id + '.*/ limit 1'
        result = influxdb_client.query(query)
        containerName = result[0]['points'][0][2]
        logger.info(task_id + ' @@ ' + containerName)
        containerNameList.append(containerName)
    return containerNameList

def get_cpu_usage_for_containers(container_id_list):
    '''
    get cpu usage of each container
    :param container_id_list:
    :return:
    '''
    container_usage_list = []
    for container_id in container_id_list:
        query = "select " + constant.SELECT_CPU + " from " + constant.SERIES + " where " + constant.WHERE_BEGIN + container_id + constant.WHERE_END + " group by " + constant.GROUP_BY + constant.CONDITION
        result = influxdb_client.query(query)
        if len(result) > 0:
            cpuUsage = result[0][u'points'][0][1] / 10 ** 9 / 4
        else:
            cpuUsage = 0
        container_usage_list.append(cpuUsage)
    return container_usage_list

def get_memory_usage_for_containers(container_id_list):
    '''
    get memory usage of each container
    :param container_id_list:
    :return:
    '''
    container_usage_list = []
    for container_id in container_id_list:
        query = "select " + constant.SELECT_MEMORY + " from " + constant.SERIES + " where " + constant.WHERE_BEGIN + container_id + constant.WHERE_END + " group by " + constant.GROUP_BY + constant.CONDITION
        result = influxdb_client.query(query)
        if len(result) > 0:
            memUsage = result[0]['points'][0][1]
        else:
            memUsage = 0
        container_usage_list.append(memUsage)
    return container_usage_list

def deployApplication(jsonFile):
    data = open(jsonFile)
    con = http.client.HTTPConnection(constant.MARATHON_URI)
    con.request('POST', '/v2/apps', data.read(), constant.HEADER)
    response = con.getresponse()
    logger.info(response.read().decode())
    return True


def scaling(numOfInstance):
    '''
    scale application
    :param numOfInstance:
    :return:
    '''
    result = marathon_client.scale_app(constant.APP_NAME, numOfInstance)
    logger.info('scale result: '+ result)
    time.sleep(constant.TIME_DELAY_SORT)
    updateHaproxy()

def checkMemoryBasedRule(container, mem, numOfInstance):
    '''
    check memory of each container then scale if needed
    :param container:
    :param mem:
    :param numOfInstance:
    :return:
    '''
    global  mem_policy,app
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if (mem > mem_policy.upper_threshold and mem != 0 and numOfInstance + mem_policy.instances_in< app.max_instances):
        numOfInstance += mem_policy.instances_in
        logger.info('--------------------------------------------------------------')        
        logger.info(currentTime + '|' + container + '|MEMORY_USAGE|' + str(mem) + "|scalling up, add 1 instance")
        logger.info('App has ' + str(numOfInstance) + ' instances')
        scaling(numOfInstance)
        logger.info('--------------------------------------------------------------')
        return True
    elif (mem <= mem_policy.lower_threshold and mem != 0 and numOfInstance-mem_policy.instances_out > app.min_instances):
        if numOfInstance > 1:
            numOfInstance -= mem_policy.instances_out
            logger.info('--------------------------------------------------------------')
            logger.info(currentTime + '|' + container + '|MEMORY_USAGE|' + str(mem) + "|scalling down, turn off 1 instance")
            logger.info('App has ' + str(numOfInstance) + ' instances')
            scaling(numOfInstance)
            logger.info('--------------------------------------------------------------')
            return True
    else:
        return False


def checkCpuBasedRule(container, Cpu, numOfInstance):
    '''
    check cpu of each container then scale if needed
    :param container:
    :param Cpu:
    :param numOfInstance:
    :return:
    '''
    global cpu_policy,app
    currentTime = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    if (Cpu > cpu_policy.upper_threshold and Cpu != 0 and numOfInstance + cpu_policy.instances_in< app.max_instances):
        numOfInstance += cpu_policy.instances_in
        logger.info('--------------------------------------------------------------')
        logger.info(currentTime + '|' + container + '|CPU_USAGE|' + str(Cpu) + "|scalling up, add 1 instance")
        logger.info('App has ' + str(numOfInstance) + ' instances')
        scaling(numOfInstance)
        logger.info('--------------------------------------------------------------')
        return True
    elif (Cpu <= cpu_policy.lower_threshold and Cpu != 0 and numOfInstance-cpu_policy.instances_out> app.min_instances):
        if numOfInstance > 1:
            numOfInstance -= cpu_policy.instances_out
            logger.info('--------------------------------------------------------------')
            logger.info(currentTime + '|' + container + '|CPU_USAGE|' + str(Cpu) + "|scalling down, turn off 1 instance")
            logger.info('App has ' + str(numOfInstance) + ' instances')
            scaling(numOfInstance)
            logger.info('--------------------------------------------------------------')
            return True
    else:
        return False


def updateHaproxy():
    '''
    update haproxy
    :return:
    '''
    command = 'sudo python ./servicerouter.py --marathon http://localhost:8080 --haproxy-config /etc/haproxy/haproxy.cfg'
    os.system('echo %s|sudo -S %s' % (constant.ROOT_PASSWORD, command))

def main():
    init()
    global app
    updateHaproxy()
    while True:
        taskIdList = getListTaskForApp(app.app_uuid)
        num = len(taskIdList)
        #
        logger.info('################')
        logger.info(str(num) + " instances")
        logger.info('TASK_ID @@ CONTAINER_ID')
        #
        containerNameList = get_list_container_for_app(taskIdList)
        containerCpuUsageList = get_cpu_usage_for_containers(containerNameList)
        containerMemUsageList = get_memory_usage_for_containers(containerNameList)
        # CHECK INSTANCES ONE BY ONE AND SCALE
        logger.info('################')
        numOfInstance = num
        for i in range(num):
            if (checkMemoryBasedRule(containerNameList[i], containerMemUsageList[i], numOfInstance)):
                continue
            else:
                checkCpuBasedRule(containerNameList[i], containerCpuUsageList[i], numOfInstance)
        time.sleep(constant.TIME_DELAY_LONG)

if __name__ == '__main__':
    main()
