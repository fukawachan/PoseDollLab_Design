/* Pure transport/cohort logic. No peripheral I/O, allocation or calibration. */
#include "pd41_core.h"
#include <string.h>
uint16_t pd_get16(const uint8_t *p){return (uint16_t)((unsigned)p[0]|((unsigned)p[1]<<8));}
uint32_t pd_get32(const uint8_t *p){uint32_t v=0;for(unsigned i=0;i<4;i++)v|=(uint32_t)p[i]<<(8*i);return v;}
uint64_t pd_get64(const uint8_t *p){uint64_t v=0;for(unsigned i=0;i<8;i++)v|=(uint64_t)p[i]<<(8*i);return v;}
void pd_put16(uint8_t *p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
void pd_put32(uint8_t *p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8*i));}
void pd_put64(uint8_t *p,uint64_t v){for(unsigned i=0;i<8;i++)p[i]=(uint8_t)(v>>(8*i));}
bool pd_word_ok(uint16_t w){return w<PD_FIXED || (w>PD_FAULT && w<=PD_FAULT+31);}
void pd_init(pd_cohort_t *c,uint64_t epoch){memset(c,0,sizeof(*c));c->epoch=epoch;for(unsigned i=0;i<6;i++)c->node[i].blocked=true;}
bool pd_boot(pd_cohort_t *c,unsigned node,uint64_t boot){
    if(!node || node>6 || !boot)return false;
    pd_node_t *n=&c->node[node-1];
    if(n->boot==boot)return true;
    n->boot=boot;n->blocked=true;if(c->active)n->bad=true;return false;
}
bool pd_ack(pd_cohort_t *c,unsigned node,uint64_t epoch,uint64_t boot){
    if(!node || node>6 || !epoch || epoch!=c->epoch || !boot || c->node[node-1].boot!=boot)return false;
    c->node[node-1].blocked=false;return true;
}
bool pd_begin(pd_cohort_t *c,uint32_t seq,uint64_t now){
    if(!c->epoch || c->active || !seq || seq<=c->sequence)return false;
    c->sequence=seq;c->start_us=now;c->active=true;
    for(unsigned i=0;i<6;i++){pd_node_t *n=&c->node[i];n->groups=0;n->ended=false;n->bad=n->blocked;n->elapsed_us=0;memset(n->words,0xff,sizeof(n->words));}
    return true;
}
static pd_node_t *accept(pd_cohort_t *c,unsigned node,uint32_t seq,uint64_t now){
    if(!c->active || !node || node>6 || seq!=c->sequence || now<c->start_us || now-c->start_us>=PD_DEADLINE_US)return NULL;
    pd_node_t *n=&c->node[node-1];return n->blocked || n->bad ? NULL:n;
}
bool pd_pair(pd_cohort_t *c,unsigned node,uint32_t seq,unsigned group,uint16_t a,uint16_t b,uint64_t now){
    pd_node_t *n=accept(c,node,seq,now);if(!n)return false;
    const unsigned count=pd_port_count[node-1], ng=(count+1)/2;
    if(group>=ng || n->ended || (n->groups&(1u<<group)) || !pd_word_ok(a) || (group*2+1<count ? !pd_word_ok(b):b!=PD_FIXED)){n->bad=true;return false;}
    n->words[group*2]=a;if(group*2+1<count)n->words[group*2+1]=b;
    n->groups|=(uint8_t)(1u<<group);return true;
}
bool pd_end(pd_cohort_t *c,unsigned node,uint32_t seq,uint16_t delay,uint16_t span,uint64_t now){
    pd_node_t *n=accept(c,node,seq,now);if(!n)return false;
    const unsigned mask=(1u<<((pd_port_count[node-1]+1)/2))-1;
    if(n->ended || n->groups!=mask || !span || (unsigned)delay+span>PD_NODE_WINDOW_US || (unsigned)delay+span>now-c->start_us){n->bad=true;return false;}
    /* Conservative shared-clock envelope: sample must follow SYNC and precede END receipt.
       Local node clocks are never presented as precisely synchronized timestamps. */
    n->elapsed_us=(uint16_t)(now-c->start_us);n->ended=true;return true;
}
bool pd_finish(pd_cohort_t *c,uint64_t now,pd_sample_t *out){
    if(!c->active || now<c->start_us)return false;
    unsigned ends=0;for(unsigned i=0;i<6;i++)ends+=c->node[i].ended;
    if(now-c->start_us<PD_DEADLINE_US && ends<6)return false;
    memset(out,0,sizeof(*out));out->sequence=c->sequence;out->timestamp_us=c->start_us;
    for(unsigned i=0;i<44;i++)out->words[i]=i<3?PD_FIXED:PD_MISSING;
    for(unsigned i=0;i<6;i++){
        pd_node_t *n=&c->node[i];if(!n->ended || n->bad || n->blocked)continue;
        for(unsigned j=0;j<pd_port_count[i];j++)out->words[pd_axis_index[i][j]]=n->words[j];
        out->presence|=(uint16_t)(1u<<i);out->timing[i][1]=n->elapsed_us;
        if(n->elapsed_us>out->window_us)out->window_us=n->elapsed_us;
    }
    c->active=false;return true;
}
static uint32_t crc32(const uint8_t *p,unsigned n){uint32_t c=0xffffffff;while(n--){c^=*p++;for(unsigned j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320:0);}return c^0xffffffff;}
size_t pd_encode(const pd_sample_t *s,uint64_t device,uint64_t boot,uint64_t serial_seq,uint8_t *wire,size_t capacity){
    if(capacity<PD_WIRE_MAX || !device || !boot || !serial_seq || s->presence>63 || s->window_us>PD_DEADLINE_US)return 0;
    for(unsigned i=0;i<3;i++)if(s->words[i]!=PD_FIXED)return 0;
    for(unsigned n=0;n<6;n++){
        bool present=(s->presence&(1u<<n))!=0;
        if(present){if(!s->timing[n][1] || (unsigned)s->timing[n][0]+s->timing[n][1]>s->window_us)return 0;}
        else if(s->timing[n][0] || s->timing[n][1])return 0;
        for(unsigned p=0;p<pd_port_count[n];p++){uint16_t w=s->words[pd_axis_index[n][p]];if(present?!pd_word_ok(w):w!=PD_MISSING)return 0;}
    }
    uint8_t raw[PD_RAW_BYTES]={0};memcpy(raw,"PD41",4);raw[4]=1;raw[5]=1;pd_put16(raw+6,PD_BODY_BYTES);
    pd_put64(raw+8,device);pd_put64(raw+16,boot);pd_put64(raw+24,serial_seq);pd_put64(raw+32,s->timestamp_us);
    pd_put32(raw+40,s->window_us);pd_put16(raw+44,s->presence);pd_put16(raw+46,44);
    for(unsigned i=0;i<44;i++)pd_put16(raw+48+2*i,s->words[i]);
    for(unsigned n=0;n<6;n++)for(unsigned j=0;j<2;j++)pd_put16(raw+136+4*n+2*j,s->timing[n][j]);
    pd_put32(raw+160,crc32(raw,160));size_t ci=0,k=1;uint8_t code=1;
    for(unsigned i=0;i<PD_RAW_BYTES;i++){
        if(!raw[i]){wire[ci]=code;ci=k++;code=1;}else{wire[k++]=raw[i];if(++code==255){wire[ci]=code;ci=k++;code=1;}}
    }
    wire[ci]=code;wire[k++]=0;return k;
}
