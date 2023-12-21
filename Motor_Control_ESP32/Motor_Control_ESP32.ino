#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <String.h>

//TB6612FNG驱动模块控制信号 共6个
#define IN1 26  //控制电机1的方向A，01为正转，10为反转 
#define IN2 25  //控制电机1的方向B，01为正转，10为反转 
#define IN3 14  //控制电机2的方向A，01为正转，10为反转 
#define IN4 12  //控制电机2的方向B，01为正转，10为反转 

#define PWMA 33  //控制电机1 PWM控制引脚
#define PWMB 13 //控制电机2 PWM控制引脚
#define STBY 27 //工作与待机

#define freq 20000     //PWM波形频率5KHZ
#define pwm_Channel_1  0 //使用PWM的通道0
#define pwm_Channel_2  1 //使用PWM的通道1

#define resolution  10    //使用PWM占空比的分辨率，占空比最大可写2^10-1=1023

#define trigPin  22
#define echoPin  23

int car_speed = 100;
char state = 'e';
/**************************************************************************
蓝牙BLE部分
**************************************************************************/
BLECharacteristic *pCharacteristic;
bool deviceConnected = false;
uint8_t txValue = 0;
long lastMsg = 0;//存放时间的变量 
String rxload;
String receive_msg;
float x=0,y=0;

#define SERVICE_UUID           "6E400001-B5A3-F393-E0A9-E50E24DCCA9E" // UART service UUID
#define CHARACTERISTIC_UUID_RX "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
#define CHARACTERISTIC_UUID_TX "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"

class MyServerCallbacks: public BLEServerCallbacks {
    void onConnect(BLEServer* pServer) {
      deviceConnected = true;
    };
    void onDisconnect(BLEServer* pServer) {
      deviceConnected = false;
    }
};
 
class MyCallbacks: public BLECharacteristicCallbacks {
    void onWrite(BLECharacteristic *pCharacteristic) {
      std::string rxValue = pCharacteristic->getValue();
      if (rxValue.length() > 0) {
        receive_msg = "";
        for (int i = 0; i < rxValue.length(); i++)
         {
          receive_msg += (char)rxValue[i];
          Serial.print(rxValue[i]);
         }
         Serial.println("");
      if(islower(receive_msg.charAt(0))){          //是小写字母
        state = receive_msg[0];                      //控制
      }
      else{
        car_speed = receive_msg.toInt();     //转数字，修改速度
      }
      }
    }
};
 
void setupBLE(String BLEName){
  const char *ble_name=BLEName.c_str();
  BLEDevice::init(ble_name);
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new MyServerCallbacks());
  BLEService *pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_TX,BLECharacteristic::PROPERTY_NOTIFY);
  pCharacteristic->addDescriptor(new BLE2902());
  BLECharacteristic *pCharacteristic = pService->createCharacteristic(CHARACTERISTIC_UUID_RX,BLECharacteristic::PROPERTY_WRITE);
  pCharacteristic->setCallbacks(new MyCallbacks());
  pService->start();
  pServer->getAdvertising()->start();
  Serial.println("Waiting a client connection to notify...");
}
/**************************************************************************
函数功能：赋值给PWM寄存器 
入口参数：左轮PWM、右轮PWM
返回  值：无
**************************************************************************/
void Set_Pwm(int moto1, int moto2)
{
  int Amplitude = 1000;  //===PWM满幅是1024 限制在950
  
  if (moto1 > 0) {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
  } else {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
  }
  
  if (moto2 > 0) {
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  } else {
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  }
  
  //功能：限制PWM赋值 
  if (moto1 < -Amplitude)  moto1 = -Amplitude;
  if (moto1 >  Amplitude)  moto1 =  Amplitude;
  if (moto2 < -Amplitude)  moto2 = -Amplitude;
  if (moto2 >  Amplitude)  moto2 =  Amplitude;
  
  //赋值给PWM寄存器 
  ledcWrite(pwm_Channel_1, abs(moto1));
  ledcWrite(pwm_Channel_2, abs(moto2));
}
void control(char command, int carspeed){
  if(command=='a'){
    Set_Pwm(carspeed, carspeed);      //前
  }
  else if(command=='b')
    Set_Pwm(-carspeed, -carspeed);    //后
  else if(command=='c')
    Set_Pwm(carspeed*0.8, carspeed);  //左
  else if(command=='d')
    Set_Pwm(carspeed, carspeed*0.8);  //右
  else if(command=='e')
    Set_Pwm(0, 0);                      //停
  else if(command=='f')
    Set_Pwm(carspeed/2.0, -carspeed/2.0); //原地转
}
void ultrasound(){
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  //计算超声波回波的时间
  long duration = pulseIn(echoPin, HIGH);
  
  //计算物体的距离(cm)
  float distance = duration * 0.034 / 2;
  if(distance < 20)
    state = 'e';
  //输出物体的距离
  Serial.print("distance:");
  Serial.println(distance);
  delay(100);
}
/*********************************setup**********************************/
void setup()
{
    pinMode(IN1, OUTPUT);          //TB6612控制引脚，控制电机1的方向，01为正转，10为反转
    pinMode(IN2, OUTPUT);          //TB6612控制引脚，
    pinMode(IN3, OUTPUT);          //TB6612控制引脚，控制电机2的方向，01为正转，10为反转
    pinMode(IN4, OUTPUT);          //TB6612控制引脚，
    pinMode(PWMA, OUTPUT);         //TB6612控制引脚，电机PWM
    pinMode(PWMB, OUTPUT);         //TB6612控制引脚，电机PWM
    pinMode(STBY, OUTPUT);

    pinMode(trigPin, OUTPUT);     //超声波
    pinMode(echoPin, INPUT);

    digitalWrite(IN1, LOW);       //TB6612控制引脚拉低
    digitalWrite(IN2, LOW);       //TB6612控制引脚拉低
    digitalWrite(IN3, LOW);       //TB6612控制引脚拉低
    digitalWrite(IN4, LOW);       //TB6612控制引脚拉低
    digitalWrite(STBY, HIGH);
  
    ledcSetup(pwm_Channel_1, freq, resolution); //PWM通道一开启设置
    ledcAttachPin(PWMA, pwm_Channel_1);     //PWM通道一和引脚PWMA关联
    ledcWrite(pwm_Channel_1, 0);        //PWM通道一占空比设置为零
    
    ledcSetup(pwm_Channel_2, freq, resolution); //PWM通道二开启设置
    ledcAttachPin(PWMB, pwm_Channel_2);     //PWM通道二和引脚PWMB关联
    ledcWrite(pwm_Channel_2, 0);        //PWM通道二占空比设置为零
    
    Serial.begin(115200);
    setupBLE("LEO_BLE");//设置蓝牙名称

}

/************************************loop************************************/
void loop()
{
    long now = millis();//记录当前时间
    if (now - lastMsg > 500) 
    {//每隔1秒发一次信号  
        if (deviceConnected&&rxload.length()>0) {
            String str=rxload;
          const char *newValue=str.c_str();
          pCharacteristic->setValue(newValue);
          pCharacteristic->notify();
          Serial.println(str);
        }
      lastMsg = now;//刷新上一次发送数据的时间
    }
    ultrasound();
    control(state, car_speed);
}
