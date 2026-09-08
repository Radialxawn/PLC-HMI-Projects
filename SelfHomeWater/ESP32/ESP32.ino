#include <Wire.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ADS1X15.h>

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
float screen_view_button_x = 0;
float screen_view_button_x_v_pps = -10;
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
AsyncWebServer server(80);
bool server_begin_done = false;

const char* PARAM_INPUT_1 = "output";
const char* PARAM_INPUT_2 = "state";

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    html {font-family: Arial; display: inline-block; text-align: center;}
    h2 {font-size: 3.0rem;}
    p {font-size: 3.0rem;}
    body {max-width: 600px; margin:0px auto; padding-bottom: 25px;}
    .switch {position: relative; display: inline-block; width: 120px; height: 68px} 
    .switch input {display: none}
    .slider {position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: #ccc; border-radius: 6px}
    .slider:before {position: absolute; content: ""; height: 52px; width: 52px; left: 8px; bottom: 8px; background-color: #fff; -webkit-transition: .4s; transition: .4s; border-radius: 3px}
    input:checked+.slider {background-color: #b30000}
    input:checked+.slider:before {-webkit-transform: translateX(52px); -ms-transform: translateX(52px); transform: translateX(52px)}
  </style>
</head>
<body>
  <h2>Home Water</h2>
  %BUTTONPLACEHOLDER%
<script>function toggleCheckbox(element) {
  var xhr = new XMLHttpRequest();
  if(element.checked){ xhr.open("GET", "/update?output="+element.id+"&state=1", true); }
  else { xhr.open("GET", "/update?output="+element.id+"&state=0", true); }
  xhr.send();
}
</script>
</body>
</html>
)rawliteral";

String _server_processor(const String& var){
  if(var == "BUTTONPLACEHOLDER"){
    String buttons = "";
    buttons += "<h4>LED</h4><label class=\"switch\"><input type=\"checkbox\" onchange=\"toggleCheckbox(this)\" id=\"2\" " + _server_output_state(2) + "><span class=\"slider\"></span></label>";
    buttons += "<h4>PUMP</h4><label class=\"switch\"><input type=\"checkbox\" onchange=\"toggleCheckbox(this)\" id=\"25\" " + _server_output_state(25) + "><span class=\"slider\"></span></label>";
    return buttons;
  }
  return String();
}

String _server_output_state(int output){
  if(digitalRead(output)){
    return "checked";
  }
  else {
    return "";
  }
}

void _server_begin() {
  if (server_begin_done) {
    return;
  }
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/html", index_html, _server_processor);
  });
  server.on("/update", HTTP_GET, [] (AsyncWebServerRequest *request) {
    String inputMessage1;
    String inputMessage2;
    // GET input1 value on <ESP_IP>/update?output=<inputMessage1>&state=<inputMessage2>
    if (request->hasParam(PARAM_INPUT_1) && request->hasParam(PARAM_INPUT_2)) {
      inputMessage1 = request->getParam(PARAM_INPUT_1)->value();
      inputMessage2 = request->getParam(PARAM_INPUT_2)->value();
      digitalWrite(inputMessage1.toInt(), inputMessage2.toInt());
    }
    else {
      inputMessage1 = "No message sent";
      inputMessage2 = "No message sent";
    }
    Serial.print("GPIO: ");
    Serial.print(inputMessage1);
    Serial.print(" - Set to: ");
    Serial.println(inputMessage2);
    request->send(200, "text/plain", "OK");
  });
  server.begin();
  server_begin_done = true;
}
/////////
//INPUT//
/////////
const int input_run = 34;
const int input_stop = 35;
bool input_run_state = false;
bool input_stop_state = false;
Adafruit_ADS1115 input_adc;
float input_adc_voltage[] = {0, 0, 0, 0};
//////////
//OUTPUT//
//////////
String output_led_state = "off";
String output_pump_state = "off";
const int output_led = 2;
const int output_pump = 25;
////////
//PUMP//
////////
unsigned long pump_time_to_stop = 0;
const long pump_time_on_max = 10*60*1000;
float pump_amp_v_offset = 0;
float pump_amp_sensor_f = 20;
unsigned long pump_amp_cycle_time_start = 0;
float pump_amp_peak_l = 0;
float pump_amp_peak_h = 0;
float pump_amp_rms = 0;
float pump_water_sensor_f = 1000;
float pump_water_mm = 0;
float pump_water_mm_l = 600;
float pump_water_mm_h = 900;
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
  input_adc.begin();
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
void _loop_input() {
  input_run_state = digitalRead(input_run);
  input_stop_state = digitalRead(input_stop);
  for (int i = 0; i < 2; i++) {
    int16_t adc = input_adc.readADC_SingleEnded(i);
    input_adc_voltage[i] = input_adc.computeVolts(adc);
  }
}

String _get_wifi_signal_strength(int32_t rssi) {
  if (rssi <= -90) {
    return "[---]";
  } else if (rssi <= -70) {
    return "[#--]";
  } else if (rssi <= -50) {
    return "[##-]";
  } else {
    return "[###]";
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
  _server_begin();
}

float _mapf(float x, float in_min, float in_max, float out_min, float out_max) {
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

int _text_x_move(const String &str, float &x, float &v_pps, float dt) {
  int16_t x1, y1;
  uint16_t text_width, text_height;
  screen.getTextBounds(str, 0, 0, &x1, &y1, &text_width, &text_height);
  x += v_pps * dt;
  if (v_pps > 0) {
    if (x + text_width > SCREEN_WIDTH) {
      v_pps = -v_pps;
    }
  } else {
    if (x < 1) {
      v_pps = -v_pps;
    }
  }
  int rx = constrain(x, 0, SCREEN_WIDTH - text_width);
  return rx;
}

void _loop_screen_update() {
  unsigned long time_current = millis();
  if (time_current < screen_time_update_next) {
    return;
  }
  screen_time_update_next = time_current + screen_time_update_interval;
  float dt = screen_time_update_interval * 1e-3;
  screen.clearDisplay();
  screen.setTextSize(1);
  screen.setTextColor(SSD1306_WHITE);
  // WIFI
  int32_t rssi = WiFi.RSSI();
  String wifi_signal = WiFi.localIP().toString() + " " + _get_wifi_signal_strength(rssi);
  int wifi_x = _text_x_move(wifi_signal, screen_view_wifi_x, screen_view_wifi_x_v_pps, dt);
  screen.setCursor(wifi_x, 0);
  screen.println(wifi_signal);
  // BUTTON STATE
  String button_state = "Run: " + String(input_run_state) + " | Stop: " + String(input_stop_state);
  int button_x = _text_x_move(button_state, screen_view_button_x, screen_view_button_x_v_pps, dt);
  screen.setCursor(button_x, 8);
  screen.println(button_state);
  // PUMP
  bool pump = digitalRead(output_pump);
  int width = pump ? 7 : 15;
  int pump_water = round(_mapf(pump_water_mm, 0, pump_water_sensor_f, 0, 128));
  screen.fillRect(128-pump_water, 16, pump_water, width, SSD1306_WHITE);
  if (pump) {
    int pump_amp = round(_mapf(pump_amp_rms, 0, pump_amp_sensor_f * 0.5, 0, 128));
    screen.fillRect(128-pump_amp, 24, pump_amp, 5, SSD1306_WHITE);
    long pump_time_remain = constrain(pump_time_to_stop - time_current, 0, pump_time_on_max);
    int pump_time = round(_mapf(pump_time_remain, 0, pump_time_on_max, 0, 128));
    screen.fillRect(128-pump_time, 30, pump_time, 1, SSD1306_WHITE);
  }
  //
  screen.display();
}

void _loop_pump() {
  // Water level
  pump_water_mm = _mapf(input_adc_voltage[0], 0, 5, 0, pump_water_sensor_f);
  // Pump amp
  float amp = _mapf(input_adc_voltage[1] + pump_amp_v_offset, 0, 5, -pump_amp_sensor_f, pump_amp_sensor_f);
  long dt = millis() - pump_amp_cycle_time_start;
  if (dt < 500) {
    if (amp < pump_amp_peak_l) {
      pump_amp_peak_l = amp;
    }
    if (amp > pump_amp_peak_h) {
      pump_amp_peak_h = amp;
    }
  } else {
    float peak_to_peak = pump_amp_peak_h - pump_amp_peak_l;
    pump_amp_rms = peak_to_peak * 0.35355;
    pump_amp_peak_l = 0;
    pump_amp_peak_h = 0;
    pump_amp_cycle_time_start = millis();
  }
  // Pump action
  bool pump = digitalRead(output_pump);
  if (pump) {
    if (input_stop_state || millis() > pump_time_to_stop || pump_water_mm > pump_water_mm_h) {
      digitalWrite(output_pump, LOW);
    }
  } else {
    if (input_run_state) {
      digitalWrite(output_pump, HIGH);
      pump_time_to_stop = millis() + pump_time_on_max;
    }
  }
}

void loop() {
  _loop_input();
  _loop_wifi_connect();
  _loop_screen_update();
  _loop_pump();
}