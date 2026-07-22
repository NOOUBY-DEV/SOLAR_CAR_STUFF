#define ALL_USENSORS unsigned char INDEX = 0; INDEX < USENSOR_COUNT; INDEX ++

#define USENSOR_1__TRIG_PIN 2
#define USENSOR_2__TRIG_PIN 8
#define USENSOR_3__TRIG_PIN 10
#define USENSOR_4__TRIG_PIN 12
#define USENSOR_COUNT 4


#define SAFE_STATUS 'S'
#define WARNING_STATUS 'W'
#define DANGER_STATUS 'D'


#define WARNING_DISTANCE_CM 100
#define DANGER_DISTANCE_CM 50



uint8_t USENSOR_LIST[] = {USENSOR_1__TRIG_PIN, USENSOR_2__TRIG_PIN, USENSOR_3__TRIG_PIN, USENSOR_4__TRIG_PIN};
char DATA[5];


void setup()
{

  for (ALL_USENSORS)
  {

    DATA[INDEX] = SAFE_STATUS;

  }

  DATA[4] = '\0';


  Serial.begin(9600);


  INIT_USENSORS();


  delay(100);

}


void INIT_USENSORS()
{

  for (ALL_USENSORS)
  {

    pinMode(USENSOR_LIST[INDEX], OUTPUT);
    pinMode(USENSOR_LIST[INDEX] + 1, INPUT);

  }

}

void loop()
{


  for (ALL_USENSORS)
  {

    // [SEND A PULSE]
    {

      digitalWrite(USENSOR_LIST[INDEX], LOW);
      delayMicroseconds(2);
      digitalWrite(USENSOR_LIST[INDEX], HIGH);
      delayMicroseconds(10);
      digitalWrite(USENSOR_LIST[INDEX], LOW);

    }


    // [CHECK DISTANCES]
    {

      const long DURATION = pulseIn(USENSOR_LIST[INDEX] + 1, HIGH);
      const int DISTANCE = DURATION * 0.034 / 2;


      if (DISTANCE <= DANGER_DISTANCE_CM)
      {

        DATA[INDEX] = DANGER_STATUS;

      }
      else if (DISTANCE <= WARNING_DISTANCE_CM)
      {

        DATA[INDEX] = WARNING_STATUS;

      }
      else
      {

        DATA[INDEX] = SAFE_STATUS;

      }

    }

  }


  Serial.println(DATA);

}
