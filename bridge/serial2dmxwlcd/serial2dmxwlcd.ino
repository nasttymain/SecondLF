// () 2023 /\/asTTY
// Arduino Uno R3 @16MHz 用です. Uno R4での動作確認はしていません
// Arduinoは5Vで駆動してください



// モニターに関する設定
// https://github.com/arduino-libraries/LiquidCrystal
#include <LiquidCrystal.h>
LiquidCrystal lcd(4, 5, 6, 7, 8, 9);
byte lcdmestype = 0;
unsigned long lcdmestime = 0;
char vbuf[6];

// DMXシールドに関する設定
// https://ssci.to/4274
// https://sourceforge.net/projects/dmxlibraryforar/
#include <Conceptinetics.h>
#define DMX_MASTER_CHANNELS   128 
#define RXEN_PIN                2
DMX_Master dmx_master ( DMX_MASTER_CHANNELS, RXEN_PIN );

//PCとの通信に関する設定
//PCのと通信は、速度: 38400bps、1バイト: 8bit、ストップビット: 1bit、パリティ: なし のUSBシリアル通信で行います
//https://github.com/arduino/ArduinoCore-avr/blob/master/libraries/SoftwareSerial/
#include <SoftwareSerial.h>
#define LED_RECEIVE_PIN 13
#define TX_PIN 10
#define RX_PIN 11
SoftwareSerial topc(RX_PIN, TX_PIN);
//通信確立フラグ
byte s = 0;
// パケットカウント
unsigned int cpack = 0;
unsigned int cerrpack = 0;


void setup() {
  lcd.begin(8, 2);
  for(byte i = 0; i < 8; i += 1){
    lcd.setCursor(i, 0);
    lcd.write(255);
    lcd.setCursor(i, 1);
    lcd.write(255);
  }
  
  dmx_master.enable();

  pinMode(LED_RECEIVE_PIN,OUTPUT);
  
  pinMode(RX_PIN, INPUT);
  pinMode(TX_PIN, OUTPUT);
  topc.begin(38400);
  topc.listen();

}
byte dh = 0;
byte da = 0;
byte dd = 0;
byte csum;
void loop() {
  if (s==0){
    // 通信が確立されていない場合
    if ((millis() & 512) == 512){
      //0.5秒毎に点滅
      digitalWrite(LED_RECEIVE_PIN, HIGH);
    }else{
      digitalWrite(LED_RECEIVE_PIN, LOW);
    }
    
  }
  if(topc.available()>=3){
    // 3バイトのコマンドを受け取ります
    s=1;
    digitalWrite(LED_RECEIVE_PIN, HIGH);
    dh = topc.read();
    da = topc.read();
    dd = topc.read();
    csum=((((da+dd)& 0b11110000)>>4) + ((da+dd)& 0b00001111))& 0b00001111;
    if ((dh & 0b00001111) != csum){
      //Cannot listen to rx while transferring to tx
      //topc.write((dh&0b11110000)+csum);
      //たぶんチェックサムのけいさんみすってる
      //s=0;
    }else{
    }
    cpack += 1;
    dmx_master.setChannelValue (da, dd);      
    digitalWrite(LED_RECEIVE_PIN, LOW);
  }else{
    // パケットが溜まってない周ではLCDの処理をする
    if(lcdmestime <= millis()){
      //------------------------
      if      (lcdmestype == 0){
        lcdmestime = millis() + 500;
        lcdmestype = 1;
        
      }else if(lcdmestype == 1){
        lcd.setCursor(0, 0);
        lcd.print("DMX BRID");
        lcd.setCursor(0, 1);
        lcd.print("GE CTRLR");
        lcdmestime = lcdmestime + 2000;
        lcdmestype = 2;
        
      }else if(lcdmestype == 2){
        lcd.setCursor(0, 0);
        lcd.print("VERSION ");
        lcd.setCursor(0, 1);
        lcd.print("20231203");
        lcdmestime = lcdmestime + 2000;
        lcdmestype = 3;
        
      }else if(lcdmestype == 3){
        lcd.setCursor(0, 0);
        lcd.print("SERIAL: ");
        lcd.setCursor(0, 1);
        lcd.print("38400BPS");
        lcdmestime = lcdmestime + 2000;
        lcdmestype = 4;
        
      }else if(lcdmestype == 4){
        lcd.setCursor(0, 0);
        lcd.print("CONTACT:");
        lcd.setCursor(0, 1);
        lcd.print(" GITHUB.");
        lcdmestime = lcdmestime + 2000;
        lcdmestype = 5;
        
      }else if(lcdmestype == 5){
        lcd.setCursor(0, 0);
        lcd.print("COM/NAST");
        lcd.setCursor(0, 1);
        lcd.print("TYMAIN  ");
        lcdmestime = lcdmestime + 2000;
        lcdmestype = 127;
        
      }else if(lcdmestype == 127){
        if(cpack >= 10000){
          cpack -= 10000;
        }
        if(cerrpack >= 10000){
          cerrpack -= 10000;
        }
        
        lcd.setCursor(0, 0);
        lcd.print("OK: ");
        lcd.setCursor(3, 0);
        snprintf(vbuf, 6, "%.4u ", cpack);
        lcd.print(vbuf);
        lcd.setCursor(0, 1);
        lcd.print("ER: ");
        lcd.setCursor(3, 1);
        snprintf(vbuf, 6, "%.4u ", cerrpack);
        lcd.print(vbuf);
        lcdmestime = lcdmestime + 500;
        lcdmestype = 127;
      }
      //------------------------
    }
  }
 
}
