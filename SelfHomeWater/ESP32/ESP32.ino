#include <Wire.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>
#include <Arduino_JSON.h>

/////////
//CONST//
/////////
const long c_min_to_ms = 60000;
const float c_peak_peak_to_rms = 0.35355;

//////////
//CONFIG//
//////////
Preferences config;
String config_wifi_ssid = "";
String config_wifi_pass = "";
int config_water_level_max_mm = 900;
int config_pump_duration_min = 10;
int config_pump_begin_24hour = 9;
int config_pump_end_24hour = 17;
int config_pump_interval_min = 120;

void _config_load() {
  config.begin("config", true);
  config_wifi_ssid = config.getString("config_wifi_ssid", "SUONG");
  config_wifi_pass = config.getString("config_wifi_pass", "11111111");
  config_water_level_max_mm = config.getInt("config_water_level_max_mm", 900);
  config_pump_duration_min = config.getInt("config_pump_duration_min", 10);
  config_pump_begin_24hour = config.getInt("config_pump_begin_24hour", 9);
  config_pump_end_24hour = config.getInt("config_pump_end_24hour", 17);
  config_pump_interval_min = config.getInt("config_pump_interval_min", 120);
  config.end();
}

void _config_save() {
  config_water_level_max_mm = constrain(config_water_level_max_mm, 600, 900);
  config_pump_duration_min = constrain(config_pump_duration_min, 10, 20);
  config_pump_begin_24hour = constrain(config_pump_begin_24hour, 8, 11);
  config_pump_end_24hour = constrain(config_pump_end_24hour, 13, 18);
  config_pump_interval_min = constrain(config_pump_interval_min, 60, 180);
  config.begin("config", false);
  config.putString("config_wifi_ssid", config_wifi_ssid);
  config.putString("config_wifi_pass", config_wifi_pass);
  config.putInt("config_water_level_max_mm", config_water_level_max_mm);
  config.putInt("config_pump_duration_min", config_pump_duration_min);
  config.putInt("config_pump_begin_24hour", config_pump_begin_24hour);
  config.putInt("config_pump_interval_min", config_pump_interval_min);
  config.end();
}

/////////
//STATE//
/////////
Preferences state;
uint64_t state_pump_tick_last = 0;

void _state_load() {
  state.begin("state", true);
  state_pump_tick_last = config.getULong64("state_pump_tick_last", 0);
  config.end();
}

void _state_save() {
  config.begin("config", false);
  config.putLong("state_pump_tick_last", state_pump_tick_last);
  config.end();
}
//////////
//SCREEN//
//////////
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
const byte screen_address = 0x3C;
Adafruit_SSD1306 screen(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
unsigned long screen_update_last_ms = 0;
const int screen_update_interval_ms = 10;
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
unsigned long wifi_retry_time_ms = 0;
const int wifi_time_retry_interval = 5000;
/////////
//INPUT//
/////////
const int input_run_pin = 34;
const int input_stop_pin = 35;
bool input_run = false;
bool input_stop = false;
Adafruit_ADS1115 input_adc;
float input_adc_voltage[] = {0, 0, 0, 0};
//////////
//OUTPUT//
//////////
const int output_led_pin = 2;
const int output_pump_pin = 25;
////////
//PUMP//
////////
unsigned long pump_begin_ms = 0;
unsigned long pump_time_remain_ms = 0;
float pump_sensor_offset_v = 0;
float pump_sensor_factor = 20;
unsigned long pump_sensor_cycle_begin_ms = 0;
float pump_sensor_peak_l_amp = 0;
float pump_sensor_peak_h_amp = 0;
float pump_current_amp = 0;
float pump_water_sensor_factor = 1000;
float pump_water_level_mm = 0;
//////////
//SERVER//
//////////
AsyncWebServer server(80);
bool server_begin_done = false;

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    html {font-family: Arial; display: inline-block; text-align: center;}
    h2 {font-size: 2.0rem;}
    p {font-size: 2.0rem;}
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
  <p>
    <span>Water Level</span>
    <span id="water_level">--</span>
    <span>mm</span>
  </p>
  <p>
    <span>Pump Current</span>
    <span id="pump_current">--</span>
    <span>amp</span>
  </p>
  <p>
    <span>Pump Time Remain</span>
    <span id="pump_time_remain">--</span>
    <span>sec</span>
  </p>
<script>
function dataGet() {
  fetch('/api/data')
    .then(response => response.json())
    .then(data => {
      document.getElementById('water_level').innerText = data.water_level;
      document.getElementById('pump_current').innerText = data.pump_current.toFixed(3);
      document.getElementById('pump_time_remain').innerText = (data.pump_time_remain*1e-3).toFixed(0);
  });
}
setInterval(dataGet, 500);
</script>
</body>
</html>
)rawliteral";

String _server_data_json_get() {
  JSONVar doc;
  doc["water_level"] = round(pump_water_level_mm);
  doc["pump_current"] = pump_current_amp;
  doc["pump_time_remain"] = pump_time_remain_ms;
  String result = JSON.stringify(doc);
  return result;
}

void _server_begin() {
  if (server_begin_done) {
    return;
  }
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/html", index_html);
  });
  server.on("/api/data", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send_P(200, "application/json", _server_data_json_get().c_str());
  });
  server.begin();
  server_begin_done = true;
}
/////////////////
//PROCESS-SETUP//
/////////////////
void _setup_input_output() {
  // INPUT
  pinMode(input_run_pin, INPUT);
  pinMode(input_stop_pin, INPUT);
  // OUTPUT
  pinMode(output_led_pin, OUTPUT);
  pinMode(output_pump_pin, OUTPUT);
  digitalWrite(output_led_pin, LOW);
  digitalWrite(output_pump_pin, LOW);
}

void _setup_i2c() {
  screen.begin(SSD1306_SWITCHCAPVCC, screen_address);
  input_adc.begin();
}

void setup() {
  Serial.begin(115200);
  _setup_input_output();
  _setup_i2c();
  _config_load();
  delay(1000);
}

////////////////
//PROCESS-LOOP//
////////////////
bool _timeout(unsigned long &last_ms, unsigned long duration_ms, bool record) {
  unsigned long current_ms = millis();
  if (current_ms - last_ms >= duration_ms) {
    if (record) {
      last_ms = current_ms;
    }
    return true;
  }
  return false;
}

void _loop_input() {
  input_run = digitalRead(input_run_pin);
  input_stop = digitalRead(input_stop_pin);
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
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }
  if (!_timeout(wifi_retry_time_ms, wifi_time_retry_interval, true)) {
    return;
  }
  WiFi.disconnect();
  WiFi.begin(config_wifi_ssid, config_wifi_pass);
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
    if (x < 0) {
      v_pps = -v_pps;
    }
  }
  int rx = constrain(x, 0, SCREEN_WIDTH - text_width);
  return rx;
}

void _loop_screen_update() {
  if (!_timeout(screen_update_last_ms, screen_update_interval_ms, true)) {
    return;
  }
  unsigned long current_ms = millis();
  float dt = screen_update_interval_ms * 1e-3;
  screen.clearDisplay();
  screen.setTextSize(1);
  screen.setTextColor(SSD1306_WHITE);
  // WIFI
  int32_t rssi = WiFi.RSSI();
  String wifi_signal = WiFi.localIP().toString() + " " + _get_wifi_signal_strength(rssi);
  int wifi_x = _text_x_move(wifi_signal, screen_view_wifi_x, screen_view_wifi_x_v_pps, dt);
  screen.setCursor(wifi_x, 0);
  screen.println(wifi_signal);
  // BUTTON
  String button_state = "Run: " + String(input_run) + " | Stop: " + String(input_stop);
  int button_x = _text_x_move(button_state, screen_view_button_x, screen_view_button_x_v_pps, dt);
  screen.setCursor(button_x, 8);
  screen.println(button_state);
  // PUMP
  bool pump = digitalRead(output_pump_pin);
  int width = pump ? 7 : 15;
  int water_level = round(_mapf(pump_water_level_mm, 0, config_water_level_max_mm, 0, 128));
  screen.fillRect(128-water_level, 16, water_level, width, SSD1306_WHITE);
  if (pump) {
    int pump_current = round(_mapf(pump_current_amp, 0, pump_sensor_factor*c_peak_peak_to_rms, 0, 128));
    screen.fillRect(128-pump_current, 24, pump_current, 5, SSD1306_WHITE);
    unsigned long pump_duration_ms = config_pump_duration_min * c_min_to_ms;
    int pump_time_remain = round(_mapf(pump_time_remain_ms, 0, pump_duration_ms, 0, 128));
    screen.fillRect(128-pump_time_remain, 30, pump_time_remain, 1, SSD1306_WHITE);
  }
  //
  screen.display();
}

void _loop_pump() {
  unsigned long current_ms = millis();
  // Water level
  pump_water_level_mm = _mapf(input_adc_voltage[0], 0, 5, 0, pump_water_sensor_factor);
  // Pump amp
  float amp = _mapf(input_adc_voltage[1] + pump_sensor_offset_v, 0, 5, -pump_sensor_factor, pump_sensor_factor);
  if (!_timeout(pump_sensor_cycle_begin_ms, 500, true)) {
    if (amp < pump_sensor_peak_l_amp) {
      pump_sensor_peak_l_amp = amp;
    }
    if (amp > pump_sensor_peak_h_amp) {
      pump_sensor_peak_h_amp = amp;
    }
  } else {
    float peak_to_peak = pump_sensor_peak_h_amp - pump_sensor_peak_l_amp;
    pump_current_amp = peak_to_peak * c_peak_peak_to_rms;
    pump_sensor_peak_l_amp = 0;
    pump_sensor_peak_h_amp = 0;
  }
  // Pump action
  bool pump = digitalRead(output_pump_pin);
  if (pump) {
    unsigned long pump_duration_ms = config_pump_duration_min * c_min_to_ms;
    pump_time_remain_ms = constrain(pump_duration_ms - (current_ms - pump_begin_ms), 0, pump_duration_ms);
    if (input_stop || _timeout(pump_begin_ms, pump_duration_ms, false) || pump_water_level_mm > config_water_level_max_mm) {
      digitalWrite(output_pump_pin, LOW);
    }
  } else {
    if (input_run) {
      digitalWrite(output_pump_pin, HIGH);
      pump_begin_ms = current_ms;
    }
  }
}

void loop() {
  _loop_input();
  _loop_wifi_connect();
  _loop_screen_update();
  _loop_pump();
}