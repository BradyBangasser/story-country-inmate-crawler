#pragma once

#include <inttypes.h>
#include "freertos/FreeRTOS.h"
#include <driver/gpio.h>
#include <driver/rtc_io.h>
#include <stdbool.h>
#include "freertos/task.h"
#include "esp_log.h"
#include <string.h>
#include <time.h>

#include "test.h"

typedef uint8_t pin;

struct lcd_config {
    bool contrast;
    pin contrast_pin; // 255 if contrast pin control is disabled
    pin rs;
    pin e;
    pin data_pins[4]; // 7, 6, 5, 4
};

static struct lcd_config config = {};

static inline int _pin_write(pin p, bool value) {
    esp_err_t err = gpio_set_level(p, value);
    return err;
}

static inline void _pulse_enable() {
    _pin_write(config.e, 0);
    vTaskDelay(1 / portTICK_PERIOD_MS); // Make this microseconds
    _pin_write(config.e, 1);
    vTaskDelay(1 / portTICK_PERIOD_MS); // Make this microseconds
    _pin_write(config.e, 0);
    vTaskDelay(1 / portTICK_PERIOD_MS); // Make this microseconds
}

static inline void _reset_pins() {
    _pin_write(config.e, 0);
    _pin_write(config.rs, 0);
    _pin_write(config.data_pins[0], 0);
    _pin_write(config.data_pins[1], 0);
    _pin_write(config.data_pins[2], 0);
    _pin_write(config.data_pins[3], 0);
}

static inline int _write_pin_analog(pin p, uint8_t value) {
    return -1;
}

static inline bool _read_pin(pin p) {
    return false;
}

static inline bool _check_busy() {
    return gpio_get_level(config.data_pins[0]);
}

static inline void _check_busy_hang() {
    while (_check_busy()) {
        ESP_LOGI("Busy", "%d", _check_busy());
        vTaskDelay(1 / portTICK_PERIOD_MS);
    }
}

static inline int _pin_nibble_write(pin rs, pin d7, pin d6, pin d5, pin d4) {
    uint8_t data = 0;
    data |= d7 << 3;
    data |= d6 << 2;
    data |= d5 << 1;
    data |= d4; 
    _pin_write(config.rs, rs);
    _pin_write(config.data_pins[0], d7);
    _pin_write(config.data_pins[1], d6);
    _pin_write(config.data_pins[2], d5);
    _pin_write(config.data_pins[3], d4);

    _pulse_enable();
    _reset_pins();
    return -1;
}

enum Commands {
    LCD_DISPLAY = 0x0,
    LCD_CLEAR = 0x01,
    LCD_RETURN_HOME = 0x02,
    LCD_SET_ENTRY_MODE = 0x04,
    LCD_DISPLAY_CTRL = 0x08,
    LCD_CURSOR_CTRL = 0x10,
    LCD_FUNCTION_SET = 0x20,
    LCD_SET_CGRAM_ADDR = 0x40,
    LCD_SET_DDRAM_ADDR = 0x80,
};

static inline int _command(bool rs, uint8_t command) {
    _pin_write(config.rs, rs);
    _pin_write(config.data_pins[0], command & 0x80);
    _pin_write(config.data_pins[1], command & 0x40);
    _pin_write(config.data_pins[2], command & 0x20);
    _pin_write(config.data_pins[3], command & 0x10);
    _pulse_enable();

    // Probably redundant 
    _pin_write(config.rs, rs);
    _pin_write(config.data_pins[0], command & 0x08);
    _pin_write(config.data_pins[1], command & 0x04);
    _pin_write(config.data_pins[2], command & 0x02);
    _pin_write(config.data_pins[3], command & 0x01);

    _pulse_enable();
    _reset_pins();

    _check_busy_hang();
    vTaskDelay(10 / portTICK_PERIOD_MS);
    return -1;
}

static inline int _write_character(char c) {
    return _command(true, c);
}

static inline int _write_string(const char *str) {
    int i;
    for (i = 0; i < strlen(str); i++) {
        _write_character(str[i]);
    }

    return 0;
}

#define _TEST_PIN_(pin, dur_ms) { _pin_write(pin, 1); vTaskDelay(dur_ms / portTICK_PERIOD_MS); _pin_write(pin, 0); }

static void _test_pins() {
    uint8_t i = 0, j = 0;
    uint8_t pin = i;
    while (i < 8) {
        pin = (i > 3) ? 7 - i : i;
        ESP_LOGI("Testing Pin", "D%d", pin + 4);
        _TEST_PIN_(config.data_pins[pin], 500);
        i++;
    }

    i = 0;
    while (i < 2) {
        pin = i ? config.rs : config.e;
        ESP_LOGI("Testing Pin", "%s (pin %d)", (pin == config.e) ? "enable" : "rw", pin);
        j = 0;
        while (j < 20) {
            _TEST_PIN_(pin, 100);
            vTaskDelay(50 / portTICK_PERIOD_MS);
            j++;
        }
        i++; 
    }
}
// implement GPIO_IS_VALID_GPIO
static inline struct lcd_config *lcd_init_4(pin rs, pin e, pin d7, pin d6, pin d5, pin d4) {
    gpio_config_t gc = {};
    esp_err_t err = ESP_OK;
    time_t seconds;
    int i;
    config.contrast = false;
    config.contrast_pin = 255;

    // init pins
    gc.intr_type = GPIO_INTR_DISABLE;
    gc.mode = GPIO_MODE_OUTPUT;
    gc.pull_down_en = false;
    gc.pull_up_en = false;
    gc.pin_bit_mask = 0;
    gc.pin_bit_mask |= (1ULL << rs);
    gc.pin_bit_mask |= (1ULL << e);

    err = gpio_config(&gc);

    if (err != ESP_OK) {
        return NULL;
    }

    gc.pin_bit_mask = 0;
    gc.pin_bit_mask |= (1ULL << d4);
    gc.pin_bit_mask |= (1ULL << d5);
    gc.pin_bit_mask |= (1ULL << d6);
    gc.pin_bit_mask |= (1ULL << d7);
    gc.mode = GPIO_MODE_INPUT_OUTPUT;

    err = gpio_config(&gc);

    if (err != ESP_OK) {
        return NULL;
    }

    config.e = e;
    config.rs = rs;
    config.data_pins[0] = d7;
    config.data_pins[1] = d6;
    config.data_pins[2] = d5;
    config.data_pins[3] = d4;

    vTaskDelay(250 / portTICK_PERIOD_MS);

    // _test_pins()

    _reset_pins();

    for (i = 0; i < 3; i++) {
        _pin_nibble_write(0, 0, 0, 1, 0);
        vTaskDelay(5 / portTICK_PERIOD_MS);
    }

    _pin_nibble_write(0, 0, 0, 1, 0);
    _reset_pins();
    _command(false, LCD_FUNCTION_SET | 0x08);
    _command(false, LCD_DISPLAY_CTRL | 0x04);
    _command(false, LCD_SET_ENTRY_MODE | 0x02);
    _command(false, LCD_RETURN_HOME);
    _command(false, LCD_CLEAR);

    i = 0;
    while (true) {
        _command(false, LCD_CLEAR);
        _write_string(people[i].name);
        _command(false, LCD_SET_DDRAM_ADDR | 0x40);
        vTaskDelay(10 / portTICK_PERIOD_MS);
        _write_string(people[i].major);
        _command(false, LCD_SET_DDRAM_ADDR);
        vTaskDelay(10 / portTICK_PERIOD_MS);
        vTaskDelay(2000 / portTICK_PERIOD_MS);
        i++;
        i = i % (sizeof(people) / sizeof(*people));
    }

    return (void *) 1;
}

static inline void lcd_init_4_contrast() {

}