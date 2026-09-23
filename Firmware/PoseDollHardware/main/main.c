/* H1 diagnostic firmware: one REAL AS5048A, no fabricated full-body samples.
 * AS5048 DS000298 v1-11: mode 1, delayed response, even parity, OCF/COF/COMP.
 * Pins: DevKitC-1 N8, SPI SCK12 MOSI11 MISO13 CS10. USB19/20 untouched.
 */
#include <stdint.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/spi_master.h"
#include "driver/gpio.h"
#include "driver/usb_serial_jtag.h"
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_random.h"
#include "esp_mac.h"
#include "esp_err.h"
static spi_device_handle_t sensor;
enum { IO_FAIL=1, PARITY_FAIL=2, SENSOR_ERROR=4, MAGNET_FAIL=8, NONZERO_OTP=16 };
static uint16_t parity(uint16_t v) { unsigned p=0;for(unsigned i=0;i<15;i++)p^=(v>>i)&1;return v|((uint16_t)p<<15); }
static int even(uint16_t v) { unsigned p=0;for(unsigned i=0;i<16;i++)p^=(v>>i)&1;return p==0; }
static esp_err_t word(uint16_t tx,uint16_t *rx) {
    uint8_t a[2]={(uint8_t)(tx>>8),(uint8_t)tx},b[2]={0};
    spi_transaction_t t={.length=16,.tx_buffer=a,.rx_buffer=b};
    gpio_set_level(GPIO_NUM_10,0);esp_rom_delay_us(1);
    esp_err_t e=spi_device_polling_transmit(sensor,&t);
    esp_rom_delay_us(1);gpio_set_level(GPIO_NUM_10,1);esp_rom_delay_us(1);
    *rx=((uint16_t)b[0]<<8)|b[1];return e;
}
static uint16_t read_reg(uint16_t addr,uint16_t *value) {
    uint16_t dummy=0,r=0,flags=0;
    esp_err_t a=word(parity(0x4000|addr),&dummy);
    esp_err_t b=word(0,&r);
    if(a!=ESP_OK || b!=ESP_OK)flags|=IO_FAIL;
    if(!even(r))flags|=PARITY_FAIL;
    if(r&0x4000)flags|=SENSOR_ERROR;
    *value=r&0x3fff;return flags;
}
static void put16(uint8_t *p,uint16_t v){p[0]=v;p[1]=v>>8;}
static void put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=v>>(8*i);}
static void put64(uint8_t *p,uint64_t v){for(unsigned i=0;i<8;i++)p[i]=v>>(8*i);}
static uint32_t crc32(const uint8_t *p,unsigned n) {
    uint32_t c=0xffffffff;
    while(n--){c^=*p++;for(unsigned j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320:0);}
    return c^0xffffffff;
}
static unsigned cobs(const uint8_t *p,unsigned n,uint8_t *out) {
    unsigned codeidx=0,k=1;uint8_t code=1;
    for(unsigned i=0;i<n;i++){
        if(p[i]==0){out[codeidx]=code;codeidx=k++;code=1;}
        else {out[k++]=p[i];if(++code==255){out[codeidx]=code;codeidx=k++;code=1;}}
    }
    out[codeidx]=code;out[k++]=0;return k;
}
void app_main(void) {
    gpio_config_t gp={.pin_bit_mask=1ULL<<10,.mode=GPIO_MODE_OUTPUT};ESP_ERROR_CHECK(gpio_config(&gp));gpio_set_level(GPIO_NUM_10,1);
    spi_bus_config_t bus={.mosi_io_num=11,.miso_io_num=13,.sclk_io_num=12,.quadwp_io_num=-1,.quadhd_io_num=-1,.max_transfer_sz=2};
    ESP_ERROR_CHECK(spi_bus_initialize(SPI2_HOST,&bus,SPI_DMA_DISABLED));
    spi_device_interface_config_t device={.clock_speed_hz=250000,.mode=1,.spics_io_num=-1,.queue_size=1};
    ESP_ERROR_CHECK(spi_bus_add_device(SPI2_HOST,&device,&sensor));
    usb_serial_jtag_driver_config_t usb={.tx_buffer_size=128,.rx_buffer_size=128};
    ESP_ERROR_CHECK(usb_serial_jtag_driver_install(&usb));
    uint8_t mac[6];ESP_ERROR_CHECK(esp_efuse_mac_get_default(mac));uint64_t id=0;
    for(unsigned i=0;i<6;i++)id=(id<<8)|mac[i];
    uint64_t boot=((uint64_t)esp_random()<<32)|esp_random(),seq=0;
    vTaskDelay(pdMS_TO_TICKS(20));TickType_t tick=xTaskGetTickCount();
    for(;;){
        uint64_t us=esp_timer_get_time();uint16_t angle=0,diag=0,mag=0,hi=0,lo=0,flags=0,dummy=0;
        flags|=read_reg(0x3ffd,&diag);
        flags|=read_reg(0x3ffe,&mag);
        flags|=read_reg(0x3fff,&angle);
        flags|=read_reg(0x0016,&hi);flags|=read_reg(0x0017,&lo);
        uint16_t zero=((hi&255)<<6)|(lo&63);
        if(!(diag&0x100) || (diag&0xe00))flags|=MAGNET_FAIL;
        if(zero)flags|=NONZERO_OTP; /* report, never silently compensate */
        uint32_t window=(uint32_t)(esp_timer_get_time()-us);
        if(flags&SENSOR_ERROR)(void)read_reg(1,&dummy); /* read-to-clear only; no write/OTP commands */
        uint8_t p[60]={0},wire[64];
        memcpy(p,"PDH1",4);p[4]=1;p[5]=1;put16(p+6,56);
        put64(p+8,id);put64(p+16,boot);put64(p+24,++seq);put64(p+32,us);
        put32(p+40,window);put16(p+44,17);put16(p+46,flags?0:angle);
        put16(p+48,diag);put16(p+50,mag);put16(p+52,zero);put16(p+54,flags);
        put32(p+56,crc32(p,56));unsigned size=cobs(p,60,wire);
        if(usb_serial_jtag_is_connected()) {
            int n=usb_serial_jtag_write_bytes(wire,size,0);
            if(n!=(int)size){uint8_t delimiter=0;(void)usb_serial_jtag_write_bytes(&delimiter,1,0);}
        }
        xTaskDelayUntil(&tick,pdMS_TO_TICKS(10));
    }
}
