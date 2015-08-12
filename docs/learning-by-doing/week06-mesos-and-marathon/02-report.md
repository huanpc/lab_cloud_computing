# Báo cáo tuần 6
#### [HuanPC] Auto - scaling team
##### Tìm hiểu mesosphere và sử dụng Marathon  triển khai  application  trong  docker

**I.  Đôi nét về Mesosphere**

######Mososphere

- Mesosphere là một giải pháp phần mềm được mở rộng từ Apache Mesos nhằm  mục đích  cung cấp một cách thức quản lý server infrastructures, tập trung vào mô hình nhiều cluster.
- Mesosphere là sự kết hợp của các thành phần Mesos, Marathon, Chronos.
- Mesosphere cung cấp giải pháp đơn giản để thực hiện việc "scale" một application.
- Mesosphere cung cấp các tính năng:
	- Application scheduling 
	- Scaling
	- Fault - tolerance 
	- Self - healing
	- Application service discovery
	- Port unification
	- End point elasticity

######Apache Mesos

Tổng quan
- Apache Mesos là một trình quản lý cluster mã nguồn mở, làm đơn giản hóa quá trình triển khai một ứn dụng trên một "scalable cluster of servers" 
- Mesos cung cấp các tính năng như:
	- Khả năng co dãn tới 10,000 node
	- Tách biệt tài nguyên cho từng task thông qua Linux Container
	- Sử dụng hiệu quả tài nguyên CPU, memory thông qua cơ chế scheduling
	- Apache ZooKeeper
	- Web UI cho việc theo dõi trạng thái của cluster

Kiến trúc
![Mesos_architecture](https://github.com/huanpc/lab_clound_computing/blob/master/docs/learning-by-doing/week06-mesos-and-marathon/images/mesos_architecture.png)

- Master deamon:  chạy trên master node và quản lý các slave deamon
- Slave daemon: chạy trên slave node và thực thi các task thuộc về các framework
- Framework: thường là một Mesos application, bao gồm:
	- Scheduler: đăng ký với Master deamon nhận các resource offer
	- Một hoặc nhiều bộ Executor: thực thi các task trên Slave daemon
- Offer: một danh sách tài nguyên CPU, memory khả dụng của một slave node. Các slave node gửi các offer tới master node, và master node sẽ chuyển chúng đến các framework đã đăng ký trước.
- Task: một đơn vị thực thi trên một slave node, được lên kế hoạch thực thi bởi framework
-  Apache ZooKeeper: kết hợp các master node. Ít nhất 3 master node để đạt được khả năng *highly-available configuration*
> Kiến trúc này cho phép Mesos chia sẻ  tài nguyên của các cluster cho các application.
> Lượng tài nguyên được phân bố tới một framework phụ thuộc vào các policy được thiết lập trên master node, và bộ framework scheduler sẽ quyết định sử dụng  offer nào. Sau đó, Mesos Master sẽ khởi chạy các task trên các Mesos slave thích hợp. Một khi task được hoàn thành, các tài nguyên sử dụng sẽ được giải phóng, chu trình gửi-nhận-xử lý các offer sẽ lại tiếp tục để lên lịch thực thi các task.
*Ví du về *Resource Offer* *
![Resource offer]()

######Marathon

- Marathon là một framework cho Mesos, được thiết kế để triển khai "long-running application".
-  Thay thế cho "traditional init system" trong mô hình Mesosphere.
- Đơn giản hóa việc thực thi một ứng dụng trên môi trường cluster với các đặc điểm:
	- High availability
	- Node constraint
	- Application health check
	- REST API for service discovery
	- Web user interface
	- Scaling
	- Healing capabitlities
Tham khảo [https://github.com/mesosphere/marathon]

######Chronos

- Chronos là một framework cho Mesos, phát triển bởi Airbnb, là sự thay thế cho `cron` (trong LINUX). 
- Là thành phần thực  hiện điều phối và schedule job Mesos.
- Bao gồm các API hỗ trợ việc schedule job,  cung cấp web UI
- Trong mô hình Mesosphere, khác với Marathon, Chronos cung cấp một cách khác cho việc thực thi một ứng dụng, theo lịch hoặc các điều kiện kích hoạt.

Tham khảo [https://github.com/mesosphere/chronos]

**II. Sử dụng Marathon triển khai một application trong  Docker**

######Cài đặt bộ mesos testing

- Cài đặt docker-compose (Xem thêm [https://docs.docker.com/compose/install/])
- Tải bộ mesos testing từ github:

```
$ git clone https://github.com/dontrebootme/compose-mesos.git
$ cd compose-mesos
```

- Sửa lại các trường `MESOS_HOSTNAME=localhost`  trong `master1, slave1, slave2,slave3` trong file `docker-compose.yml` 
- Khởi chạy các container từ bộ testing:

```
$ docker-compose up -d
```
- Kết quả:

```
$compose-mesos# docker ps 
CONTAINER ID        IMAGE                                 COMMAND                CREATED             STATUS              PORTS                              NAMES
afc5bf9efb7a        redjack/mesos-slave:0.21.0            "mesos-slave"          2 minutes ago       Up 2 minutes        5051/tcp, 0.0.0.0:5053->5053/tcp   composemesos_slave3_1     
b9ae92cd29ae        redjack/mesos-slave:0.21.0            "mesos-slave"          2 minutes ago       Up 2 minutes        5051/tcp, 0.0.0.0:5052->5052/tcp   composemesos_slave2_1     
c11675c35071        redjack/mesos-slave:0.21.0            "mesos-slave"          2 minutes ago       Up 2 minutes        0.0.0.0:5051->5051/tcp             composemesos_slave1_1     
c3706aea670d        mesosphere/marathon:v0.8.1            "./bin/start --maste   2 minutes ago       Up 2 minutes        0.0.0.0:8080->8080/tcp             composemesos_marathon_1   
244feaac7e81        tomaskral/chronos:2.3.2-mesos0.21.1   "/usr/bin/chronos --   2 minutes ago       Up 2 minutes        0.0.0.0:4400->8080/tcp             composemesos_chronos_1    
5193cd029a49        redjack/mesos-master:0.21.0           "mesos-master"         2 minutes ago       Up 2 minutes        0.0.0.0:5050->5050/tcp             composemesos_mesos1_1     
85b4b3a791f9        jplock/zookeeper:3.4.6                "/opt/zookeeper/bin/   2 minutes ago       Up 2 minutes        2181/tcp, 2888/tcp, 3888/tcp       composemesos_zk1_1     
```

- Truy cập vào các Web user interface theo địa chỉ:
	- Mesos Master	http://localhost:5050
	- Marathon	http://localhost:8080
	- Chronos	http://localhost:4400

######Triển khai một ứng dụng trên Docker

- Ý tưởng: tạo một application đơn giản chạy trên nền shell script thực hiện in ra liên tục dòng chữ `HELLO MARATHON`

Bước 1: tạo file định nghĩa một application: 

```
$touch hello_app.json
$nano hello_app.json 
{
    "id": "basic-0",
    "cmd": "while [ true ] ; do echo 'Hello Marathon' ; sleep 5 ; done",
    "cpus": 0.1,
    "mem": 10.0,
    "instances": 2
}
```

- Tham số `cmd` khai báo câu lệnh sẽ được thực thi khi ứng dụng khởi chạy.
- Tham khảo thêm tại [đây](https://mesosphere.github.io/marathon/docs/application-basics.html)

Bước 2: sử dụng HTTP API để deploy ứng dụng với file khai báo trên

`$ curl -X POST -H "Content-Type: application/json" http://localhost/v2/apps -d@hello_app.json`
Các API của Marathon sẽ đề cập sau.
Kết quả:

```
{"id":"/basic-0","cmd":"while [ true ] ; do echo 'Hello Marathon' ; sleep 5 ; done","args":null,"user":null,"env":{},"instances":2,"cpus":0.1,"mem":10.0,"disk":0.0,"executor":"","constraints":[],"uris":[],"storeUrls":[],"ports":[0],"requirePorts":false,"backoffFactor":1.15,"container":null,"healthChecks":[],"dependencies":[],"upgradeStrategy":{"minimumHealthCapacity":1.0,"maximumOverCapacity":1.0},"labels":{},"version":"2015-08-03T14:12:37.890Z","deployments":[{"id":"eb46a15d-61cd-4adb-889f-823408923b4d"}],"tasks":[],"tasksStaged":0,"tasksRunning":0,"tasksHealthy":0,"tasksUnhealthy":0,"backoffSeconds":1,"maxLaunchDelaySeconds":3600}
```

- Vào web interface của Marathon:
![Marathon](https://github.com/huanpc/lab_clound_computing/blob/master/docs/learning-by-doing/week06-mesos-and-marathon/images/marathon.png)

![Marathon_task](https://github.com/huanpc/lab_clound_computing/blob/master/docs/learning-by-doing/week06-mesos-and-marathon/images/Marathon_task.png)

- Giao diện hoạt động của Mesos:
![Mesos_webUI](https://github.com/huanpc/lab_clound_computing/blob/master/docs/learning-by-doing/week06-mesos-and-marathon/images/mesos.png)

- Application đang running trên 1 slave:
![App_running](https://github.com/huanpc/lab_clound_computing/blob/master/docs/learning-by-doing/week06-mesos-and-marathon/images/slave_running.png)

######Scaling up, down

- Marathon cung cấp các hàm HTTP API hỗ trợ việc deploy, manage một application.
- Để scale up, down, ta có thể tạo một `http request` với phương thức `PUT` có dạng như sau:

```
$ curl -X PUT -H "Content-Type: application/json" http://localhost:8080/v2/apps/hello-app -d@hello_app.json
```

> Lưu ý:  đoạn `-d@hello_app.json` sử dụng lại file application definition, với trường `instances` đã được thay đổi, để tiến hành thêm hay bớt *task* cho application đang thực thi. Có thể cập nhật các trường khác bằng cách này (`cpu`,`memory` ...).
> Ngoài ra còn có nhiều cách khác để tạo một http request, với data là có dạng json, các bạn từ tìm hiểu thêm :) .

- Tham khảo bên dưới một số API của Marathon

**III. Một số REST API của Marathon  hỗ trrợ việc  deploy một application** 

- Cách sử dụng: gửi một `HTTP REQUEST` tới địa chỉ `http://localhost:8080/{command}` 

Method | Command| Meaning
------------- | -------------|-------------
POST  | /v2/apps|Khởi chạy một application
GET| /v2/apps| liệt kê tất cả application đang chạy
GET |/v2/apps/{appId}/versions| liệt kê version của application ứng với appId
PUT |/v2/apps/{appId}| Thay đổi config của application
DELETE| /v2/apps/{appId} |Destroy app appId
GET |/v2/tasks |Liệt kê tất cả các task đang chạy

Tham khảo thêm tại [đây](https://mesosphere.github.io/marathon/docs/rest-api.html#put-v2-apps-appid)

>Code demo sử dụng REST API viết bằng python nằm trong cùng folder với báo cáo này.
