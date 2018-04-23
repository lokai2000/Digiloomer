

#define VERSION "0.002"


byte idxL[16] = {0,15,7,8,3,12,4,11,1,14,6,9,2,13,5,10};
byte idxR[16] = {0,15,13,14,9,10,12,11,1,2,4,3,8,7,5,6};

//Left side encoder pin
#define pinL   7
//Right side encoder pin
#define pinR   6
//Motor Enable Pin
#define pinE   9
//Motor A control
#define pinA   8
//Motor B control
#define pinB   11

//Define motor selection
#define motorL 0
#define motorR 1

byte motorACtrl[2] = { LOW,  HIGH };
byte motorBCtrl[2] = { HIGH, LOW  }; 


void setup() {

  //Encoder pins are inputs
  pinMode(pinL,INPUT);
  pinMode(pinR,INPUT);

  //Motor shield pins are outputs
  pinMode(8,OUTPUT);
  pinMode(pinE,OUTPUT);
  pinMode(10,OUTPUT);
  pinMode(11,OUTPUT);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);

  //Disable everything
  digitalWrite(8,LOW);
  digitalWrite(pinE,LOW);
  digitalWrite(10,LOW);
  digitalWrite(11,LOW);
  digitalWrite(12,LOW);
  digitalWrite(13,LOW);

  Serial.begin(9600);  
  homeLoom(motorL);
  homeLoom(motorR);

  Serial.print("DIGILOOM ");
  Serial.println(VERSION);

}

void loop() {

  byte ch;
  byte vA;
  byte vB;

  if ( Serial.available() ) {

    while ( Serial.available() ) {
      ch = Serial.read();

      if ( ch == 'S' ){
        while(!Serial.available() ){
        }
        vA = Serial.read();
        while(!Serial.available() ){
        }
        vB = Serial.read();
        //delay(1000);
        gotoLoom(vA,motorL);
        gotoLoom(vB,motorR);
        Serial.println("ACK");
      }
      
    }
  }
}


//-----------------------------------------------
void motorSelect(byte mtr){
  digitalWrite(pinA,motorACtrl[mtr]);
  digitalWrite(pinB,motorBCtrl[mtr]);
}


//-----------------------------------------------
void syncLOW(byte mtr){

  int lclPin;
  
  motorSelect(mtr);
  if (mtr==motorL) lclPin = pinL;
  if (mtr==motorR) lclPin = pinR;

  //Turn on the motor
  digitalWrite(pinE,HIGH);

  while ( digitalRead(lclPin)==HIGH );
  //debounce
  delay(2);
  while ( digitalRead(lclPin)==HIGH );

  //Turn off the motor
  digitalWrite(pinE,LOW);
  
}


//-----------------------------------------------
byte stepLoom(byte mtr){

  int lclPin;
  unsigned long int refTime;
  unsigned long int loTime;
  unsigned long int hiTime=0;
  unsigned long int tgtTime;

  syncLOW(mtr);
  
  if (mtr==motorL) lclPin = pinL;
  if (mtr==motorR) lclPin = pinR;

  //enable motor
  refTime = millis();
  digitalWrite(pinE,HIGH);
  
  //Find sync
  while ( digitalRead(lclPin)==LOW );
  tgtTime= millis();
  loTime = tgtTime - refTime;

  //Run for preset time of 70 ms
  while ( millis() < (tgtTime+95) ){
    if ( digitalRead(lclPin)==LOW ){
      hiTime = millis() - tgtTime;
    }
  }

  digitalWrite(pinE,LOW);

  //Serial.print(hiTime);
  //Serial.print(", ");
  //Serial.println(loTime);

  if ( (loTime<40) && (hiTime>84)  ) {
    return 1;
  } else {
    return 0;
  }
  
}


//-----------------------------------------------
void homeLoom(byte mtr){
  int i;
  while ( !stepLoom(mtr) );
}


//-----------------------------------------------
void gotoLoom(byte idx, byte mtr){

  byte *lclIdx;

  homeLoom(mtr);

  if (mtr==motorL) lclIdx = idxL;
  if (mtr==motorR) lclIdx = idxR;
  
  for (byte i=0; i<lclIdx[idx]; i++){
    stepLoom(mtr);
  }

}


