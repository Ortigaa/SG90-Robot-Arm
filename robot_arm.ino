// Include the servo library
#include <Servo.h>

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// define the pins used for the servos (all digital PWM)
int usedPins[] = {3, 5, 6, 9, 10};

// Create instances of Servo object
Servo servos[5];

// variables to hold the parsed data
int pos = 0;
int servo = 0;
int velocity = 10; // so this is really ms, and controls the delay in the for loop
int positions[5];

boolean newData = false;

//============
void prepareServos(){
  for (int count = 0; count < 5; count ++){
    servos[count].attach(usedPins[count]); // Attach servos to pins
    servos[count].write(0); // move all motos to 0
    positions[count] = 0;
    delay(100);
  }

    //test all motors
  for (int ser = 0; ser < 5; ser ++){
    for (pos = 0; pos <= 180; pos += 1.0) {
      servos[ser].write(pos);
      delay(velocity);
    }
    for (pos = 180; pos >= 0; pos -= 1.0){
      servos[ser].write(pos);
      delay(velocity);
    }
  }
}

//============
void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}
//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index

    strtokIndx = strtok(tempChars, ","); //get the first part to define the servo
    servo = atoi(strtokIndx);

    strtokIndx = strtok(NULL, ","); // get the second part to define the position
    pos = atoi(strtokIndx);

}


//============
void setup() {
  prepareServos();
  Serial.begin(9600);
  Serial.println("Enter data in this format: <servo(int), pos(int)>");
  Serial.println();

}

void loop() {

  recvWithStartEndMarkers();
  if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        // This is my first attemp to control the speed, but somehow does not work
//        if (positions[servo] > pos){
//          for(int p = positions[servo]; p = pos; p-=1)
//           servos[servo].write(p);
//           delay(velocity);
//        }
//        else if (servos[servo].read() < pos){
//         for(int p = positions[servo]; p = pos; p+=1)
//           servos[servo].write(p);
//           delay(velocity);
//        }
        // No speed control
        servos[servo].write(pos);
        positions[servo] = pos;
        newData = false;
        for (int i = 0; i<5; i++){
          Serial.println(positions[i]);
        }
        
    }
}
