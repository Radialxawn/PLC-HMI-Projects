#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>

//////////
//SCREEN//
//////////
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
const byte screen_address = 0x3C;
Adafruit_SSD1306 screen(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
unsigned long screen_time_check_next = 0;
const long screen_time_check_interval = 5000;
unsigned long screen_time_update_next = 0;
const long screen_time_update_interval = 10;
///////////////
//SCREEN-VIEW//
///////////////
float screen_view_wifi_x = 0;
float screen_view_wifi_x_v_pps = 10; // pixel per sec
////////
//WIFI//
////////
const char* wifi_ssid = "SUONG";
const char* wifi_password = "11111111";
unsigned long wifi_time_retry_next = 0;
const long wifi_time_retry_interval = 5000;
//////////
//SERVER//
//////////
WiFiServer server(80);
String server_header;
unsigned long server_time_current = millis();
unsigned long server_time_last = 0; 
const long server_timeout = 2000;
/////////
//INPUT//
/////////
const int input_run = 36;
const int input_stop = 39;
//////////
//OUTPUT//
//////////
String output_led_state = "off";
String output_pump_state = "off";
const int output_led = 2;
const int output_pump = 26;

/////////////////
//PROCESS-SETUP//
/////////////////
void _setup_input_output() {
  // INPUT
  pinMode(input_run, INPUT);
  pinMode(input_stop, INPUT);
  // OUTPUT
  pinMode(output_led, OUTPUT);
  pinMode(output_pump, OUTPUT);
  digitalWrite(output_led, LOW);
  digitalWrite(output_pump, LOW);
}

void _setup_i2c() {
  screen.begin(SSD1306_SWITCHCAPVCC, screen_address);
}

void setup() {
  Serial.begin(115200);
  _setup_input_output();
  _setup_i2c();
  delay(1000);
}

////////////////
//PROCESS-LOOP//
////////////////
String _get_wifi_signal_strength(int32_t rssi) {
  if (rssi <= -90) {
    return "[-----]";
  } else if (rssi <= -80) {
    return "[#----]";
  } else if (rssi <= -70) {
    return "[##---]";
  } else if (rssi <= -60) {
    return "[###--]";
  } else if (rssi <= -50) {
    return "[####-]";
  } else {
    return "[#####]";
  }
}

void _loop_wifi_connect() {
  unsigned long time_current = millis();
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  if (time_current < wifi_time_retry_next) {
    return;
  }
  wifi_time_retry_next = time_current + wifi_time_retry_interval;
  WiFi.disconnect();
  WiFi.begin(wifi_ssid, wifi_password);
  server.close();
  server.begin();
}

void _loop_screen_update() {
  unsigned long time_current = millis();
  if (time_current < screen_time_update_next) {
    return;
  }
  screen_time_update_next = time_current + screen_time_update_interval;
  screen.clearDisplay();
  screen.setTextSize(1);
  screen.setTextColor(SSD1306_WHITE);
  // WIFI
  int16_t x1, y1;
  uint16_t text_width, text_height;
  int32_t rssi = WiFi.RSSI();
  String wifi_signal = WiFi.localIP().toString() + " " + _get_wifi_signal_strength(rssi);
  screen.getTextBounds(wifi_signal, 0, 0, &x1, &y1, &text_width, &text_height);
  screen_view_wifi_x += screen_view_wifi_x_v_pps * screen_time_update_interval * 1e-3;
  if (screen_view_wifi_x_v_pps > 0) {
    if (screen_view_wifi_x + text_width > SCREEN_WIDTH) {
      screen_view_wifi_x_v_pps = -screen_view_wifi_x_v_pps;
    }
  } else {
    if (screen_view_wifi_x < 1) {
      screen_view_wifi_x_v_pps = -screen_view_wifi_x_v_pps;
    }
  }
  int x = constrain(screen_view_wifi_x, 0, SCREEN_WIDTH - text_width);
  screen.setCursor(x, 0);
  screen.println(wifi_signal);
  // WATER LEVEL
  screen.display();
}

void _loop_server(){
  if (WiFi.status() != WL_CONNECTED) {
    return;
  }
  WiFiClient client = server.available();   // Listen for incoming clients
  if (client) {                             // If a new client connects,
    server_time_current = millis();
    server_time_last = server_time_current;
    String currentLine = "";                // make a String to hold incoming data from the client
    while (client.connected() && server_time_current - server_time_last <= server_timeout) {  // loop while the client's connected
      server_time_current = millis();
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        server_header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();
            
            // turns the GPIOs on and off
            if (server_header.indexOf("GET /led/on") >= 0) {
              output_led_state = "on";
              digitalWrite(output_led, HIGH);
            } else if (server_header.indexOf("GET /led/off") >= 0) {
              output_led_state = "off";
              digitalWrite(output_led, LOW);
            } else if (server_header.indexOf("GET /pump/on") >= 0) {
              output_pump_state = "on";
              digitalWrite(output_pump, HIGH);
            } else if (server_header.indexOf("GET /pump/off") >= 0) {
              output_pump_state = "off";
              digitalWrite(output_pump, LOW);
            }
            
            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons 
            // Feel free to change the background-color and font-size attributes to fit your preferences
            client.println("<style>html { font-family: Helvetica; display: inline-block; margin: 0px auto; text-align: center;}");
            client.println(".button { background-color: #4CAF50; border: none; color: white; padding: 16px 40px;");
            client.println("text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}");
            client.println(".button2 {background-color: #555555;}</style></head>");
            
            // Web Page Heading
            client.println("<body><h1>Home Water</h1>");
            
            // Display current state, and ON/OFF buttons for LED  
            client.println("<p>LED - State " + output_led_state + "</p>");
            // If the output_led_state is off, it displays the ON button       
            if (output_led_state=="off") {
              client.println("<p><a href=\"/led/on\"><button class=\"button\">ON</button></a></p>");
            } else {
              client.println("<p><a href=\"/led/off\"><button class=\"button button2\">OFF</button></a></p>");
            } 
               
            // Display current state, and ON/OFF buttons for PUMP  
            client.println("<p>PUMP - State " + output_pump_state + "</p>");
            // If the output_pump_state is off, it displays the ON button       
            if (output_pump_state=="off") {
              client.println("<p><a href=\"/pump/on\"><button class=\"button\">ON</button></a></p>");
            } else {
              client.println("<p><a href=\"/pump/off\"><button class=\"button button2\">OFF</button></a></p>");
            }
            client.println("</body></html>");
            
            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    server_header = "";
    // Close the connection
    client.stop();
  }
}

void loop() {
  _loop_wifi_connect();
  _loop_screen_update();
  _loop_server();
}