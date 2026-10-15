#include <Arduino_FreeRTOS.h>
#include <Adafruit_NeoPixel.h>


#define TRUE 1
#define FALSE 0
#define forever while(TRUE)

#define YIELD_LOOP_TIME 50

#define yield() vTaskDelay(10 / portTICK_PERIOD_MS);
#define yield_time(TIME) vTaskDelay(TIME / portTICK_PERIOD_MS);
#define yield_time_until(condition, total_time, triggered) \
for (ulong time = 0; time < total_time; time += YIELD_LOOP_TIME) \
{ \
        if (condition) triggered = TRUE; break; \
        \
        yield_time(YIELD_LOOP_TIME); \
} \
triggered = FALSE; \

#define JOYSTICK_ACTIVATION_RANGE 0.9999
#define JOYSTICK_X_PIN A0
#define JOYSTICK_Y_PIN A1
#define BRAKE_TRIG_PIN 13
#define BRAKE_ECHO_PIN 12
#define BRAKE_POINT 4
#define LIGHT_ROWS 3
#define LIGHT_ROW_WIDTH 10
#define get_light_index(x, y) ( (y * LIGHT_ROW_WIDTH) + x )


typedef unsigned long ulong;
typedef unsigned char uchar;

typedef struct color3
{
        uchar r, g ,b, o;
}
color3;

typedef struct vec2
{
        double x, y;
}
vec2;

typedef struct light_section
{
        ulong start, last;
}
light_section;

typedef struct joystick_data
{
        vec2 current;
        vec2 half_distance;
        vec2 full_distance;
        ulong current_direction;
}
joystick_data;

ulong in_control_mode = TRUE;


enum DIRECTION_NUMBERS
{
        LEFT = 0,
        RIGHT,
        UP,
        DOWN,
        CENTER,
};

enum LIGHT_PINS
{
        LF_LIGHT_PIN = 0,
        RF_LIGHT_PIN,
        LB_LIGHT_PIN,
        RB_LIGHT_PIN,
};

enum FILL_SECTIONS
{
        FILL_SECTION = 0,
        CONTROL_SECTION,
};


Adafruit_NeoPixel lf_light(SIDE_light__PIXEL_COUNT, LF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rf_light(SIDE_light__PIXEL_COUNT, RF_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel lb_light(SIDE_light__PIXEL_COUNT, LB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel rb_light(SIDE_light__PIXEL_COUNT, RB_LIGHT_PIN, NEO_GRB + NEO_KHZ800);


Adafruit_NeoPixel* olive_delights[] = {&lf_light, &rf_light, &lb_light, &rb_light, NULL};
Adafruit_NeoPixel* left_lights[] = {&lf_light, &lb_light, NULL};
Adafruit_NeoPixel* right_lights[] = {&rf_light, &rb_light, NULL};
Adafruit_NeoPixel* back_lights[] = {&lb_light, &rb_light, NULL};

light_section light_sections[] =
{
        {0, 5},
        {6, 9},
};

const color3 BLACK = {0, 0, 0};
const color3 WHITE = {255, 255, 255};
const color3 RED = {255, 0, 0};
const color3 YELLOW = {255, 255, 0};

joystick_data joystick;




void setup()
{
        init__joystick();

        init__lights();

        start__scheduler();
}

void loop()
{Adafruit_NeoPixel*
}

void start__scheduler()
{
        xTaskCreate(light_control__loop, "light_control__loop", 64, NULL, 1, NULL);
        xTaskCreate(set_joystick_direction__loop, "set_joystick_direction__loop", 64, NULL, 1, NULL);
        xTaskCreate(brake_light__loop, "brake_light__loop", 64, NULL, 1, NULL);

        vTaskStartScheduler();
}

void init__lights()
{
        for (ulong index = 0; olive_delights[index] != NULL; index ++)
        {
                Adafruit_NeoPixel* light = olive_delights[index];

                light->begin();
                light->setBrightness(100);
                light->show();
        }
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
        forever
        {
                if (in_control_mode)
                {
                        continue;
                }

                const ulong current_direction = joystick.current_direction;

                if (current_direction == CENTER)
                {
                        in_control_mode = FALSE;

                        yield();

                        continue;
                }
                else
                {
                        in_control_mode = TRUE;
                }

                switch (current_direction)
                {
                        case LEFT  : break;

                        case RIGHT : break;

                        case UP    : break;

                        case DOWN  : break;
                }

                in_control_mode = FALSE;

                yield();
        }
}

void set_joystick_direction__loop(void* args)
{
        forever
        {
                joystick.current.x = (analogRead(JOYSTICK_X_PIN) - joystick.half_distance.x) / joystick.full_distance.x) * 2;
                joystick.current.x = (analogRead(JOYSTICK_Y_PIN) - joystick.half_distance.y) / joystick.full_distance.y) * 2;

                if (abs(joystick.current.x) < JOYSTICK_ACTIVATION_RANGE && abs(joystick.current.y) < JOYSTICK_ACTIVATION_RANGE)
                {
                        joystick.current_direction = CENTER;

                        yield();

                        continue;
                }

                if (abs(jostick.current.x) > abs(jostick.current.y))
                {
                        if (joystick.current.x < 0)
                        {
                                joystick.current_direction = LEFT;
                        }
                        else
                        {
                                joystick.current_direction = RIGHT;
                        }
                }
                else
                {
                        if (joystick.current.y < 0)
                        {
                                joystick.current_direction = DOWN;
                        }
                        else
                        {
                                joystick.current_direction = UP;
                        }
                }

                yield();
        }
}

void brake_light__loop(void* args)
{
        forever
        {
                digitalWrite(BRAKE_TRIG_PIN, LOW);
                delayMicroseconds(2);
                digitalWrite(BRAKE_TRIG_PIN, HIGH);
                delayMicroseconds(10);
                digitalWrite(BRAKE_TRIG_PIN, HIGH);

                const long DISTANCE = pulseIn(BRAKE_ECHO_PIN, HIGH, 3000) * 0.017;

                if (DISTANCE > 0 && DISTANCE <= BRAKE_POINT)
                {
                        color__light_section(back_lights[0], FILL_SECTION, RED);
                        color__light_section(back_lights[1], FILL_SECTION, RED);
                }
                else
                {
                        color__light_section(back_lights[0], FILL_SECTION, BLACK);
                        color__light_section(back_lights[1], FILL_SECTION, BLACK);
                }

                yield();
        }
}

void color__light_section(Adafruit_NeoPixel* light, const ulong section_index, const color3 color)
{
        light_section section = light_sections[section_index];

        for (ulong y_index = 0; y_index < LIGHT_ROWS; y_index ++)
        {
                for (ulong x_index = section.start; x_index <= section.last; x_index ++)
                {
                        light->setPixelColor(get_light_index(x_index, y_index), light->Color(color.r, color.g, color.b));
                }
        }
}

class light_controls
{
        public:
                static void blink_direction(ulong direction)
                {
                        Adafruit_NeoPixel** light_array;

                        if (direction == LEFT)
                        {
                                light_array = left_lights;
                        }
                        else
                        {
                                light_array = right_lights;
                        }

                        color__light_section(light_array[0], CONTROL_SECTION, YELLOW);
                        color__light_section(light_array[1], CONTROL_SECTION, YELLOW);

                        ulong triggered;

                        yield_time_until(joystick.current_direction == direction, 500);

                        if (triggered)
                        {
                                return
                        }
                }
}
