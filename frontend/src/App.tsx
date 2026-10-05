import { useEffect, useMemo, useState } from "react";
import ReactECharts from "echarts-for-react";
import { api } from "./api";
import type { EquipmentPoint, DailyPoint, AnomalyRow, ScatterPoint } from "./types";

type Tab = "cycle" | "period";

const anomalyLabel: Record<string,string> = {
  normal: "正常",
  chatter: "ビビり/周期振動",
  chip_entrapment: "砥粒・切りくず巻込み",
  backlash: "ガタ/バックラッシ",
};

export default function App() {
  const [tab,setTab] = useState<Tab>("cycle");

  const [date,setDate] = useState("2026-10-05");
  const [serials,setSerials] = useState<string[]>([]);
  const [serial,setSerial] = useState("");
  const [axis,setAxis] = useState(3);

  const [equipment,setEquipment] = useState<EquipmentPoint[]>([]);
  const [features,setFeatures] = useState<any>({});
  const [measurement,setMeasurement] = useState<any>({profile:[],metrics:{}});
  const [changes,setChanges] = useState<any[]>([]);
  const [trace,setTrace] = useState<any>({});
  const [loading,setLoading] = useState(false);

  const [start,setStart] = useState("2026-07-05");
  const [end,setEnd] = useState("2026-10-05");
  const [machine,setMachine] = useState("ALL");
  const [daily,setDaily] = useState<DailyPoint[]>([]);
  const [anomalies,setAnomalies] = useState<AnomalyRow[]>([]);
  const [scatter,setScatter] = useState<ScatterPoint[]>([]);
  const [summary,setSummary] = useState<any>({cycles:0,ng_count:0,ng_rate:0});

  useEffect(()=>{
    api.serials(date).then(r=>{
      setSerials(r.serials);
      if (!r.serials.includes(serial)) setSerial(r.serials[0] ?? "");
    });
  },[date]);

  useEffect(()=>{
    if (!serial || tab!=="cycle") return;
    setLoading(true);
    Promise.all([
      api.equipment(serial,axis),
      api.measurement(serial),
      api.changes(serial),
      api.trace(serial),
    ]).then(([e,m,c,t])=>{
      setEquipment(e.data);
      setFeatures(e.features);
      setMeasurement(m);
      setChanges(c.data);
      setTrace(t);
    }).finally(()=>setLoading(false));
  },[serial,axis,tab]);

  useEffect(()=>{
    if (tab!=="period") return;
    setLoading(true);
    api.period(start,end,machine,axis).then(r=>{
      setSummary(r.summary);
      setDaily(r.daily);
      setAnomalies(r.anomalies);
      setScatter(r.scatter);
    }).finally(()=>setLoading(false));
  },[tab,start,end,machine,axis]);

  const jumpToCycle = (row: AnomalyRow) => {
    const d = row.production_time.slice(0,10);
    setDate(d);
    setSerial(row.serial_no);
    setTab("cycle");
  };

  const waveOption = useMemo(()=>({
    tooltip:{trigger:"axis"},
    legend:{data:["Position","Torque","Feed"]},
    grid:{left:55,right:55,top:50,bottom:70},
    dataZoom:[{type:"inside"},{type:"slider"}],
    xAxis:{type:"category",name:"Time [s]",data:equipment.map(p=>(p.time_ms/1000).toFixed(3)),boundaryGap:false},
    yAxis:[
      {type:"value",name:"Position"},
      {type:"value",name:"Torque / Feed"}
    ],
    series:[
      {name:"Position",type:"line",showSymbol:false,data:equipment.map(p=>p.position)},
      {name:"Torque",type:"line",showSymbol:false,yAxisIndex:1,data:equipment.map(p=>p.torque)},
      {name:"Feed",type:"line",showSymbol:false,yAxisIndex:1,data:equipment.map(p=>p.feed)}
    ]
  }),[equipment]);

  const xyOption = useMemo(()=>({
    tooltip:{trigger:"item"},
    grid:{left:60,right:30,top:35,bottom:50},
    xAxis:{type:"value",name:"Position"},
    yAxis:{type:"value",name:"Torque"},
    series:[{
      type:"line",showSymbol:false,
      data:equipment.map(p=>[p.position,p.torque])
    }]
  }),[equipment]);

  const profileOption = useMemo(()=>({
    tooltip:{trigger:"axis"},
    grid:{left:55,right:30,top:35,bottom:55},
    xAxis:{type:"value",name:"歯面位置 [%]"},
    yAxis:{type:"value",name:"偏差 [µm]"},
    dataZoom:[{type:"inside"},{type:"slider"}],
    series:[{
      type:"line",showSymbol:false,
      data:(measurement.profile ?? []).map((p:any)=>[p.profile_position,p.deviation_um])
    }]
  }),[measurement]);

  const trendOption = (field:keyof DailyPoint, title:string, unit:string) => ({
    title:{text:title,left:12,top:6,textStyle:{fontSize:14}},
    tooltip:{trigger:"axis"},
    grid:{left:55,right:20,top:45,bottom:45},
    xAxis:{type:"category",data:daily.map(d=>d.date),boundaryGap:false},
    yAxis:{type:"value",name:unit},
    dataZoom:[{type:"inside"}],
    series:[{type:"line",showSymbol:false,data:daily.map(d=>d[field])}]
  });

  const scatterOption = {
    title:{text:"設備負荷と歯面品質の相関",left:12,top:6,textStyle:{fontSize:14}},
    tooltip:{
      formatter:(p:any)=>`${p.data[2]}<br>Torque RMS: ${p.data[0]}<br>Profile RMS: ${p.data[1]}`
    },
    grid:{left:60,right:25,top:50,bottom:50},
    xAxis:{type:"value",name:"Torque RMS"},
    yAxis:{type:"value",name:"Profile RMS [µm]"},
    series:[{
      type:"scatter",
      symbolSize:6,
      data:scatter.map(s=>[s.x,s.y,s.serial_no,s.judgment,s.anomaly_type])
    }]
  };

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Equipment Insight</h1>
          <span>Gear Grinding Analytics</span>
        </div>
        <div className="tabs">
          <button className={tab==="cycle"?"active":""} onClick={()=>setTab("cycle")}>1サイクル解析</button>
          <button className={tab==="period"?"active":""} onClick={()=>setTab("period")}>期間解析</button>
        </div>
      </header>

      {loading && <div className="loading">Loading...</div>}

      {tab==="cycle" ? (
        <main>
          <section className="filters">
            <label>日付<input type="date" value={date} min="2026-07-05" max="2026-10-05" onChange={e=>setDate(e.target.value)}/></label>
            <label>Serial
              <select value={serial} onChange={e=>setSerial(e.target.value)}>
                {serials.map(s=><option key={s}>{s}</option>)}
              </select>
            </label>
            <label>Axis
              <select value={axis} onChange={e=>setAxis(Number(e.target.value))}>
                {[1,2,3,4,5,6].map(a=><option key={a} value={a}>Axis {a}</option>)}
              </select>
            </label>
            <div className="chips">
              <span className="chip">{trace.machine_name ?? "-"}</span>
              <span className="chip">砥石 {trace.wheel_id ?? "-"}</span>
              <span className={`chip ${trace.judgment==="NG"?"danger":""}`}>{trace.judgment ?? "-"}</span>
              <span className="chip">{anomalyLabel[trace.anomaly_type] ?? trace.anomaly_type ?? "-"}</span>
            </div>
          </section>

          <section className="feature-cards">
            <div><small>Torque RMS</small><strong>{features.torque_rms ?? "-"}</strong></div>
            <div><small>Torque Peak</small><strong>{features.torque_peak ?? "-"}</strong></div>
            <div><small>Feed Std</small><strong>{features.feed_std ?? "-"}</strong></div>
            <div><small>Position Error</small><strong>{features.position_error ?? "-"}</strong></div>
            <div><small>Dominant Freq</small><strong>{features.dominant_freq_hz ?? "-"} Hz</strong></div>
            <div><small>Profile RMS</small><strong>{measurement.metrics?.profile_rms_um ?? "-"} µm</strong></div>
          </section>

          <div className="grid two">
            <Panel title={`Axis ${axis} - Position / Torque / Feed`}>
              <ReactECharts option={waveOption} style={{height:380}}/>
            </Panel>
            <Panel title="Position - Torque">
              <ReactECharts option={xyOption} style={{height:380}}/>
            </Panel>
            <Panel title="歯面測定プロファイル">
              <ReactECharts option={profileOption} style={{height:330}}/>
              <div className="metric-row">
                <span>RMS {measurement.metrics?.profile_rms_um ?? "-"} µm</span>
                <span>P-V {measurement.metrics?.profile_pv_um ?? "-"} µm</span>
                <span>Waviness {measurement.metrics?.waviness_um ?? "-"} µm</span>
              </div>
            </Panel>
            <Panel title="変化点 / トレサビ">
              <div className="trace-list">
                <div><b>Serial</b><span>{trace.serial_no}</span></div>
                <div><b>Assy</b><span>{trace.assy_serial}</span></div>
                <div><b>設備</b><span>{trace.machine_name}</span></div>
                <div><b>砥石</b><span>{trace.wheel_id}</span></div>
                <div><b>Dress count</b><span>{trace.dress_count}</span></div>
                <div><b>生産日時</b><span>{trace.production_time}</span></div>
              </div>
              <table>
                <thead><tr><th>時刻</th><th>項目</th><th>内容</th></tr></thead>
                <tbody>{changes.map((c,i)=><tr key={i}><td>{c.event_time?.slice(11,23)}</td><td>{c.item_name}</td><td>{c.description}</td></tr>)}</tbody>
              </table>
            </Panel>
          </div>
        </main>
      ) : (
        <main>
          <section className="filters">
            <label>開始<input type="date" value={start} min="2026-07-05" max="2026-10-05" onChange={e=>setStart(e.target.value)}/></label>
            <label>終了<input type="date" value={end} min="2026-07-05" max="2026-10-05" onChange={e=>setEnd(e.target.value)}/></label>
            <label>設備
              <select value={machine} onChange={e=>setMachine(e.target.value)}>
                <option value="ALL">全設備</option>
                {["M01","M02","M03","M04"].map(m=><option key={m}>{m}</option>)}
              </select>
            </label>
            <label>Axis
              <select value={axis} onChange={e=>setAxis(Number(e.target.value))}>
                {[1,2,3,4,5,6].map(a=><option key={a} value={a}>Axis {a}</option>)}
              </select>
            </label>
          </section>

          <section className="feature-cards">
            <div><small>Cycles</small><strong>{summary.cycles?.toLocaleString()}</strong></div>
            <div><small>NG</small><strong>{summary.ng_count?.toLocaleString()}</strong></div>
            <div><small>NG Rate</small><strong>{summary.ng_rate}%</strong></div>
          </section>

          <div className="grid two">
            <Panel title="Torque RMS 長期トレンド"><ReactECharts option={trendOption("torque_rms","Torque RMS","")} style={{height:300}}/></Panel>
            <Panel title="歯面 Profile RMS 長期トレンド"><ReactECharts option={trendOption("profile_rms_um","Profile RMS","µm")} style={{height:300}}/></Panel>
            <Panel title="Feedばらつき"><ReactECharts option={trendOption("feed_std","Feed Std","")} style={{height:300}}/></Panel>
            <Panel title="Position Error"><ReactECharts option={trendOption("position_error","Position Error","")} style={{height:300}}/></Panel>
            <Panel title="Waviness"><ReactECharts option={trendOption("waviness_um","Waviness","µm")} style={{height:300}}/></Panel>
            <Panel title="NG率"><ReactECharts option={trendOption("ng_rate","NG Rate","%")} style={{height:300}}/></Panel>
          </div>

          <div className="grid two period-bottom">
            <Panel title="設備特徴量 × 品質">
              <ReactECharts option={scatterOption} style={{height:380}}/>
            </Panel>
            <Panel title="異常シリアルランキング">
              <div className="table-wrap anomaly-table">
                <table>
                  <thead><tr><th>Serial</th><th>日時</th><th>設備</th><th>異常</th><th>Score</th><th>Profile RMS</th></tr></thead>
                  <tbody>
                    {anomalies.map(r=><tr key={r.serial_no} onClick={()=>jumpToCycle(r)}>
                      <td className="link">{r.serial_no}</td>
                      <td>{r.production_time}</td>
                      <td>{r.machine_name}</td>
                      <td>{anomalyLabel[r.anomaly_type] ?? r.anomaly_type}</td>
                      <td>{r.anomaly_score.toFixed(2)}</td>
                      <td>{r.profile_rms_um.toFixed(2)}</td>
                    </tr>)}
                  </tbody>
                </table>
              </div>
              <p className="hint">行をクリックすると、そのSerialの1サイクル解析へ移動します。</p>
            </Panel>
          </div>
        </main>
      )}
    </div>
  );
}

function Panel({title,children}:{title:string;children:React.ReactNode}) {
  return <section className="panel"><div className="panel-title">{title}</div><div className="panel-body">{children}</div></section>;
}
