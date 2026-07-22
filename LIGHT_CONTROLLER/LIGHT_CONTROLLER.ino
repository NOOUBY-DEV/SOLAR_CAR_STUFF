#include <Arduino_FreeRTOS.h>
#include <Adafruit_NeoPixel.h>




#define YEILD_DELAY_MS(MS) vTaskDelay(MS / portTICK_PERIOD_MS);
#define YEILD_DELAY() vTaskDelay(10 / portTICK_PERIOD_MS);


#define TRUE 1
#define FALSE 0


#define NO_EVENTS 0
#define LIGHT_MODE_CONTROL 1
#define BLINK_CONTROL 2


#define LEFT 0
#define RIGHT 1


#define LF_LIGHT_PIN 0
#define RF_LIGHT_PIN 1
#define LB_LIGHT_PIN 2
#define RB_LIGHT_PIN 3


#define SIDE_LIGHT__PIXEL_COUNT 18
#define SIDE_LIGHT__BLINKER_PIXEL_COUNT 6


#define JOYSTICK_VRX_PIN A1
#define JOYSTICK_VRY_PIN A0
#define JOYSTICK_ACTIVATION_RANGE 0.999


#define BLINK_TIMES 5
#define BLINK_TIME_MS 500


typedef struct
{

  double X;
  double Y;

}
VECTOR2_DOUBLE;


VECTOR2_DOUBLE JOYSTICK;


Adafruit_NeoPixel LF_LIGHT(SIDE_LIGHT__PIXEL_COUNT, LF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel RF_LIGHT(SIDE_LIGHT__PIXEL_COUNT, RF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel LB_LIGHT(SIDE_LIGHT__PIXEL_COUNT, LB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel RB_LIGHT(SIDE_LIGHT__PIXEL_COUNT, RB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);


Adafruit_NeoPixel* LIGHT_LIST[] = {&LF_LIGHT, &LB_LIGHT, &RF_LIGHT, &RB_LIGHT, NULL};



VECTOR2_DOUBLE JOYSTICK_MAX_TOTAL;
VECTOR2_DOUBLE JOYSTICK_MAX_HALF;



char IS_WHITE_MODE = TRUE;


char JOYSTICK_IS_LOCKED = FALSE;


char TAILLIGHT_USED = FALSE;



void setup()
{

  INIT_JOYSTICK();


  INIT_SERIAL();


  INIT_LIGHTS();


  xTaskCreate(BREAK_LOOP, "BREAK_LOOP", 32, NULL, 1, NULL);
  xTaskCreate(INPUT_LOOP, "INPUT_LOOP", 128, NULL, 1, NULL);


  vTaskStartScheduler();

}


void loop()
{
}


void INIT_SERIAL()
{

  Serial.begin(9600);

}


void INIT_JOYSTICK()
{

  delay(500);


  JOYSTICK_MAX_HALF.X = analogRead(JOYSTICK_VRX_PIN);
  JOYSTICK_MAX_HALF.Y = analogRead(JOYSTICK_VRY_PIN);

  JOYSTICK_MAX_TOTAL.X = JOYSTICK_MAX_HALF.X * 2;
  JOYSTICK_MAX_TOTAL.Y = JOYSTICK_MAX_HALF.Y * 2;

}


void INIT_LIGHTS()
{

  for (unsigned char INDEX = 0; LIGHT_LIST[INDEX] != NULL; INDEX ++)
  {

    Adafruit_NeoPixel* LIGHT = LIGHT_LIST[INDEX];


    LIGHT->begin();
    LIGHT->setBrightness(50);
    LIGHT->show();

  }

}


void SET_HEADLIGHT_COLOR(const unsigned char R_VALUED, const unsigned char G_VALUED, const unsigned char B_VALUED)
{

  for (unsigned char INDEX = 0; LIGHT_LIST[INDEX] != NULL; INDEX ++)
  {

    Adafruit_NeoPixel* LIGHT = LIGHT_LIST[INDEX];


    for (unsigned char PIXEL_INDEX = 0; PIXEL_INDEX < SIDE_LIGHT__PIXEL_COUNT; PIXEL_INDEX ++)
    {

      LF_LIGHT.setPixelColor(PIXEL_INDEX, LF_LIGHT.Color(R_VALUED, G_VALUED, B_VALUED));
      RF_LIGHT.setPixelColor(PIXEL_INDEX, RF_LIGHT.Color(R_VALUED, G_VALUED, B_VALUED));
      
    }


    LF_LIGHT.show();
    RF_LIGHT.show();

  }

}



void BLINK(const int DIRECTION)
{

  TAILLIGHT_USED = TRUE;


  const unsigned char STARTING_INDEX = 0 + ((DIRECTION == RIGHT) * 2);


  for (unsigned char COUNTER = 0; COUNTER < BLINK_TIMES; COUNTER ++)
  {

    SET_BLINK_COLOR(STARTING_INDEX, 0, 0, 0);


    YEILD_DELAY_MS(BLINK_TIME_MS)


    SET_BLINK_COLOR(STARTING_INDEX, 255, 255, 0);


    YEILD_DELAY_MS(BLINK_TIME_MS)

  }


  SET_BLINK_COLOR(STARTING_INDEX, 0, 0, 0);


  TAILLIGHT_USED = FALSE;

}


void EMERGENCY_LIGHT_MODE()
{

  TAILLIGHT_USED = TRUE;


  while (TRUE)
  {

    // [BLINK ALL LIGHTS]
    {

      SET_BLINK_COLOR(0, 0, 0, 0);
      SET_BLINK_COLOR(2, 0, 0, 0);


      YEILD_DELAY_MS(BLINK_TIME_MS)


      SET_BLINK_COLOR(0, 255, 255, 0);
      SET_BLINK_COLOR(2, 255, 255, 0);


      YEILD_DELAY_MS(BLINK_TIME_MS)
      
    }


    // [BREAK IF JOYSTICK UP PRESSED]
    {

      JOYSTICK.Y = ((analogRead(JOYSTICK_VRY_PIN) - JOYSTICK_MAX_HALF.Y) / JOYSTICK_MAX_TOTAL.Y) * 2;


      if (JOYSTICK.Y >= JOYSTICK_ACTIVATION_RANGE)
      {

        SET_BLINK_COLOR(0, 0, 0, 0);
        SET_BLINK_COLOR(2, 0, 0, 0);


        break;

      }

    }


    YEILD_DELAY();

  }


  TAILLIGHT_USED = FALSE;

}


void SET_BLINK_COLOR(unsigned char STARTING_INDEX, unsigned char R_VALUED, const unsigned char G_VALUED, const unsigned char B_VALUED)
{

  for (unsigned char LIGHT_INDEX = STARTING_INDEX; LIGHT_INDEX < STARTING_INDEX + 2; LIGHT_INDEX ++)
  {

    for (unsigned char PIXEL_INDEX = SIDE_LIGHT__PIXEL_COUNT - SIDE_LIGHT__BLINKER_PIXEL_COUNT; PIXEL_INDEX < SIDE_LIGHT__PIXEL_COUNT; PIXEL_INDEX ++)
    {

      LIGHT_LIST[LIGHT_INDEX]->setPixelColor(PIXEL_INDEX, LIGHT_LIST[LIGHT_INDEX]->Color(R_VALUED, G_VALUED, B_VALUED));

    }


    LIGHT_LIST[LIGHT_INDEX]->show();

  }

}


void SET_TAILLIGHT_COLOR(unsigned char R_VALUED, const unsigned char G_VALUED, const unsigned char B_VALUED)
{

  for (unsigned char PIXEL_INDEX = 0; PIXEL_INDEX < SIDE_LIGHT__PIXEL_COUNT - (TAILLIGHT_USED * SIDE_LIGHT__BLINKER_PIXEL_COUNT); PIXEL_INDEX ++)
  {

    LB_LIGHT.setPixelColor(PIXEL_INDEX, LB_LIGHT.Color(R_VALUED, G_VALUED, B_VALUED));
    RB_LIGHT.setPixelColor(PIXEL_INDEX, RB_LIGHT.Color(R_VALUED, G_VALUED, B_VALUED));

  }


  LB_LIGHT.show();
  RB_LIGHT.show();

}


void INPUT_LOOP(void* ARG)
{

  while (TRUE)
  {

    if (INPUT_EVENT() != LIGHT_MODE_CONTROL)
    {

      if (IS_WHITE_MODE)
      {

        SET_HEADLIGHT_COLOR(255, 255, 255);

      }
      else
      {

        SET_HEADLIGHT_COLOR(255, 255, 0);

      }

    }


    YEILD_DELAY();

  }

}


int INPUT_EVENT()
{


  JOYSTICK.X = ((analogRead(JOYSTICK_VRX_PIN) - JOYSTICK_MAX_HALF.X) / JOYSTICK_MAX_TOTAL.X) * 2;
  JOYSTICK.Y = ((analogRead(JOYSTICK_VRY_PIN) - JOYSTICK_MAX_HALF.Y) / JOYSTICK_MAX_TOTAL.Y) * 2;


  // [PRINT JOYSTICK POSITIONS]
  {

    Serial.print("[&] JOYSTICK.X  :  ");
    Serial.print(JOYSTICK.X);
    Serial.print("  |  JOYSTICK.Y  :  ");
    Serial.println(JOYSTICK.Y);
    
  }


  if (abs(JOYSTICK.X) < JOYSTICK_ACTIVATION_RANGE && abs(JOYSTICK.Y) < JOYSTICK_ACTIVATION_RANGE)
  {

    if (JOYSTICK_IS_LOCKED)
    {

      JOYSTICK_IS_LOCKED = FALSE;

    }


    return NO_EVENTS;

  }


  if (JOYSTICK_IS_LOCKED)
  {

    return NO_EVENTS;

  }


  if (JOYSTICK.X >= JOYSTICK_ACTIVATION_RANGE)
  {

    Serial.println("[$] =================== [BLINK RIGHT ACTIVATED] ===================");


    JOYSTICK_IS_LOCKED = TRUE;


    BLINK(RIGHT);


    return BLINK_CONTROL;

  }
  if (JOYSTICK.X <= -JOYSTICK_ACTIVATION_RANGE)
  {

    Serial.println("[$] =================== RIGHT KEY ACTIVATED  ===================");


    JOYSTICK_IS_LOCKED = TRUE;


    BLINK(LEFT);


    return BLINK_CONTROL;

  }
  if (JOYSTICK.Y >= JOYSTICK_ACTIVATION_RANGE)
  {

    Serial.println("[$] =================== [EMERGENCY LIGHT ACTIVATED] ===================");


    JOYSTICK_IS_LOCKED = TRUE;


    EMERGENCY_LIGHT_MODE();


    return BLINK_CONTROL;

  }
  if (JOYSTICK.Y <= -JOYSTICK_ACTIVATION_RANGE)
  {

    Serial.println("[$] =================== [COLOR SWITCH MODE ACTIVATED] ===================");


    JOYSTICK_IS_LOCKED = TRUE;


    IS_WHITE_MODE = !IS_WHITE_MODE;


    return LIGHT_MODE_CONTROL;

  }


  YEILD_DELAY();


  return NO_EVENTS;

}


void BREAK_LOOP(void* ARG)
{

  #define CRASH_SENSOR_PIN 13
  #define CRASH_SENSOR_STATUS digitalRead(CRASH_SENSOR_PIN)


  pinMode(CRASH_SENSOR_PIN, INPUT_PULLUP);


  while (TRUE)
  {

    if (CRASH_SENSOR_STATUS == LOW)
    {

      SET_TAILLIGHT_COLOR(255, 0, 0);

    }
    else
    {

      SET_TAILLIGHT_COLOR(0, 0, 0);

    }


    YEILD_DELAY();
    
  }

}
