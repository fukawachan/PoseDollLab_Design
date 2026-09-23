#pragma once
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "pd41_config.h"
enum { PD_FIXED=0x4000, PD_MISSING=0xffff, PD_FAULT=0x8000, PD_BODY_BYTES=160, PD_RAW_BYTES=164, PD_WIRE_MAX=167 };
typedef struct {
    uint64_t boot;
    uint16_t words[PD_MAX_PORTS];
    uint16_t elapsed_us;
    uint8_t groups;
    bool blocked, bad, ended;
} pd_node_t;
typedef struct {
    uint64_t epoch, start_us;
    uint32_t sequence;
    bool active;
    pd_node_t node[PD_NODE_COUNT];
} pd_cohort_t;
typedef struct {
    uint16_t words[PD_AXIS_COUNT], timing[PD_NODE_COUNT][2], presence;
    uint32_t sequence, window_us;
    uint64_t timestamp_us;
} pd_sample_t;
void pd_init(pd_cohort_t *c, uint64_t epoch);
bool pd_boot(pd_cohort_t *c, unsigned node, uint64_t boot);
bool pd_ack(pd_cohort_t *c, unsigned node, uint64_t epoch, uint64_t boot);
bool pd_begin(pd_cohort_t *c, uint32_t seq, uint64_t now_us);
bool pd_pair(pd_cohort_t *c, unsigned node, uint32_t seq, unsigned group, uint16_t a, uint16_t b, uint64_t now_us);
bool pd_end(pd_cohort_t *c, unsigned node, uint32_t seq, uint16_t delay_us, uint16_t span_us, uint64_t now_us);
bool pd_finish(pd_cohort_t *c, uint64_t now_us, pd_sample_t *out);
bool pd_word_ok(uint16_t w);
size_t pd_encode(const pd_sample_t *s, uint64_t device, uint64_t boot, uint64_t serial_seq, uint8_t *wire, size_t capacity);
uint16_t pd_get16(const uint8_t *p);
uint32_t pd_get32(const uint8_t *p);
uint64_t pd_get64(const uint8_t *p);
void pd_put16(uint8_t *p, uint16_t v);
void pd_put32(uint8_t *p, uint32_t v);
void pd_put64(uint8_t *p, uint64_t v);
