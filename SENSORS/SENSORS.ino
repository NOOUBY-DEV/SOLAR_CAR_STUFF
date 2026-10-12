#include <OneWire.h>
#include <DallasTemperature.h>


typedef unsigned char uchar;
typedef unsigned long ulong;


#define ULTRASOUND_COUNT 4
#define ULTRASOUND_START_PIN 2
#define ULTRASOUND_END_PIN (ULTRASOUND_START_PIN + (ULTRASOUND_COUNT * 2))
#define ULTRASOUND_TIMEOUT 20000
#define BATTERY_TEMP_SENSOR_PIN 13


enum ULTRASOUND_PINS
{
	LF_TRIG = ULTRASOUND_START_PIN,
	LF_ECHO,
	RF_TRIG,
	RF_ECHO,
	LB_TRIG,
	LB_ECHO,
	RB_TRIG,
	RB_ECHO,
};


uchar shared_buffer[24];
const uchar* ultrasound_buffer = &shared_buffer[0];
const double* battery_temp_buffer = (double*)(&shared_buffer[4]);


OneWire battery_temp_onewire(BATTERY_TEMP_SENSOR_PIN);
DallasTemperature battery_temp_sensor(&battery_temp_onewire);


void setup()
{
	Serial.begin(9600);

	check_type_sizes();

	assign_ultrasound_pins();

	battery_temp_sensor.begin();
}

void loop() 
{
	#define DEBUG

	get_ultrasound_distances(ultrasound_buffer);
	get_battery_temp(battery_temp_buffer);
	
	#if !defined(DEBUG)
	{
		Serial.write(shared_buffer, 24);
	}
	#else
	{
		Serial.write(shared_buffer, 4);
		Serial.println("");

		Serial.print("battery temperature : ");
		Serial.println(*battery_temp_buffer);
	}
	#endif
	
	delay(100);
}

void check_type_sizes()
{
	if ((sizeof(uchar) != 1) || (sizeof(ulong) != 4) || (sizeof(double) != 4))
	{
		Serial.println("ERROR");
		exit(1);
	}
}

void assign_ultrasound_pins()
{
	pinMode(LF_TRIG, OUTPUT);
	pinMode(RF_TRIG, OUTPUT);
	pinMode(LB_TRIG, OUTPUT);
	pinMode(RB_TRIG, OUTPUT);
	
	pinMode(LF_ECHO, INPUT);
	pinMode(RF_ECHO, INPUT);
	pinMode(LB_ECHO, INPUT);
	pinMode(RB_ECHO, INPUT);	
}

void get_ultrasound_distances(uchar* buffer)
{
	ulong buffer_index = 0;
	
	for (ulong ultrasound_index = ULTRASOUND_START_PIN; ultrasound_index < ULTRASOUND_END_PIN; ultrasound_index += 2, buffer_index ++)
	{	
		digitalWrite(ultrasound_index, LOW);
		delayMicroseconds(2);
		digitalWrite(ultrasound_index, HIGH);
		delayMicroseconds(10);
		digitalWrite(ultrasound_index, LOW);

		const ulong duration = pulseIn(ultrasound_index + 1, HIGH, ULTRASOUND_TIMEOUT);
		const ulong distance = duration * 0.017;

		buffer[buffer_index] = get_distance_status(distance);
	}
}

static inline uchar get_distance_status(const ulong distance)
{
	if (distance <= 50) return 'D';
	if (distance <= 100) return 'W';
	return 'S';
}

void get_battery_temp(double* buffer)
{	
	battery_temp_sensor.requestTemperatures();
	
	*buffer = battery_temp_sensor.getTempCByIndex(0);
}
