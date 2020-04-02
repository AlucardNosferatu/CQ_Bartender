# CQ_Bartender
For Tulpas and Hosts
 
采用了收发与处理分离的方式进行重写，将采集到的必要信息存入文件，由另外一个独立运行的程序循环检测、读取并处理其内容信息，再把结果存入文件，由酷Q的on_timer事件触发结果文件的检测、读取与发送
 
## 技术点：
1.利用了酷Q的on_timer机制，绕过了新线程无法持续存在问题
 
2.每一个检测到的文件分别用不同thread执行，提高文件处理效率
 
3.采用文件队列进行数据交换，利用磁盘空间为消息做缓存，提高收发效率
 
4.采用了独立的程序进行内容处理，即使崩溃也不影响收发模块，收发模块可使用os.system重启崩溃的处理模块
 
5.对同一文件的操作采用异常抛出后递归执行的办法，在其他程序结束对文件操作前会不断try而不会因为异常中止程序
 
## 问题：
由于酷Q的SDK-X本身的缺陷，即使什么都不处理，handler也会因为赶不上逐条转发的高速信息而导致非法访问内存，因此上述提速手段虽有效但远不足以解决问题

## 结论：
在采用了消息频率限制插件后进行了测试，即使在阻塞式运行方案下也能有不错的效果，因此该运行方案不再投入使用，转而作为个人的技术储备
