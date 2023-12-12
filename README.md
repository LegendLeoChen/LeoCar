# Leo Car
- 这是一个树莓派智能小车的项目，树莓派安装摄像头，通过mjpg-streamer向局域网上传网络视频流。在同局域网的PC或者树莓派本身运行python flask服务，即可使用手机（同局域网）通过服务器上的web应用访问视频流，并通过交互组件操控小车进行转向。
- 后续小车上树莓派的摄像头将根据人脸检测进行追踪，可能将PC作为云算力增强其功能。
- 硬件：树莓派3B+，摄像头（任意），亚克力小车（双轮），TT电机，电机驱动TB6612，锂电池。

webcam_facedetetion.py：读取树莓派摄像头上传的mjpg-streamer的视频流（IP地址），并进行人脸检测。

webcam_video.py：读取树莓派摄像头上传的mjpg-streamer的视频流（IP地址）显示。

web_control.py：博客页面/h5页面 通过局域网和 PC/树莓派 上的python flask服务器交互，控制遥杆发送数据到服务器。

static：python flask服务器上的web应用，可访问视频流，通过交互组件进行小车的角度控制信息的传输。