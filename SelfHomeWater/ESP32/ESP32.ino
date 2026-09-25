#include <Wire.h>
#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_ADS1X15.h>
#include <Preferences.h>
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>

/////////
//CONST//
/////////
const long c_min_to_ms = 60000;
const float c_peak_peak_to_rms = 0.35355;

//////////
//CONFIG//
//////////
Preferences config;
String config_wifi_ssid = "";         const char* config_wifi_ssid_key = "wifi_ssid";
String config_wifi_pass = "";         const char* config_wifi_pass_key = "wifi_pass";
int config_water_level_max_mm = 900;  const char* config_water_level_max_mm_key = "w_l_max_mm";
int config_pump_begin_24hour = 9;     const char* config_pump_begin_24hour_key = "p_begin_24";
int config_pump_end_24hour = 17;      const char* config_pump_end_24hour_key = "p_end_24";
int config_pump_interval_min = 120;   const char* config_pump_interval_min_key = "p_itv_min";
int config_pump_duration_min = 10;    const char* config_pump_duration_min_key = "p_drt_min";

void _config_load() {
  config.begin("config", true);
  config_wifi_ssid = config.getString(config_wifi_ssid_key, "SUONG");
  config_wifi_pass = config.getString(config_wifi_pass_key, "11111111");
  config_water_level_max_mm = config.getInt(config_water_level_max_mm_key, 900);
  config_pump_begin_24hour = config.getInt(config_pump_begin_24hour_key, 9);
  config_pump_end_24hour = config.getInt(config_pump_end_24hour_key, 17);
  config_pump_interval_min = config.getInt(config_pump_interval_min_key, 120);
  config_pump_duration_min = config.getInt(config_pump_duration_min_key, 10);
  config.end();
}

void _config_save() {
  config_water_level_max_mm = constrain(config_water_level_max_mm, 600, 900);
  config_pump_begin_24hour = constrain(config_pump_begin_24hour, 8, 11);
  config_pump_end_24hour = constrain(config_pump_end_24hour, 13, 18);
  config_pump_interval_min = constrain(config_pump_interval_min, 60, 180);
  config_pump_duration_min = constrain(config_pump_duration_min, 10, 20);
  config.begin("config", false);
  config.putString(config_wifi_ssid_key, config_wifi_ssid);
  config.putString(config_wifi_pass_key, config_wifi_pass);
  config.putInt(config_water_level_max_mm_key, config_water_level_max_mm);
  config.putInt(config_pump_begin_24hour_key, config_pump_begin_24hour);
  config.putInt(config_pump_end_24hour_key, config_pump_end_24hour);
  config.putInt(config_pump_interval_min_key, config_pump_interval_min);
  config.putInt(config_pump_duration_min_key, config_pump_duration_min);
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
const int screen_update_interval_ms = 20;
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
String server_receive = "";

const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML><html>
<head>
  <title>ESP Web Server</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="data:,">
  <style>
    html {font-family: Arial; display: inline-block; text-align: center;}
    h2 {font-size: 1.5rem;}
    p {font-size: 1.5rem;}
    input {font-size: 1.5rem;}
    button {font-size: 1.5rem;}
    body {max-width: 600px; margin:0px auto; padding-bottom: 25px;}
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
  <h2>Configuration <button onclick="dataSet()">Save</button></h2>
  <p>
    <span>Water Level Max</span>
    <input type="number" id="cf_water_level_max" style="width: 4ch" onfocus="cf_focus(this)">
    <span><sup>mm</sup>
  </p>
  <p>
    <span>Pump from</span>
    <input type="number" id="cf_pump_begin" style="width: 3ch" onfocus="cf_focus(this)">
    <span><sup>h</sup> to</span>
    <input type="number" id="cf_pump_end" style="width: 3ch" onfocus="cf_focus(this)">
    <span><sup>h</sup> each</span>
    <input type="number" id="cf_pump_interval" style="width: 4ch" onfocus="cf_focus(this)">
    <span><sup>min</sup> for</span>
    <input type="number" id="cf_pump_duration" style="width: 3ch" onfocus="cf_focus(this)">
    <span><sup>min</sup>
  </p>
<script>
cf = {
  'cf_water_level_max': false,
  'cf_pump_begin': false,
  'cf_pump_end': false,
  'cf_pump_interval': false,
  'cf_pump_duration': false,
}
function cf_focus(field) {
  cf[field.id] = true;
}
function cf_reset() {
  for (let k in cf) {
    cf[k] = false;
  }
}
function dataGet() {
  fetch('/api/data')
    .then(response => response.json())
    .then(data => {
      document.getElementById('water_level').innerText = data.water_level;
      document.getElementById('pump_current').innerText = data.pump_current.toFixed(3);
      document.getElementById('pump_time_remain').innerText = (data.pump_time_remain*1e-3).toFixed(0);
      for (let k in cf) {
        if (!cf[k]) {
          document.getElementById(k).value = data[k];
        }
      }
    });
}
setInterval(dataGet, 500);
function dataSet() {
  data = {
    cf_water_level_max: parseInt(document.getElementById('cf_water_level_max').value),
    cf_pump_begin: parseInt(document.getElementById('cf_pump_begin').value),
    cf_pump_end: parseInt(document.getElementById('cf_pump_end').value),
    cf_pump_interval: parseInt(document.getElementById('cf_pump_interval').value),
    cf_pump_duration: parseInt(document.getElementById('cf_pump_duration').value)
  }
  fetch('/api/data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
    .then(response => response.json())
    .then(data => cf_reset())
    .catch(error => console.error('Error:', error));
}
</script>
</body>
</html>
)rawliteral";

String _server_data_json_get() {
  JsonDocument doc;
  doc["water_level"] = round(pump_water_level_mm);
  doc["pump_current"] = pump_current_amp;
  doc["pump_time_remain"] = pump_time_remain_ms;
  doc["cf_water_level_max"] = config_water_level_max_mm;
  doc["cf_pump_begin"] = config_pump_begin_24hour;
  doc["cf_pump_end"] = config_pump_end_24hour;
  doc["cf_pump_interval"] = config_pump_interval_min;
  doc["cf_pump_duration"] = config_pump_duration_min;
  String result;
  serializeJson(doc, result);
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
  server.on("/api/data", HTTP_POST,
    [](AsyncWebServerRequest *request) {
      request->send(200, "text/plain", "POST request received");
    },
    NULL,
    [](AsyncWebServerRequest *request, uint8_t *data, size_t len, size_t index, size_t total) {
      if (index == 0) {
        server_receive = "";
      }
      for (size_t i = 0; i < len; i++) {
        server_receive += (char)data[i];
      }
      if (index + len == total) {
        JsonDocument doc;
        DeserializationError error = deserializeJson(doc, server_receive);
        if (!error) {
          const char* status = doc["status"];
          //
          if (doc["cf_water_level_max"].is<int>()) { config_water_level_max_mm = doc["cf_water_level_max"]; }
          if (doc["cf_pump_begin"].is<int>()) { config_pump_begin_24hour = doc["cf_pump_begin"]; }
          if (doc["cf_pump_end"].is<int>()) { config_pump_end_24hour = doc["cf_pump_end"]; }
          if (doc["cf_pump_interval"].is<int>()) { config_pump_interval_min = doc["cf_pump_interval"]; }
          if (doc["cf_pump_duration"].is<int>()) { config_pump_duration_min = doc["cf_pump_duration"]; }
          _config_save();
          //
          request->send(200, "application/json", "{\"success\":true}");
        } else {
          request->send(400, "text/plain", "Invalid JSON");
        }
      }
    }
  );
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
  screen.ssd1306_command(SSD1306_SETCONTRAST);
  screen.ssd1306_command(128);
  screen.display();
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
  int width = pump ? 10 : 15;
  int water_level = round(_mapf(pump_water_level_mm, 0, config_water_level_max_mm, 0, 128));
  screen.fillRect(128-water_level, 16, water_level, width, SSD1306_WHITE);
  if (pump) {
    int pump_current = round(_mapf(pump_current_amp, 0, pump_sensor_factor*c_peak_peak_to_rms, 0, 128));
    screen.fillRect(128-pump_current, 27, pump_current, 2, SSD1306_WHITE);
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