# Báo cáo tuần 7-8
### Viết chương trình auto-scaling đơn giản cho application được deploy trên hệ thống  Mesos, Marathon.

#### Ý tưởng
- Sử dụng Marathon để deploy một application trên  Mesos có nhiều ưu điểm như thời gian trễ nhỏ, dễ dàng scale up, scale down, tun off instance....
- Tôi tiến hành giả lập một hệ thống  auto-scaling đơn giản  chạy trên docker container với các thành phần  chính:
    -   Bộ monitoring bao gồm cadvisor
    -   Bộ database bao gồm influxDB
    -   Bộ scaling sử dụng Marathon framework, chương trình giả lập tự viết
    -   Môi trường khởi chạy ứng dụng : Mesos
    -   Môi trường giả lập lượng truy cập của người dùng: jmeter
    -   Bộ load balancing Haproxy
-   Hệ thống auto - scaling sẽ thực hiện việc turn on, turn off các instance (task) của một application được deploy trên Mesos bằng cách sử dụng các hàm REST API được cung cấp sẵn của Marathon.
-   Application thử nghiệm là một web service đơn giản.

#### Giải thuật
```
while true:
    taskIdList = lấy tất cả taskId của một ứng dụng
    for  0<i<lenght(taskIdList):
        containerNameList=thực hiện lấy container name tương ứng với taskId
        containerCpuUsageList = thực hiện lấy lượng cpu usage của từng task container
        containerMemUsageList = thực hiện lấy lượng memory usage của từng task container
    for  0<i<lenght(taskIdList):
        thực hiện scale từng task instance, dựa vào luật  thres-hold based rule
```
#### Demo (be writting)