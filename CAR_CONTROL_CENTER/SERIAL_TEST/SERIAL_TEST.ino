unsigned long COUNT = 1;


void setup()
{

  Serial.begin(9600);


  delay(1000);

}


void loop()
{

  Serial.print("HELLO WORLD  |  ");
  Serial.println(COUNT);


  COUNT ++;


  delay(1000);

}
