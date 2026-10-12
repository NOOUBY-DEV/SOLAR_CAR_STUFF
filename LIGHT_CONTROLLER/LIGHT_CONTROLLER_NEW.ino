#include <Arduino_FreeRTOS.h>
#include <Adafruit_NeoPixel.h>


#define JOYSTICK_ACTIVATION_RANGE 0.99999
#define JOYSTICK_X_PIN A0
#define JOYSTICK_Y_PIN A1


typedef unsigned long ulong;
typedef unsigned char uchar;


typedef struct vec2
{
        double x, y;
}
vec2;

typedef struct joystick_data
{
        vec2 current;
        vec2 half_distance;
        vec2 full_distance;
}
joystick_data;


enum DIRECTION_NUMBERS
{
        LEFT,
        RIGHT,
        UP,
        DOWN,
        CENTER,
};


Adafruit_NeoPixel lf_light(SIDE_LIGHT__PIXEL_COUNT, LF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rf_light(SIDE_LIGHT__PIXEL_COUNT, RF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel lb_light(SIDE_LIGHT__PIXEL_COUNT, LB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rb_light(SIDE_LIGHT__PIXEL_COUNT, RB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);


Adafruit_NeoPixel* all_of_the_lights[] = {&lf_light, &rf_light, &lb_light, &rb_light};
Adafruit_NeoPixel* left_lights[] = {&lf_light, &lb_light};
Adafruit_NeoPixel* right_lights[] = {&rf_light, &rb_light};


joystick_data joystick;


void setup()
{
        start_scheduler();
}

void loop()
{
}

void start_scheduler()
{
        xTaskCreate(light_control__loop, "light_control__loop", 128, NULL, 1, NULL);
        xTaskCreate(BREAK_LOOP, "BREAK_LOOP", 32, NULL, 1, NULL);
        xTaskCreate(INPUT_LOOP, "INPUT_LOOP", 128, NULL, 1, NULL);


        vTaskStartScheduler();
}

void init__joystick()
{
        delay(200);

        joystick.half_distance.x = analogRead(JOYSTICK_X_PIN);
        joystick.half_distance.y = analogRead(JOYSTICK_Y_PIN);
        joystick.full_distance.x = joystick.half_distance.x * 2;
        joystick.full_distance.y = joystick.half_distance.y * 2;
}

void light_control__loop(void* args)
{

}

ulong get_joystick_direction()
{
        joystick.current.x = (analogRead(JOYSTICK_X_PIN) - joystick.half_distance.x) / joystick.full_distance.x) * 2;
        joystick.current.x = (analogRead(JOYSTICK_Y_PIN) - joystick.half_distance.y) / joystick.full_distance.y) * 2;

        if (abs(joystick.current.x) < JOYSTICK_ACTIVATION_RANGE && abs(joystick.current.y) < JOYSTICK_ACTIVATION_RANGE)
        {
                return CENTER;
        }

        if (abs(jostick.current.x) > abs(jostick.current.y))
        {
                if (joystick.current.x < 0)
                {
                        return LEFT;
                }
                else
                {
                        return RIGHT;
                }
        }
        else
        {
                if (joystick.current.y < 0)
                {
                        return DOWN;
                }
                else
                {
                        return UP;
                }
        }
}
