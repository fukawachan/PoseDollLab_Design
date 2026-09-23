"""Beginner-facing H1 diagnostic UI; all transport is read-only and opt-in."""
import tkinter as tk
from tkinter import ttk,messagebox
from pathlib import Path
import datetime,threading,queue,os,argparse
from diagnose import capture,list_ports
class App:
    def __init__(self,root):
        self.root=root;self.events=queue.Queue();self.stop=threading.Event();self.running=False
        self.logdir=Path(__file__).resolve().parent/"recordings";self.devices={}
        root.title("PoseDoll H1 · 单轴诊断");root.geometry("850x620")
        f=ttk.Frame(root,padding=20);f.pack(fill="both",expand=True)
        ttk.Label(f,text="H1 单轴诊断",font=("Microsoft YaHei UI",20)).pack(anchor="w")
        ttk.Label(f,text="仅在接线和烧录核对后连接；本工具只读取串口，不控制 UE。").pack(anchor="w",pady=(5,15))
        row=ttk.Frame(f);row.pack(fill="x")
        self.ports=ttk.Combobox(row,state="readonly",width=70);self.ports.pack(side="left",fill="x",expand=True)
        self.refresh_button=ttk.Button(row,text="刷新端口",command=self.refresh);self.refresh_button.pack(side="left",padx=8)
        row=ttk.Frame(f);row.pack(fill="x",pady=12)
        self.start_button=ttk.Button(row,text="记录 10 秒",command=self.start);self.start_button.pack(side="left")
        self.stop_button=ttk.Button(row,text="停止并保存",command=self.stop.set,state="disabled");self.stop_button.pack(side="left",padx=8)
        ttk.Button(row,text="打开日志文件夹",command=self.open_logs).pack(side="left")
        self.state=tk.StringVar(value="未连接");self.angle=tk.StringVar(value="—")
        ttk.Label(f,textvariable=self.state,font=("Microsoft YaHei UI",13)).pack(anchor="w")
        ttk.Label(f,textvariable=self.angle,font=("Consolas",34)).pack(anchor="w",pady=8)
        ttk.Label(f,text="有效读数仅代表该帧诊断正常；不代表绝对精度或整机验收通过。").pack(anchor="w")
        self.text=tk.Text(f,height=17,font=("Consolas",10),wrap="word");self.text.pack(fill="both",expand=True,pady=10)
        self.refresh();root.after(100,self.poll);root.protocol("WM_DELETE_WINDOW",self.close)
    def refresh(self):
        if self.running:return
        try:
            self.devices={v["port"]+" · "+v["description"]:v for v in list_ports()}
            self.ports["values"]=list(self.devices);self.ports.set("")
            self.state.set("请根据烧录记录选择已核对的开发板端口" if self.devices else "未发现串口；尚未接入硬件时属正常情况")
        except Exception as exc:messagebox.showerror("端口读取失败",str(exc))
    def open_logs(self):
        self.logdir.mkdir(exist_ok=True);os.startfile(self.logdir)
    def start(self):
        if self.running:return
        item=self.devices.get(self.ports.get())
        if not item:messagebox.showinfo("选择端口","请先选择已核对的开发板端口。");return
        self.running=True;self.stop.clear();self.start_button["state"]="disabled";self.refresh_button["state"]="disabled";self.ports["state"]="disabled";self.stop_button["state"]="normal"
        self.text.delete("1.0","end");self.state.set("正在记录；测静止噪声时保持关节固定")
        dest=self.logdir/("h1_"+datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
        def worker():
            try:
                r=capture(item["port"],10,dest,self.stop,lambda v,n,e:self.events.put(("sample",(v,n,e))))
                self.events.put(("done",(r,str(dest))))
            except Exception as exc:self.events.put(("error",str(exc)))
        threading.Thread(target=worker,daemon=True).start()
    def poll(self):
        import json
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=="sample":
                    v,n,e=data;angle=v["raw_degrees"]
                    self.angle.set(f"{angle:.3f}°" if angle is not None else "无效")
                    self.state.set(f"帧 {n} · {v['status']} · flags={v['flags']} · 格式/会话错误 {e}")
                else:
                    self.running=False;self.start_button["state"]="normal";self.refresh_button["state"]="normal";self.ports["state"]="readonly";self.stop_button["state"]="disabled"
                    if kind=="error":self.state.set("记录失败");self.text.insert("end",data)
                    else:
                        report,dest=data;self.state.set("已保存记录，请按验收说明解释结果")
                        self.text.insert("end",dest+"\n\n"+json.dumps(report,ensure_ascii=False,indent=2))
        except queue.Empty:pass
        self.root.after(100,self.poll)
    def close(self):
        if self.running:self.stop.set();self.state.set("正在停止并保存；保存后再关闭窗口")
        else:self.root.destroy()
if __name__=="__main__":
    args=argparse.ArgumentParser();args.add_argument("--smoke-test",action="store_true");a=args.parse_args()
    root=tk.Tk()
    if a.smoke_test:root.withdraw()
    app=App(root)
    if a.smoke_test:root.update_idletasks();root.destroy();print("GUI construction OK; no serial connection opened")
    else:root.mainloop()
