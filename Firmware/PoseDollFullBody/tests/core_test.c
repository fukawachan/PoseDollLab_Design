#include "pd41_core.h"
#include <stdio.h>
#include <stdlib.h>
#define CHECK(x) do{if(!(x)){fprintf(stderr,"FAIL line %d: %s\n",__LINE__,#x);return 1;}}while(0)
static void ready(pd_cohort_t *c){pd_init(c,123);for(unsigned n=1;n<=6;n++){(void)pd_boot(c,n,100+n);(void)pd_ack(c,n,123,100+n);}(void)pd_begin(c,1,1000);}
static bool fill(pd_cohort_t *c,unsigned node,uint16_t value){
    unsigned count=pd_port_count[node-1];
    for(unsigned g=0;g<(count+1)/2;g++)if(!pd_pair(c,node,1,g,value,g*2+1<count?value:PD_FIXED,2000))return false;
    return pd_end(c,node,1,100,900,3000);
}
int main(int argc,char **argv){
    pd_cohort_t c;pd_sample_t s;ready(&c);
    for(unsigned n=1;n<=6;n++)CHECK(fill(&c,n,555));CHECK(pd_finish(&c,4000,&s));CHECK(s.presence==63 && s.window_us==2000);
    for(unsigned i=0;i<44;i++)CHECK(s.words[i]==(i<3?PD_FIXED:555));
    uint8_t wire[PD_WIRE_MAX];size_t len=pd_encode(&s,0x123456789abc,789,1,wire,sizeof(wire));CHECK(len>160 && len<=sizeof(wire));
    if(argc>1){FILE *f=NULL;if(fopen_s(&f,argv[1],"wb") || !f)return 1;CHECK(fwrite(wire,1,len,f)==len);CHECK(fclose(f)==0);}
    CHECK(pd_begin(&c,2,20000));CHECK(!pd_pair(&c,3,1,0,12,12,21000));CHECK(pd_pair(&c,3,2,0,12,12,21000));
    CHECK(!pd_end(&c,3,2,0,1000,22000));CHECK(pd_finish(&c,34000,&s));CHECK(s.presence==0);CHECK(s.words[12]==PD_MISSING);
    ready(&c);CHECK(pd_pair(&c,3,1,0,555,555,2000));CHECK(!pd_pair(&c,3,1,0,555,555,2001));CHECK(!fill(&c,3,555));CHECK(pd_finish(&c,15000,&s));CHECK(!s.presence);
    ready(&c);CHECK(fill(&c,2,555));CHECK(!pd_boot(&c,2,999));CHECK(!pd_ack(&c,2,123,102));CHECK(pd_finish(&c,15000,&s));CHECK(!s.presence);
    ready(&c);CHECK(fill(&c,2,PD_FAULT+8));CHECK(pd_finish(&c,15000,&s));CHECK(s.presence==2 && s.words[6]==PD_FAULT+8);
    ready(&c);CHECK(!pd_pair(&c,1,1,0,PD_FIXED,555,2000));CHECK(pd_finish(&c,15000,&s));CHECK(!s.presence);
    ready(&c);CHECK(pd_pair(&c,1,1,0,11,11,2000));CHECK(pd_pair(&c,1,1,1,11,PD_FIXED,2000));CHECK(!pd_end(&c,1,1,0,7000,3000));
    CHECK(pd_finish(&c,15000,&s));CHECK(!s.presence);CHECK(!pd_begin(&c,1,20000));CHECK(!pd_finish(&c,20000,&s));
    ready(&c);CHECK(!pd_pair(&c,1,1,0,11,11,15000));CHECK(pd_finish(&c,15000,&s));CHECK(!s.presence);
    s.words[0]=0;CHECK(!pd_encode(&s,1,2,3,wire,sizeof(wire)));
    puts("PASS: 9 C cohort/serialization scenarios; golden PD41 frame emitted");return 0;
}
