"""Full-body diagnostic UI. Opens no port until the user explicitly starts capture."""
import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from pathlib import Path
import argparse,datetime,json,queue,threading,os
from full_diagnose import CFG,capture,analyze,list_ports

class App:
 def __init__(self,root):
  self.root=root;self.events=queue.Queue();self.stop=threading.Event();self.running=False;self.devices={};self.logdir=Path(__file__).resolve().parent/'recordings'
  root.title('PoseDoll · 全身 41 轴诊断');root.geometry('1040x830');frame=ttk.Frame(root,padding=18);frame.pack(fill='both',expand=True)
  ttk.Label(frame,text='全身关节诊断',font=('Microsoft YaHei UI',20)).pack(anchor='w')
  ttk.Label(frame,text='显示原始传感器状态；骨盆三轴固定为参考。整体位置和转动在 UE 设置。').pack(anchor='w',pady=(5,12))
  row=ttk.Frame(frame);row.pack(fill='x');self.ports=ttk.Combobox(row,state='readonly',width=52);self.ports.pack(side='left',fill='x',expand=True)
  self.refresh_button=ttk.Button(row,text='刷新端口',command=self.refresh);self.refresh_button.pack(side='left',padx=5)
  self.start_button=ttk.Button(row,text='记录 10 秒',command=self.start);self.start_button.pack(side='left',padx=5)
  self.stop_button=ttk.Button(row,text='停止并保存',command=self.stop.set,state='disabled');self.stop_button.pack(side='left')
  row=ttk.Frame(frame);row.pack(fill='x',pady=8);self.offline=ttk.Button(row,text='打开已有 .bin 记录',command=self.open_record);self.offline.pack(side='left');ttk.Button(row,text='打开日志文件夹',command=self.open_logs).pack(side='left',padx=6)
  self.state=tk.StringVar(value='未连接；可先打开离线记录');self.nodes=tk.StringVar(value='N1–N6：未收到数据')
  ttk.Label(frame,textvariable=self.state,font=('Microsoft YaHei UI',12)).pack(anchor='w');ttk.Label(frame,textvariable=self.nodes).pack(anchor='w',pady=(2,8))
  holder=ttk.Frame(frame);holder.pack(fill='both',expand=True);self.table=ttk.Treeview(holder,columns=('port','axis','status','raw','degrees','fault'),show='headings',height=24)
  for key,text,width in [('port','接口',85),('axis','关节通道',230),('status','状态',120),('raw','原始计数',105),('degrees','传感器原始角度',145),('fault','故障位',75)]:self.table.heading(key,text=text);self.table.column(key,width=width,anchor='w')
  self.table.pack(side='left',fill='both',expand=True);scroll=ttk.Scrollbar(holder,orient='vertical',command=self.table.yview);scroll.pack(side='right',fill='y');self.table.configure(yscrollcommand=scroll.set)
  self.table.tag_configure('invalid',foreground='#b42318');self.table.tag_configure('missing',foreground='#9a6700');self.table.tag_configure('fixed',foreground='#637083')
  ports={p['axis_id']:f"N{n['id']} / P{p['port']}" for n in CFG['nodes'] for p in n['ports']};self.port_labels=ports
  for aid in CFG['protocol_order']:self.table.insert('', 'end',iid=aid,values=(ports.get(aid,'固定参考'),aid,'未读取','—','—','—'))
  ttk.Label(frame,text='原始角度不是人体关节角度。必须完成实体零点、方向和磁场校准后才能用于姿势。').pack(anchor='w',pady=(8,3))
  self.note=tk.Text(frame,height=6,wrap='word',font=('Microsoft YaHei UI',10));self.note.pack(fill='x');root.after(100,self.poll);root.protocol('WM_DELETE_WINDOW',self.close)
 def refresh(self):
  if self.running:return
  try:self.devices={q['port']+' · '+q['description']:q for q in list_ports()};self.ports['values']=list(self.devices);self.ports.set('');self.state.set('选择已核对接线和固件的网关端口' if self.devices else '未发现串口；尚未接入硬件时属正常情况')
  except Exception as exc:messagebox.showerror('端口读取失败',str(exc))
 def show(self,row,count,errors,offline=False):
  labels={'valid':'读数有效','invalid':'传感器故障','missing':'本帧缺失','fixed':'固定 0°'}
  for a in row['axes']:
   raw=a['count'];deg='—' if raw is None else f'{raw*360/16384:.3f}°';self.table.item(a['axis_id'],values=(self.port_labels.get(a['axis_id'],'固定参考'),a['axis_id'],labels[a['status']], '—' if raw is None else raw,deg,a['flags']),tags=(a['status'],))
  valid=sum(a['status']=='valid' for a in row['axes'][3:]);self.state.set(f"{'离线记录' if offline else '正在记录'} · {valid}/41 路有效 · 帧 {count} · 格式/会话错误 {errors} · 未校准")
  self.nodes.set(' / '.join(f"N{n} {'已到齐' if row['node_presence_mask']&(1<<(n-1)) else '缺失'}" for n in range(1,7))+f" · 传输包络 {row['sample_window_us']/1000:.2f} ms")
 def start(self):
  if self.running:return
  chosen=self.devices.get(self.ports.get())
  if not chosen:messagebox.showinfo('选择端口','先刷新并选择已核对的网关端口。');return
  self.running=True;self.stop.clear();self.toggle();dest=self.logdir/('pd41_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f'));self.state.set('正在等待全身数据')
  def work():
   try:report=capture(chosen['port'],10,dest,self.stop,lambda v,n,e:self.events.put(('sample',(v,n,e))));self.events.put(('done',(report,str(dest))))
   except Exception as exc:self.events.put(('error',str(exc)))
  threading.Thread(target=work,daemon=True).start()
 def toggle(self):
  for b in (self.refresh_button,self.start_button,self.offline):b['state']='disabled' if self.running else 'normal'
  self.ports['state']='disabled' if self.running else 'readonly';self.stop_button['state']='normal' if self.running else 'disabled'
 def finish(self,report,path):
  self.note.delete('1.0','end');self.note.insert('end',path+'\n'+f"记录 {report['frames']} 帧；41 路全部有效 {report['complete_valid_frames']} 帧；丢失序号 {report['sequence_gaps']}；格式/会话错误 {report['framing_or_session_errors']}。\n"+'各轴统计保存在 .summary.json；固定人偶时才可将波动解释为噪声。尚未完成硬件校准或实物验收。')
 def open_record(self):
  path=filedialog.askopenfilename(filetypes=[('PD41 原始记录','*.bin')])
  if not path:return
  try:
   _,rows,report=analyze(path)
   if rows:self.show(rows[-1],len(rows),report['framing_or_session_errors'],True)
   else:self.state.set('文件中没有可解码的 PD41 全身帧')
   self.finish(report,path)
  except Exception as exc:messagebox.showerror('记录读取失败',str(exc))
 def open_logs(self):self.logdir.mkdir(exist_ok=True);os.startfile(self.logdir)
 def poll(self):
  try:
   while True:
    kind,data=self.events.get_nowait()
    if kind=='sample':self.show(*data)
    else:
     self.running=False;self.toggle()
     if kind=='done':self.finish(*data);self.state.set('记录已保存；未校准')
     else:self.state.set('记录失败');self.note.insert('end',data)
  except queue.Empty:pass
  self.root.after(100,self.poll)
 def close(self):
  if self.running:self.stop.set();self.state.set('正在停止并保存；保存后可关闭')
  else:self.root.destroy()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--smoke-test',action='store_true');a=parser.parse_args();root=tk.Tk()
 if a.smoke_test:root.withdraw()
 app=App(root)
 if a.smoke_test:root.update_idletasks();root.destroy();print('PD41 GUI constructed; no port enumerated or opened')
 else:root.mainloop()
