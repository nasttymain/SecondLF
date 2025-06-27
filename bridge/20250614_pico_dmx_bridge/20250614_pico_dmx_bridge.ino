// (C) 2025 /\/asTTY
// ABD-Style DMX Bridge for RP2040/RP2350 Boards

#include <Arduino.h>

// https://github.com/jostlowe/Pico-DMX/
#include <DmxOutput.h>

DmxOutput dmx;
#define UNIVERSE_LENGTH 512
uint8_t universe[UNIVERSE_LENGTH + 1];


void setup()
{
  Serial.begin();
  dmx.begin(15);

  for (int i = 1; i < UNIVERSE_LENGTH + 1; i++)
  {
      universe[i] = 0;
  }
}
uint8_t t = 0;
uint8_t packs[3];
uint8_t packc = 0;
uint8_t dh, da, dd;
void loop()
{
  while(Serial.available() >= 1){
    if (Serial.available() >= 1){
      //データが溜まっている
      packs[packc] = Serial.read();
      packc += 1;

    }
    if(packc == 3){
      // 3バイトのコマンドを受け取ります
      dh = packs[0];
      da = packs[1];
      dd = packs[2];
      packc = 0;
      
      if(dh == 255){
        // dh = 0xFFはリセットコマンド。1ズラして待つ。FFを数回連続して送った後にデータを続けて送信すると、パケット境界がアラインされる
        packs[0] = packs[1];
        packs[1] = packs[2];
        packc = 2;
      }else{
        universe[da] = dd;
      }

    }
  }
  dmx.write(universe, UNIVERSE_LENGTH);

  while (dmx.busy()){}
  delay(10);
}