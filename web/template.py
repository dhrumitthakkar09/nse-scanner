"""
Dashboard HTML template.

Kept in its own module so routes.py stays readable.
"""

HTML: str = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>NSE F&O Scan Pro</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet"/>
<style>
:root{
  --bg:    #080c16;
  --bg2:   #0e1525;
  --bg3:   #162035;
  --bg4:   #1e2a45;
  --bdr:   #25335a;
  --bdr2:  #344470;
  --tx:    #dde6f8;
  --tx2:   #8aa0cc;
  --tx3:   #4d6090;
  --ac:    #4d8ef7;
  --ac2:   #2255cc;
  --ac-bg: #12204a;
  --gr:    #34d399;
  --gr2:   #10b981;
  --gr-bg: #052e1c;
  --rd:    #f87171;
  --rd2:   #dc2626;
  --rd-bg: #2a0808;
  --or:    #fbbf24;
  --or-bg: #2c1800;
  --pu:    #a78bfa;
  --pu-bg: #1c0f3a;
  --ff: 'Inter', sans-serif;
  --mono: 'JetBrains Mono', monospace;
  --r: 10px;
  --r2: 6px;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html{scroll-behavior:smooth;}
body{font-family:var(--ff);background:var(--bg);color:var(--tx);font-size:14px;line-height:1.55;min-height:100vh;}

/* ── TOPBAR ────────────────────────────── */
.topbar{
  position:sticky;top:0;z-index:300;
  display:flex;align-items:center;height:58px;padding:0 24px;gap:20px;
  background:var(--bg2);border-bottom:1px solid var(--bdr);
  box-shadow:0 4px 24px rgba(0,0,0,.5);
}
.logo{display:flex;align-items:center;gap:10px;flex-shrink:0;}
.logo-icon{
  width:32px;height:32px;border-radius:8px;flex-shrink:0;
  background:linear-gradient(135deg,#1a3880,#4d8ef7);
  display:flex;align-items:center;justify-content:center;
  font-size:10px;font-weight:800;color:#fff;letter-spacing:-.02em;
  box-shadow:0 0 18px rgba(77,142,247,.35);
}
.logo-name{font-size:15px;font-weight:800;color:var(--tx);letter-spacing:-.03em;}
.logo-sub {font-size:10.5px;color:var(--tx3);margin-top:1px;}

/* tab nav */
.tabs{display:flex;gap:2px;background:var(--bg3);border-radius:8px;padding:3px;}
.tab-btn{
  padding:5px 16px;border:none;cursor:pointer;
  font-family:var(--ff);font-size:12.5px;font-weight:600;
  color:var(--tx3);background:transparent;border-radius:6px;
  transition:all .18s;white-space:nowrap;
}
.tab-btn:hover{color:var(--tx2);background:var(--bg4);}
.tab-btn.active{color:var(--tx);background:var(--bg4);box-shadow:0 1px 5px rgba(0,0,0,.4);}
.tab-settings{color:var(--or) !important;}
.tab-settings.active{color:var(--or) !important;}

/* topbar right */
.tb-right{display:flex;align-items:center;gap:12px;margin-left:auto;}
.clock{font-family:var(--mono);font-size:12px;font-weight:500;color:var(--tx2);background:var(--bg3);padding:5px 10px;border-radius:var(--r2);border:1px solid var(--bdr);}
.mkt-badge{display:flex;align-items:center;gap:6px;padding:5px 11px;border-radius:20px;font-size:11.5px;font-weight:700;border:1px solid var(--bdr2);background:var(--bg3);color:var(--tx3);}
.mkt-badge.open{background:var(--gr-bg);border-color:var(--gr2);color:var(--gr);}
.mkt-dot{width:7px;height:7px;border-radius:50%;background:currentColor;flex-shrink:0;}
.mkt-badge.open .mkt-dot{animation:pdot 1.8s ease-in-out infinite;}
@keyframes pdot{0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,.5);}50%{box-shadow:0 0 0 5px rgba(52,211,153,0);}}
.scan-btn{
  display:flex;align-items:center;gap:7px;padding:7px 16px;border-radius:var(--r2);
  background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;border:none;cursor:pointer;
  font-family:var(--ff);font-size:12.5px;font-weight:700;
  box-shadow:0 0 14px rgba(77,142,247,.28);transition:all .18s;
}
.scan-btn:hover{transform:translateY(-1px);box-shadow:0 4px 20px rgba(77,142,247,.45);}
.scan-btn:active{transform:translateY(0);}
.scan-btn:disabled{background:var(--bg4);color:var(--tx3);box-shadow:none;cursor:not-allowed;transform:none;}

/* ── STATUS STRIP ──────────────────────── */
.status-strip{
  display:flex;align-items:stretch;
  background:var(--bg2);border-bottom:1px solid var(--bdr);flex-wrap:wrap;
}
.stat-cell{display:flex;flex-direction:column;justify-content:center;padding:8px 20px;border-right:1px solid var(--bdr);gap:2px;}
.stat-cell:last-child{border-right:none;margin-left:auto;}
.stat-lbl{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:var(--tx3);}
.stat-val{font-size:13px;font-weight:700;color:var(--tx);font-family:var(--mono);}
.sp{display:inline-flex;align-items:center;gap:5px;padding:2px 9px;border-radius:20px;font-size:11.5px;font-weight:700;}
.sp-idle    {background:var(--bg4);color:var(--tx3);}
.sp-scanning{background:var(--ac-bg);color:var(--ac);}
.sp-done    {background:var(--gr-bg);color:var(--gr);}
.sp-error   {background:var(--rd-bg);color:var(--rd);}
.spin{display:inline-block;animation:spin .75s linear infinite;}
@keyframes spin{to{transform:rotate(360deg);}}

/* ── CONTENT ───────────────────────────── */
.content{max-width:1800px;margin:0 auto;padding:22px 24px 56px;}
.pane{display:none;}
.pane.active{display:block;}

/* ── SECTION HEADER ────────────────────── */
.sh{display:flex;align-items:center;gap:10px;margin-bottom:14px;}
.sh-title{font-size:14px;font-weight:800;color:var(--tx);letter-spacing:-.02em;}
.sh-sub{font-size:11.5px;color:var(--tx3);font-weight:500;}
.sh-badge{padding:3px 10px;border-radius:20px;background:var(--ac-bg);color:var(--ac);font-size:11px;font-weight:700;}
.sh-rule{flex:1;height:1px;background:var(--bdr);}

/* ── SECTOR STRIP ──────────────────────── */
.strip{display:flex;gap:8px;overflow-x:auto;padding-bottom:4px;margin-bottom:20px;scrollbar-width:thin;scrollbar-color:var(--bdr) transparent;}
.sc-chip{
  display:flex;flex-direction:column;align-items:center;padding:8px 14px;border-radius:8px;
  background:var(--bg3);border:1px solid var(--bdr);flex-shrink:0;min-width:86px;
  cursor:default;transition:all .15s;
}
.sc-chip:hover{border-color:var(--bdr2);}
.sc-chip.tr{background:var(--gr-bg);border-color:var(--gr2);}
.sc-chip-name{font-size:10.5px;font-weight:700;color:var(--tx2);}
.sc-chip-pct{font-size:14px;font-weight:800;font-family:var(--mono);margin-top:2px;}
.sc-chip.tr .sc-chip-name{color:var(--gr);}

/* ── HEATMAP ───────────────────────────── */
.hmap{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin-bottom:26px;}
.hm-cell{border-radius:10px;padding:16px 14px 12px;cursor:default;transition:transform .15s,box-shadow .15s;position:relative;overflow:hidden;}
.hm-cell:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,.6);}
.hm-cell::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.04) 0%,rgba(0,0,0,.12) 100%);pointer-events:none;}
.hm-name{font-size:12.5px;font-weight:700;margin-bottom:4px;}
.hm-pct{font-size:28px;font-weight:800;font-family:var(--mono);letter-spacing:-.03em;line-height:1;}
.hm-sub{font-size:10px;font-weight:500;margin-top:6px;opacity:.72;}
.hm-badge{position:absolute;top:9px;right:9px;font-size:9.5px;font-weight:700;padding:2px 6px;border-radius:4px;}
.hz0{background:#042a16;color:#4ade80;}
.hz1{background:#073320;color:#34d399;}
.hz2{background:#122608;color:#a3e635;}
.hz3{background:#271a00;color:#fbbf24;}
.hz4{background:#220e00;color:#f97316;}
.hzN{background:var(--bg3);color:var(--tx3);border:1px solid var(--bdr);}

/* ── GAINERS / LOSERS ──────────────────── */
.gl-wrap{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:26px;}
.gl-card{background:var(--bg2);border:1px solid var(--bdr);border-radius:var(--r);overflow:hidden;}
.gl-head{display:flex;align-items:center;gap:8px;padding:11px 16px;border-bottom:1px solid var(--bdr);font-size:12px;font-weight:700;}
.gl-head.g{background:var(--gr-bg);color:var(--gr);}
.gl-head.l{background:var(--rd-bg);color:var(--rd);}
.gl-body{padding:6px 0;}
.gl-row{display:flex;align-items:center;padding:7px 16px;gap:10px;transition:background .1s;}
.gl-row:hover{background:var(--bg3);}
.gl-n{font-size:10px;font-weight:700;color:var(--tx3);font-family:var(--mono);width:16px;flex-shrink:0;}
.gl-name{font-size:12.5px;font-weight:700;color:var(--tx);flex:1;}
.gl-bar-bg{flex:1;height:4px;background:var(--bg4);border-radius:2px;overflow:hidden;}
.gl-bar{height:100%;border-radius:2px;transition:width .4s;}
.gl-chg{font-size:12.5px;font-weight:700;font-family:var(--mono);width:58px;text-align:right;flex-shrink:0;}

/* ── SECTOR CARDS ──────────────────────── */
.sec-cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:11px;margin-bottom:26px;}
.sec-card{background:var(--bg2);border:1px solid var(--bdr);border-radius:var(--r);padding:15px 16px;transition:all .18s;cursor:default;position:relative;overflow:hidden;}
.sec-card:hover{border-color:var(--bdr2);transform:translateY(-2px);box-shadow:0 6px 22px rgba(0,0,0,.5);}
.sec-card.tr{border-color:var(--gr2);background:linear-gradient(145deg,var(--gr-bg),var(--bg2));}
.sec-card.tr::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--gr2),var(--gr));}
.sctop{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:7px;}
.scname{font-size:13px;font-weight:800;color:var(--tx);}
.scsym{font-size:10px;color:var(--tx3);font-family:var(--mono);margin-top:2px;}
.scbadge{font-size:9.5px;font-weight:700;padding:2px 7px;border-radius:4px;white-space:nowrap;}
.sbz{background:var(--gr-bg);color:var(--gr);}
.sbf{background:var(--bg4);color:var(--tx3);}
.scdist{font-size:24px;font-weight:800;letter-spacing:-.03em;margin:3px 0 7px;}
.scmeta{display:flex;justify-content:space-between;font-size:10.5px;color:var(--tx3);margin-bottom:8px;}
.scmeta span{color:var(--tx2);font-weight:600;}
.dbar{width:100%;height:3px;background:var(--bg4);border-radius:2px;position:relative;overflow:visible;}
.dbar-f{height:100%;border-radius:2px;position:absolute;left:0;top:0;transition:width .5s;}
.dbar-p{width:9px;height:9px;border-radius:50%;position:absolute;top:-3px;transform:translateX(-50%);border:2px solid var(--bg2);transition:left .5s;}
.dbar-lbl{display:flex;justify-content:space-between;font-size:9px;color:var(--tx3);margin-top:4px;font-family:var(--mono);}

/* ── TABLE ─────────────────────────────── */
.tbl-card{background:var(--bg2);border:1px solid var(--bdr);border-radius:var(--r);overflow:hidden;margin-bottom:20px;}
.tbl-bar{display:flex;align-items:center;gap:9px;padding:11px 16px;background:var(--bg3);border-bottom:1px solid var(--bdr);flex-wrap:wrap;}
.tbl-title{font-size:12.5px;font-weight:700;color:var(--tx);}
.tbl-cnt{font-size:11.5px;color:var(--tx3);}
.sf-wrap{display:flex;gap:5px;flex-wrap:wrap;}
.sf-btn{
  padding:3px 9px;border-radius:20px;border:1px solid var(--bdr);
  background:transparent;color:var(--tx3);font-family:var(--ff);font-size:10.5px;font-weight:600;
  cursor:pointer;transition:all .15s;
}
.sf-btn:hover{border-color:var(--ac);color:var(--ac);}
.sf-btn.on{border-color:var(--ac);background:var(--ac-bg);color:var(--ac);}
.tbl-search{
  margin-left:auto;padding:6px 11px;border-radius:var(--r2);
  border:1px solid var(--bdr2);background:var(--bg4);color:var(--tx);
  font-family:var(--ff);font-size:12.5px;outline:none;width:190px;
}
.tbl-search:focus{border-color:var(--ac);}
.tbl-search::placeholder{color:var(--tx3);}
.tbl-wrap{overflow-x:auto;}
table{width:100%;border-collapse:collapse;}
thead th{
  padding:10px 13px;background:var(--bg3);border-bottom:1px solid var(--bdr2);
  font-size:11px;font-weight:700;color:var(--tx3);text-align:left;white-space:nowrap;
  cursor:pointer;user-select:none;text-transform:uppercase;letter-spacing:.05em;
}
thead th:hover{color:var(--ac);background:var(--bg4);}
thead th.r{text-align:right;}
thead th .si{margin-left:3px;font-size:9.5px;opacity:.35;}
thead th.sort-asc  .si::after{content:'↑';opacity:1;color:var(--ac);}
thead th.sort-desc .si::after{content:'↓';opacity:1;color:var(--ac);}
thead th:not(.sort-asc):not(.sort-desc) .si::after{content:'↕';}
tbody tr{border-bottom:1px solid var(--bdr);transition:background .1s;}
tbody tr:last-child{border-bottom:none;}
tbody tr:hover{background:var(--bg3);}
tbody td{padding:10px 13px;font-size:13px;vertical-align:middle;white-space:nowrap;}
tbody td.r{text-align:right;}
.td-rank{font-family:var(--mono);font-size:11px;color:var(--tx3);}
.td-name{font-size:13.5px;font-weight:800;color:var(--tx);}
.td-sec{font-size:10.5px;color:var(--tx3);margin-top:2px;}
.td-price{font-family:var(--mono);font-size:13px;font-weight:700;color:var(--tx);}
.td-ath  {font-family:var(--mono);font-size:10.5px;color:var(--tx3);}
.dp{display:inline-flex;padding:3px 9px;border-radius:20px;font-size:11.5px;font-weight:700;font-family:var(--mono);}
.dp-z1{background:var(--gr-bg);color:#4ade80;}
.dp-z2{background:#062a1e;color:#34d399;}
.dp-z3{background:#122206;color:#a3e635;}
.dp-z4{background:var(--or-bg);color:var(--or);}
.rp{display:inline-block;padding:2px 8px;border-radius:4px;background:var(--ac-bg);color:var(--ac);font-size:11.5px;font-weight:600;font-family:var(--mono);}
.chg-p{color:var(--gr);font-weight:700;font-family:var(--mono);}
.chg-n{color:var(--rd);font-weight:700;font-family:var(--mono);}
.vs-h{color:var(--gr);font-weight:700;font-family:var(--mono);}
.vs-n{color:var(--tx3);font-family:var(--mono);}
.tu{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:6px;background:var(--gr-bg);color:var(--gr);font-size:12px;}
.td{display:inline-flex;align-items:center;justify-content:center;width:25px;height:25px;border-radius:6px;background:var(--or-bg);color:var(--or);font-size:11px;}

/* ── LOG ───────────────────────────────── */
.log-card{background:var(--bg2);border:1px solid var(--bdr);border-radius:var(--r);overflow:hidden;margin-bottom:20px;}
.log-head{display:flex;align-items:center;gap:8px;padding:9px 16px;background:var(--bg3);border-bottom:1px solid var(--bdr);font-size:11px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.06em;}
.log-body{max-height:150px;overflow-y:auto;padding:9px 16px;font-family:var(--mono);font-size:11.5px;line-height:1.75;}
.ll-ok{color:var(--gr);}
.ll-w{color:var(--or);}
.ll-e{color:var(--rd);}
.ll-d{color:var(--tx3);}

/* ── EMPTY ─────────────────────────────── */
.empty{text-align:center;padding:44px 20px;color:var(--tx3);}
.e-ico{font-size:32px;margin-bottom:12px;}
.e-txt{font-size:14px;font-weight:700;color:var(--tx2);}
.e-sub{font-size:11.5px;margin-top:5px;}

/* ── SETTINGS ──────────────────────────── */
.cfg-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(360px,1fr));gap:16px;align-items:start;}
.cfg-card{background:var(--bg2);border:1px solid var(--bdr);border-radius:var(--r);overflow:hidden;}
.cfg-head{display:flex;align-items:center;gap:9px;padding:12px 18px;background:var(--bg3);border-bottom:1px solid var(--bdr);font-size:11.5px;font-weight:700;color:var(--tx2);text-transform:uppercase;letter-spacing:.07em;}
.cfg-body{padding:18px;display:flex;flex-direction:column;gap:14px;}
.cfg-row{display:flex;flex-direction:column;gap:5px;}
.cfg-2{display:grid;grid-template-columns:1fr 1fr;gap:11px;}
.cfg-lbl{font-size:10.5px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.07em;}
.cfg-inp{
  padding:8px 11px;border-radius:var(--r2);border:1px solid var(--bdr2);
  background:var(--bg4);color:var(--tx);font-family:var(--mono);font-size:12.5px;
  outline:none;width:100%;transition:border-color .15s;
}
.cfg-inp:focus{border-color:var(--ac);box-shadow:0 0 0 2px rgba(77,142,247,.14);}
.cfg-inp::placeholder{color:var(--tx3);}
.cfg-hint{font-size:10.5px;color:var(--tx3);}
.cfg-btns{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.btn{padding:8px 18px;border-radius:var(--r2);font-family:var(--ff);font-size:12.5px;font-weight:700;cursor:pointer;border:none;transition:all .18s;}
.btn-p{background:linear-gradient(135deg,var(--ac),var(--ac2));color:#fff;box-shadow:0 0 12px rgba(77,142,247,.22);}
.btn-p:hover{box-shadow:0 4px 18px rgba(77,142,247,.4);transform:translateY(-1px);}
.btn-s{background:var(--bg4);color:var(--tx3);border:1px solid var(--bdr2);}
.btn-s:hover{color:var(--tx2);border-color:var(--tx3);}
.pw-wrap{position:relative;}
.pw-wrap .cfg-inp{padding-right:38px;}
.pw-eye{position:absolute;right:9px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;color:var(--tx3);font-size:13px;padding:3px;}
.pw-eye:hover{color:var(--tx2);}
.toast{padding:6px 12px;border-radius:var(--r2);font-size:11.5px;font-weight:600;display:none;}
.toast-ok{background:var(--gr-bg);color:var(--gr);}
.toast-err{background:var(--rd-bg);color:var(--rd);}
.tg-res{font-size:11.5px;font-weight:600;margin-top:4px;}
.tg-ok{color:var(--gr);}
.tg-err{color:var(--rd);}

/* ── INTRADAY HEATMAP ──────────────────── */
.imap{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px;margin-bottom:26px;}
.im-cell{border-radius:10px;padding:16px 14px 12px;cursor:default;transition:transform .15s,box-shadow .15s;position:relative;overflow:hidden;}
.im-cell:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,0,0,.6);}
.im-cell::after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(255,255,255,.04) 0%,rgba(0,0,0,.12) 100%);pointer-events:none;}
.im-name{font-size:12.5px;font-weight:700;margin-bottom:4px;}
.im-pct{font-size:28px;font-weight:800;font-family:var(--mono);letter-spacing:-.03em;line-height:1;}
.im-sub{font-size:10px;font-weight:500;margin-top:6px;opacity:.72;}

/* ── SCROLLBAR ─────────────────────────── */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--bdr2);border-radius:2px;}

/* ── RESPONSIVE ────────────────────────── */
@media(max-width:768px){
  .content{padding:14px;}
  .topbar{padding:0 14px;gap:10px;}
  .gl-wrap{grid-template-columns:1fr;}
  .cfg-grid{grid-template-columns:1fr;}
  .hmap{grid-template-columns:repeat(2,1fr);}
  .logo-sub{display:none;}
  .stat-cell:nth-child(n+4){display:none;}
}
</style>
</head>
<body>

<!-- ══ TOPBAR ═══════════════════════════════════════════ -->
<div class="topbar">
  <div class="logo">
    <div class="logo-icon">FO</div>
    <div>
      <div class="logo-name">F&amp;O Scan Pro</div>
      <div class="logo-sub">220 Stocks · 75-Min · Dhan API</div>
    </div>
  </div>

  <div class="tabs">
    <button class="tab-btn active" id="tab-scanner"  onclick="showTab('scanner')">Scanner</button>
    <button class="tab-btn"        id="tab-sectors"  onclick="showTab('sectors')">Sectors</button>
    <button class="tab-btn tab-settings" id="tab-settings" onclick="showTab('settings')">⚙ Settings</button>
  </div>

  <div class="tb-right">
    <div class="clock" id="clock">--:--:-- IST</div>
    <div class="mkt-badge" id="mktBadge">
      <div class="mkt-dot"></div><span id="mktTxt">MARKET</span>
    </div>
    <button class="scan-btn" id="scanBtn" onclick="triggerScan()">
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2.2">
        <path d="M13.5 8A5.5 5.5 0 1 1 8 2.5"/><path d="M13.5 2.5v3h-3"/>
      </svg>Scan Now
    </button>
  </div>
</div>

<!-- ══ STATUS STRIP ══════════════════════════════════════ -->
<div class="status-strip">
  <div class="stat-cell"><div class="stat-lbl">Status</div><div class="stat-val" id="statusPill"><span class="sp sp-idle">Idle</span></div></div>
  <div class="stat-cell"><div class="stat-lbl">Last Scan</div><div class="stat-val" id="lastScan">—</div></div>
  <div class="stat-cell"><div class="stat-lbl">Next Scan</div><div class="stat-val" id="nextScan">—</div></div>
  <div class="stat-cell"><div class="stat-lbl">Signals</div><div class="stat-val" id="signalCnt">0</div></div>
  <div class="stat-cell"><div class="stat-lbl">Universe</div><div class="stat-val">220 F&amp;O</div></div>
  <div class="stat-cell"><div class="stat-lbl">Scan #</div><div class="stat-val" id="scanCnt">0</div></div>
</div>

<div class="content">

<!-- ══ SCANNER PANE ══════════════════════════════════════ -->
<div class="pane active" id="pane-scanner">

  <div class="sh">
    <div class="sh-title">Sector Pulse</div>
    <div class="sh-badge" id="stripBadge">0 trending</div>
    <div class="sh-rule"></div>
  </div>
  <div class="strip" id="strip">
    <div class="empty"><div class="e-sub">Run a scan to load sector data</div></div>
  </div>

  <div class="sh" style="margin-top:6px">
    <div class="sh-title">Qualified Stocks</div>
    <div class="sh-badge" id="stockBadge">0 results</div>
    <div class="sh-sub">Consolidating 0–15% below ATH · EMA(9)&gt;EMA(21) · 200K+ avg vol</div>
    <div class="sh-rule"></div>
  </div>

  <div class="tbl-card">
    <div class="tbl-bar">
      <div class="tbl-title">Results</div>
      <div class="tbl-cnt" id="tblCnt">—</div>
      <div class="sf-wrap" id="sfBtns">
        <button class="sf-btn on" data-s="all" onclick="setSF('all',this)">All</button>
      </div>
      <input class="tbl-search" id="searchBox" type="text" placeholder="Search stock or sector…" oninput="filterTable()"/>
    </div>
    <div class="tbl-wrap">
      <table>
        <thead>
          <tr>
            <th data-col="idx">#<span class="si"></span></th>
            <th data-col="name">Stock<span class="si"></span></th>
            <th data-col="sector">Sector<span class="si"></span></th>
            <th data-col="price" class="r">CMP ₹<span class="si"></span></th>
            <th data-col="ath" class="r">ATH ₹<span class="si"></span></th>
            <th data-col="dist_pct" class="r sort-asc">Dist ATH<span class="si"></span></th>
            <th data-col="range_pct" class="r">8C Range<span class="si"></span></th>
            <th data-col="chg_1d" class="r">1D Chg<span class="si"></span></th>
            <th data-col="vol_surge" class="r">Vol×<span class="si"></span></th>
            <th data-col="uptrend" class="r">Trend<span class="si"></span></th>
          </tr>
        </thead>
        <tbody id="tbody">
          <tr><td colspan="10"><div class="empty"><div class="e-ico">📡</div><div class="e-txt">Awaiting first scan</div><div class="e-sub">Click Scan Now to begin</div></div></td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="log-card">
    <div class="log-head">
      <svg width="11" height="11" viewBox="0 0 16 16" fill="currentColor"><path d="M5 3h6v2H5V3zm-2 4h10v2H3V7zm0 4h7v2H3v-2z"/></svg>
      Activity Log
    </div>
    <div class="log-body" id="logBody"><div class="ll-d">Waiting for scan…</div></div>
  </div>

</div><!-- /scanner -->

<!-- ══ SECTORS PANE ═══════════════════════════════════════ -->
<div class="pane" id="pane-sectors">

  <div class="sh">
    <div class="sh-title">Intraday Sector Heatmap</div>
    <div class="sh-sub">% change from today&#39;s open · All 12 sectors</div>
    <div class="sh-rule"></div>
  </div>
  <div class="imap" id="imap">
    <div class="empty" style="grid-column:1/-1"><div class="e-ico">📊</div><div class="e-txt">No data yet</div><div class="e-sub">Run a scan first</div></div>
  </div>

  <div class="sh">
    <div class="sh-title">Intraday Gainers &amp; Losers</div>
    <div class="sh-sub">Today&#39;s % change from open · All F&amp;O stocks</div>
    <div class="sh-badge" id="intradayBadge">0 stocks</div>
    <div class="sh-rule"></div>
  </div>
  <div class="gl-wrap">
    <div class="gl-card">
      <div class="gl-head g">▲ Top Gainers</div>
      <div class="gl-body" id="intradayGainers"><div class="empty" style="padding:20px"><div class="e-sub">No data</div></div></div>
    </div>
    <div class="gl-card">
      <div class="gl-head l">▼ Top Losers</div>
      <div class="gl-body" id="intradayLosers"><div class="empty" style="padding:20px"><div class="e-sub">No data</div></div></div>
    </div>
  </div>

</div><!-- /sectors -->

<!-- ══ SETTINGS PANE ══════════════════════════════════════ -->
<div class="pane" id="pane-settings">

  <div class="sh" style="margin-bottom:18px">
    <div class="sh-title">Configuration</div>
    <div class="sh-sub">Changes take effect immediately and are saved to config.yaml</div>
    <div class="sh-rule"></div>
  </div>

  <div class="cfg-grid">

    <!-- Dhan API -->
    <div class="cfg-card">
      <div class="cfg-head">🔑 &nbsp;Dhan API Credentials</div>
      <div class="cfg-body">
        <div class="cfg-row">
          <div class="cfg-lbl">Client ID</div>
          <input class="cfg-inp" id="ci-client" type="text" placeholder="e.g. 1106384983"/>
        </div>
        <div class="cfg-row">
          <div class="cfg-lbl">Access Token</div>
          <div class="pw-wrap">
            <input class="cfg-inp" id="ci-token" type="password" placeholder="eyJ…"/>
            <button class="pw-eye" onclick="togglePw('ci-token',this)">👁</button>
          </div>
          <div class="cfg-hint">JWT from Dhan HQ → My Profile → API Access</div>
        </div>
        <div class="cfg-btns">
          <button class="btn btn-p" onclick="saveDhan()">Save Credentials</button>
          <span class="toast" id="t-dhan"></span>
        </div>
      </div>
    </div>

    <!-- Telegram -->
    <div class="cfg-card">
      <div class="cfg-head">📨 &nbsp;Telegram Alerts</div>
      <div class="cfg-body">
        <div class="cfg-row">
          <div class="cfg-lbl">Bot Token</div>
          <div class="pw-wrap">
            <input class="cfg-inp" id="ci-tg-tok" type="password" placeholder="123456:ABCdef…"/>
            <button class="pw-eye" onclick="togglePw('ci-tg-tok',this)">👁</button>
          </div>
          <div class="cfg-hint">Get from @BotFather on Telegram</div>
        </div>
        <div class="cfg-row">
          <div class="cfg-lbl">Chat / Channel ID</div>
          <input class="cfg-inp" id="ci-tg-chat" type="text" placeholder="-100xxxxxxxxxx or @channel"/>
          <div class="cfg-hint">Negative ID for groups, @username for channels</div>
        </div>
        <div class="cfg-btns">
          <button class="btn btn-p" onclick="saveTG()">Save</button>
          <button class="btn btn-s" onclick="testTG()">Test Alert</button>
          <span class="toast" id="t-tg"></span>
        </div>
        <div class="tg-res" id="tg-res"></div>
      </div>
    </div>

    <!-- Scan Params -->
    <div class="cfg-card">
      <div class="cfg-head">⚙ &nbsp;Scan Parameters</div>
      <div class="cfg-body">
        <div class="cfg-2">
          <div class="cfg-row"><div class="cfg-lbl">Scan Interval (min)</div><input class="cfg-inp" id="ci-interval" type="number" min="5" max="120" placeholder="15"/></div>
          <div class="cfg-row"><div class="cfg-lbl">ATH Max Distance %</div><input class="cfg-inp" id="ci-ath" type="number" step="0.5" min="1" max="30" placeholder="15"/></div>
        </div>
        <div class="cfg-2">
          <div class="cfg-row"><div class="cfg-lbl">Consol. Candles</div><input class="cfg-inp" id="ci-candles" type="number" min="4" max="20" placeholder="8"/></div>
          <div class="cfg-row"><div class="cfg-lbl">Max Range %</div><input class="cfg-inp" id="ci-range" type="number" step="0.5" min="1" max="20" placeholder="5"/></div>
        </div>
        <div class="cfg-2">
          <div class="cfg-row"><div class="cfg-lbl">Min Avg Volume</div><input class="cfg-inp" id="ci-vol" type="number" step="10000" min="10000" placeholder="200000"/></div>
          <div class="cfg-row"><div class="cfg-lbl">API Delay (sec)</div><input class="cfg-inp" id="ci-delay" type="number" step="0.1" min="0.1" max="5" placeholder="0.4"/></div>
        </div>
        <div class="cfg-btns">
          <button class="btn btn-p" onclick="saveParams()">Save Parameters</button>
          <button class="btn btn-s" onclick="loadCfg()">Reset</button>
          <span class="toast" id="t-params"></span>
        </div>
      </div>
    </div>

  </div>

  <!-- Scrip Master Diagnostics -->
  <div class="cfg-grid" style="margin-top:16px">
    <div class="cfg-card" style="grid-column:1/-1">
      <div class="cfg-head">🔍 &nbsp;Scrip Master Diagnostics</div>
      <div class="cfg-body">
        <div style="color:var(--tx2);font-size:12.5px;margin-bottom:10px">
          Use this if Intraday Gainers/Losers shows very few stocks. The scrip master maps stock symbols
          to Dhan security IDs — if it's stale or failed to load, most stocks will be skipped.
        </div>
        <div class="cfg-btns" style="flex-wrap:wrap;gap:8px">
          <button class="btn btn-s" onclick="checkScrip()">Check Scrip Master</button>
          <button class="btn btn-p" onclick="reloadScrip()">Force Reload Scrip Master</button>
          <span class="toast" id="t-scrip"></span>
        </div>
        <div id="scrip-result" style="margin-top:10px;font-size:12.5px;font-family:var(--mono);
             color:var(--tx2);background:var(--bg3);border:1px solid var(--bdr);
             border-radius:6px;padding:10px 14px;display:none;white-space:pre-wrap;
             line-height:1.7"></div>
      </div>
    </div>
  </div>

</div><!-- /settings -->

</div><!-- /content -->

<script>
// ════════════════════ STATE ══════════════════════
let allStocks  = [], allSectors = [], allIntradayStocks = [];
let sortCol = 'dist_pct', sortDir = 'asc', activeSector = 'all';

// ──────────────────── UTILS ──────────────────────
const fmt = (n,d=2) => n==null?'—':Number(n).toLocaleString('en-IN',{minimumFractionDigits:d,maximumFractionDigits:d});
const fmtC = n => n==null?'—':(n>=0?'+':'')+fmt(n,2)+'%';

function dClass(d){
  if(d==null) return 'dp-z4';
  if(d<=5) return 'dp-z1';
  if(d<=9) return 'dp-z2';
  if(d<=12) return 'dp-z3';
  return 'dp-z4';
}
function dCol(d){
  if(d==null||d>15) return '#4d6090';
  if(d<=5)  return '#4ade80';
  if(d<=8)  return '#34d399';
  if(d<=11) return '#a3e635';
  if(d<=13) return '#fbbf24';
  return '#f97316';
}
function hmCls(d){
  if(d==null||d>15) return 'hzN';
  if(d<=5)  return 'hz0';
  if(d<=8)  return 'hz1';
  if(d<=11) return 'hz2';
  if(d<=13) return 'hz3';
  return 'hz4';
}
function iColor(chg){
  if(chg==null) return 'var(--tx3)';
  if(chg>=3)   return '#4ade80';
  if(chg>=1)   return '#34d399';
  if(chg>=0)   return '#6ee7b7';
  if(chg>=-1)  return '#fca5a5';
  if(chg>=-3)  return '#f87171';
  return '#dc2626';
}
function iBg(chg){
  if(chg==null) return 'var(--bg3)';
  if(chg>=3)   return '#042a16';
  if(chg>=1)   return '#052e1c';
  if(chg>=0)   return '#0d2018';
  if(chg>=-1)  return '#2a0a0a';
  if(chg>=-3)  return '#300808';
  return '#3a0505';
}

// ──────────────────── TABS ───────────────────────
function showTab(t){
  document.querySelectorAll('.pane').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('pane-'+t).classList.add('active');
  document.getElementById('tab-'+t).classList.add('active');
  if(t==='settings') loadCfg();
}

// ────────────────── SECTOR STRIP ─────────────────
function renderStrip(sectors){
  const el = document.getElementById('strip');
  const t  = sectors.filter(s=>s.trending).length;
  document.getElementById('stripBadge').textContent = t+' trending';
  if(!sectors.length){ el.innerHTML='<div class="empty"><div class="e-sub">No sector data</div></div>'; return; }
  el.innerHTML = sectors.map(s=>{
    const col = dCol(s.dist_pct);
    const pct = s.dist_pct!=null ? s.dist_pct.toFixed(1)+'%' : '—';
    return `<div class="sc-chip ${s.trending?'tr':''}">
      <div class="sc-chip-name">${s.sector}</div>
      <div class="sc-chip-pct" style="color:${col}">${pct}</div>
    </div>`;
  }).join('');
}

// ──────────────────── HEATMAP ────────────────────
function renderHmap(sectors){
  const el = document.getElementById('hmap');
  if(!sectors.length){ el.innerHTML='<div class="empty" style="grid-column:1/-1"><div class="e-ico">🗺</div><div class="e-txt">No data</div></div>'; return; }
  el.innerHTML = sectors.map(s=>{
    const cls = hmCls(s.dist_pct);
    const pct = s.dist_pct!=null ? s.dist_pct.toFixed(1)+'%' : 'N/A';
    const pr  = s.price ? '₹'+Number(s.price).toLocaleString('en-IN') : '—';
    const btxt = s.trending ? 'Trending' : (s.dist_pct!=null&&s.dist_pct<=15 ? 'In Zone' : 'Out');
    const bbg  = s.trending ? 'rgba(52,211,153,.22)' : (s.dist_pct!=null&&s.dist_pct<=15 ? 'rgba(163,230,53,.16)' : 'rgba(255,255,255,.07)');
    return `<div class="hm-cell ${cls}">
      <div class="hm-badge" style="background:${bbg}">${btxt}</div>
      <div class="hm-name">${s.sector}</div>
      <div class="hm-pct">${pct}</div>
      <div class="hm-sub">CMP ${pr}</div>
    </div>`;
  }).join('');
}

// ─────────────── GAINERS / LOSERS (Sector tab) ───
function renderGL(sectors){
  const rows = sectors
    .filter(s=>s.intraday_chg!=null)
    .map(s=>({sec:s.sector, avg:s.intraday_chg}));
  rows.sort((a,b)=>b.avg-a.avg);
  const maxA = Math.max(...rows.map(r=>Math.abs(r.avg)),0.01);
  const gainers = rows.filter(r=>r.avg>0).slice(0,6);
  const losers  = rows.filter(r=>r.avg<0).reverse().slice(0,6);
  function mkList(items,isG){
    if(!items.length) return '<div class="empty" style="padding:20px"><div class="e-sub">No data</div></div>';
    return items.map((r,i)=>{
      const bw = Math.round(Math.abs(r.avg)/maxA*100);
      const bc = isG?'#34d399':'#f87171';
      return `<div class="gl-row">
        <div class="gl-n">${i+1}</div>
        <div class="gl-name">${r.sec}</div>
        <div class="gl-bar-bg"><div class="gl-bar" style="width:${bw}%;background:${bc}"></div></div>
        <div class="gl-chg" style="color:${bc}">${fmtC(r.avg)}</div>
      </div>`;
    }).join('');
  }
  document.getElementById('gainersBody').innerHTML = mkList(gainers,true);
  document.getElementById('losersBody').innerHTML  = mkList(losers,false);
}

// ─────────────── INTRADAY HEATMAP ────────────────
function renderIntradayHmap(sectors){
  const el = document.getElementById('imap');
  if(!sectors.length){
    el.innerHTML='<div class="empty" style="grid-column:1/-1"><div class="e-ico">📊</div><div class="e-txt">No data yet</div><div class="e-sub">Run a scan first</div></div>';
    return;
  }
  const sorted = [...sectors].sort((a,b)=>(b.intraday_chg||0)-(a.intraday_chg||0));
  el.innerHTML = sorted.map(s=>{
    const chg = s.intraday_chg;
    const col = iColor(chg);
    const bg  = iBg(chg);
    const pct = chg!=null ? (chg>=0?'+':'')+chg.toFixed(2)+'%' : 'N/A';
    const pr  = s.price ? '₹'+Number(s.price).toLocaleString('en-IN') : '—';
    return `<div class="im-cell" style="background:${bg}">
      <div class="im-name" style="color:${col}">${s.sector}</div>
      <div class="im-pct" style="color:${col}">${pct}</div>
      <div class="im-sub" style="color:${col}">${pr}</div>
    </div>`;
  }).join('');
}

// ─────────────── INTRADAY GAINERS/LOSERS ─────────
function renderIntradayGL(stocks){
  document.getElementById('intradayBadge').textContent = stocks.length+' stocks';
  const sorted  = [...stocks].sort((a,b)=>b.intraday_chg-a.intraday_chg);
  const gainers = sorted.filter(s=>s.intraday_chg>0).slice(0,10);
  const losers  = sorted.filter(s=>s.intraday_chg<0).reverse().slice(0,10);
  const maxA = Math.max(...stocks.map(s=>Math.abs(s.intraday_chg||0)),0.01);
  function mkList(items,isG){
    if(!items.length) return '<div class="empty" style="padding:20px"><div class="e-sub">No data</div></div>';
    return items.map((s,i)=>{
      const bw = Math.round(Math.abs(s.intraday_chg)/maxA*100);
      const bc = isG?'#34d399':'#f87171';
      const chgStr = (s.intraday_chg>=0?'+':'')+s.intraday_chg.toFixed(2)+'%';
      return `<div class="gl-row">
        <div class="gl-n">${i+1}</div>
        <div class="gl-name">${s.name}<div style="font-size:10px;color:var(--tx3);margin-top:1px">${s.sector}</div></div>
        <div class="gl-bar-bg"><div class="gl-bar" style="width:${bw}%;background:${bc}"></div></div>
        <div class="gl-chg" style="color:${bc}">${chgStr}</div>
      </div>`;
    }).join('');
  }
  document.getElementById('intradayGainers').innerHTML = mkList(gainers,true);
  document.getElementById('intradayLosers').innerHTML  = mkList(losers,false);
}

// ─────────────── SECTOR CARDS ────────────────────
function renderSecCards(sectors){
  const el = document.getElementById('secCards');
  const t  = sectors.filter(s=>s.trending).length;
  document.getElementById('secDetailBadge').textContent = t+' trending';
  if(!sectors.length){ el.innerHTML='<div class="empty" style="grid-column:1/-1"><div class="e-sub">No data</div></div>'; return; }
  el.innerHTML = sectors.map(s=>{
    const col  = dCol(s.dist_pct);
    const pct  = s.dist_pct!=null ? s.dist_pct.toFixed(1)+'%' : '—';
    const barW = s.dist_pct!=null ? Math.min(s.dist_pct/15*100,100) : 0;
    const athS = s.ath   ? '₹'+Number(s.ath).toLocaleString('en-IN')   : '—';
    const prS  = s.price ? '₹'+Number(s.price).toLocaleString('en-IN') : '—';
    const bcls = (s.trending||(s.dist_pct!=null&&s.dist_pct<=15)) ? 'sbz' : 'sbf';
    const btxt = s.trending ? 'Trending' : (s.dist_pct!=null&&s.dist_pct<=15 ? 'In Zone' : 'Out');
    return `<div class="sec-card ${s.trending?'tr':''}">
      <div class="sctop">
        <div><div class="scname">${s.sector}</div><div class="scsym">${s.symbol}</div></div>
        <span class="scbadge ${bcls}">${btxt}</span>
      </div>
      <div class="scdist" style="color:${col}">${pct}</div>
      <div class="scmeta"><div>ATH <span>${athS}</span></div><div>Now <span>${prS}</span></div></div>
      <div class="dbar">
        <div class="dbar-f" style="width:${barW}%;background:${col}35"></div>
        <div class="dbar-p" style="left:${barW}%;background:${col}"></div>
      </div>
      <div class="dbar-lbl"><span>0%</span><span>5%</span><span>10%</span><span>15%</span></div>
    </div>`;
  }).join('');
}

// ────────────────────── TABLE ────────────────────
function buildFilters(stocks){
  const sects = [...new Set(stocks.map(s=>s.sector))].sort();
  const c = document.getElementById('sfBtns');
  c.innerHTML = `<button class="sf-btn ${activeSector==='all'?'on':''}" data-s="all" onclick="setSF('all',this)">All</button>`;
  sects.forEach(s=>{
    c.innerHTML += `<button class="sf-btn ${activeSector===s?'on':''}" data-s="${s}" onclick="setSF('${s}',this)">${s}</button>`;
  });
}
function setSF(s, btn){
  activeSector = s;
  document.querySelectorAll('.sf-btn').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
  filterTable();
}
function sortData(data){
  return [...data].sort((a,b)=>{
    let av=a[sortCol], bv=b[sortCol];
    if(sortCol==='name'||sortCol==='sector'){
      av=(av||'').toLowerCase(); bv=(bv||'').toLowerCase();
      return sortDir==='asc'?(av<bv?-1:av>bv?1:0):(av>bv?-1:av<bv?1:0);
    }
    if(sortCol==='uptrend'){av=av?1:0;bv=bv?1:0;}
    av=av??99999; bv=bv??99999;
    return sortDir==='asc'?av-bv:bv-av;
  });
}
function filterTable(){
  const q = document.getElementById('searchBox').value.trim().toLowerCase();
  let d = activeSector==='all' ? allStocks : allStocks.filter(s=>s.sector===activeSector);
  if(q) d = d.filter(s=>s.name.toLowerCase().includes(q)||s.sector.toLowerCase().includes(q));
  renderRows(sortData(d));
}
function renderRows(data){
  const tb = document.getElementById('tbody');
  document.getElementById('tblCnt').textContent    = `${data.length} result${data.length!==1?'s':''}`;
  document.getElementById('stockBadge').textContent = `${allStocks.length} results`;
  document.getElementById('signalCnt').textContent  = allStocks.length;
  if(!data.length){
    tb.innerHTML=`<tr><td colspan="10"><div class="empty"><div class="e-ico">🔍</div><div class="e-txt">No stocks matched</div><div class="e-sub">Try a different filter or wait for next scan</div></div></td></tr>`;
    return;
  }
  tb.innerHTML = data.map((s,i)=>{
    const dc  = dClass(s.dist_pct);
    const chC = s.chg_1d>=0 ? 'chg-p' : 'chg-n';
    const vsC = s.vol_surge>=1.5 ? 'vs-h' : 'vs-n';
    const ti  = s.uptrend ? `<span class="tu">▲</span>` : `<span class="td">~</span>`;
    return `<tr>
      <td><span class="td-rank">${i+1}</span></td>
      <td><div class="td-name">${s.name}</div><div class="td-sec">${s.sector}</div></td>
      <td><span style="font-size:11px;font-weight:600;color:var(--tx3)">${s.sector}</span></td>
      <td class="r"><div class="td-price">${fmt(s.price)}</div></td>
      <td class="r"><div class="td-ath">${fmt(s.ath)}</div></td>
      <td class="r"><span class="dp ${dc}">${fmt(s.dist_pct,1)}%</span></td>
      <td class="r"><span class="rp">${fmt(s.range_pct,1)}%</span></td>
      <td class="r"><span class="${chC}">${fmtC(s.chg_1d)}</span></td>
      <td class="r"><span class="${vsC}">${fmt(s.vol_surge,2)}×</span></td>
      <td class="r">${ti}</td>
    </tr>`;
  }).join('');
}
// Sort headers
document.querySelectorAll('thead th[data-col]').forEach(th=>{
  th.addEventListener('click',()=>{
    const col=th.dataset.col;
    if(sortCol===col) sortDir=sortDir==='asc'?'desc':'asc';
    else{sortCol=col;sortDir='asc';}
    document.querySelectorAll('thead th').forEach(h=>h.classList.remove('sort-asc','sort-desc'));
    th.classList.add(sortDir==='asc'?'sort-asc':'sort-desc');
    filterTable();
  });
});

// ──────────────────── STATUS ─────────────────────
function renderStatus(d){
  const map={idle:['Idle','sp-idle'],scanning:['Scanning…','sp-scanning'],done:['Done','sp-done'],error:['Error','sp-error']};
  const [lbl,cls]=map[d.status]||['—','sp-idle'];
  const sp=d.status==='scanning'?'<span class="spin">⟳</span> ':'';
  document.getElementById('statusPill').innerHTML=`<span class="sp ${cls}">${sp}${lbl}</span>`;
  document.getElementById('lastScan').textContent = d.last_scan||'—';
  document.getElementById('nextScan').textContent = d.next_scan||'—';
  document.getElementById('scanCnt').textContent  = d.scan_count||0;
  const b=document.getElementById('mktBadge'), t=document.getElementById('mktTxt');
  if(d.market_open){b.className='mkt-badge open';t.textContent='NSE OPEN';}
  else{b.className='mkt-badge';t.textContent='NSE CLOSED';}
  document.getElementById('scanBtn').disabled = d.status==='scanning';
}

// ───────────────────── LOG ───────────────────────
function renderLog(lines){
  if(!lines||!lines.length) return;
  document.getElementById('logBody').innerHTML = [...lines].reverse().map(l=>{
    let c='ll-d';
    if(l.includes('✅')||l.includes('Done')) c='ll-ok';
    else if(l.includes('⚠')||l.includes('warn')) c='ll-w';
    else if(l.includes('❌')||l.includes('Error')) c='ll-e';
    return `<div class="${c}">${l}</div>`;
  }).join('');
}

// ─────────────────── POLL ────────────────────────
async function fetchData(){
  try{
    const r=await fetch('/api/data'); const d=await r.json();
    renderStatus(d);
    allSectors=d.sectors||[]; allStocks=d.stocks||[]; allIntradayStocks=d.intraday_stocks||[];
    renderStrip(allSectors);
    renderIntradayHmap(allSectors);
    renderIntradayGL(allIntradayStocks);
    buildFilters(allStocks);
    filterTable();
    renderLog(d.log||[]);
  }catch(e){console.error(e);}
}
async function triggerScan(){
  await fetch('/api/scan',{method:'POST'});
  setTimeout(fetchData,500);
}

// ─────────────────── CLOCK ───────────────────────
function updateClock(){
  const ist=new Date(new Date().toLocaleString('en-US',{timeZone:'Asia/Kolkata'}));
  document.getElementById('clock').textContent=ist.toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit',second:'2-digit'})+' IST';
}

// ═══════════════ SETTINGS ════════════════════════
async function loadCfg(){
  try{
    const r=await fetch('/api/settings'); const d=await r.json();
    document.getElementById('ci-client').value  = d.dhan_client_id||'';
    document.getElementById('ci-token').value   = d.dhan_access_token||'';
    document.getElementById('ci-tg-tok').value  = d.telegram_bot_token||'';
    document.getElementById('ci-tg-chat').value = d.telegram_chat_id||'';
    document.getElementById('ci-interval').value= d.scan_interval_minutes||15;
    document.getElementById('ci-ath').value     = d.ath_max_dist_pct||15;
    document.getElementById('ci-range').value   = d.max_range_pct||5;
    document.getElementById('ci-candles').value = d.consol_candles||8;
    document.getElementById('ci-vol').value     = d.min_avg_volume||200000;
    document.getElementById('ci-delay').value   = d.api_call_delay_secs||0.4;
  }catch(e){console.error('Settings load:',e);}
}
function toast(id,msg,ok){
  const el=document.getElementById(id);
  el.textContent=msg; el.className='toast '+(ok?'toast-ok':'toast-err');
  el.style.display='inline-block';
  setTimeout(()=>el.style.display='none',3500);
}
async function post(payload,toastId){
  try{
    const r=await fetch('/api/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});
    const d=await r.json();
    toast(toastId, d.ok?'✓ Saved':'✗ '+(d.error||'Error'), d.ok);
  }catch(e){toast(toastId,'✗ Network error',false);}
}
function saveDhan(){
  post({dhan_client_id:document.getElementById('ci-client').value.trim(),
        dhan_access_token:document.getElementById('ci-token').value.trim()},'t-dhan');
}
function saveTG(){
  post({telegram_bot_token:document.getElementById('ci-tg-tok').value.trim(),
        telegram_chat_id:document.getElementById('ci-tg-chat').value.trim()},'t-tg');
}
async function testTG(){
  const el=document.getElementById('tg-res');
  el.className='tg-res'; el.textContent='Sending…';
  try{
    const r=await fetch('/api/test-telegram',{method:'POST'}); const d=await r.json();
    el.className='tg-res '+(d.ok?'tg-ok':'tg-err');
    el.textContent=d.ok?'✓ Message sent! Check Telegram.':'✗ '+(d.error||'Failed');
  }catch(e){el.className='tg-res tg-err';el.textContent='✗ Network error';}
}
function saveParams(){
  post({
    scan_interval_minutes:parseInt(document.getElementById('ci-interval').value),
    ath_max_dist_pct:parseFloat(document.getElementById('ci-ath').value),
    max_range_pct:parseFloat(document.getElementById('ci-range').value),
    consol_candles:parseInt(document.getElementById('ci-candles').value),
    min_avg_volume:parseInt(document.getElementById('ci-vol').value),
    api_call_delay_secs:parseFloat(document.getElementById('ci-delay').value),
  },'t-params');
}
function togglePw(id,btn){
  const el=document.getElementById(id);
  const s=el.type==='password';
  el.type=s?'text':'password'; btn.textContent=s?'🙈':'👁';
}

// ─────────────────── SCRIP MASTER ───────────────
async function checkScrip(){
  const res=document.getElementById('scrip-result');
  res.style.display='block'; res.textContent='Fetching…';
  try{
    const r=await fetch('/api/scrip-debug'); const d=await r.json();
    const ok=d.stocks_with_id>50;
    const li=d.load_info||{};
    const cv=li.col_values||{};
    let colLines='';
    for(const [col,vals] of Object.entries(cv)){
      colLines+=`  ${col}:\n    ${vals.join(', ')}\n`;
    }
    res.textContent=
      `Equity map : ${d.equity_map_size} entries  |  Index map: ${d.index_map_size} entries\n`+
      `CSV rows   : ${li.csv_rows||'?'}  |  Raw eq matches: ${li.eq_raw_count||'?'}\n`+
      `Stocks with security_id: ${d.stocks_with_id} / ${d.stocks_with_id+d.stocks_missing_id}\n`+
      (d.missing_samples&&d.missing_samples.length?`Missing : ${d.missing_samples.join(', ')}\n`:'')+
      `\nColumn values in CSV:\n${colLines}`+
      `\nSample equity keys: ${(d.sample_equity_keys||[]).join(', ')}`;
    res.style.color=ok?'var(--gr)':'var(--rd)';
    toast('t-scrip', ok?`✓ ${d.stocks_with_id} stocks resolved`:`⚠ Only ${d.stocks_with_id} resolved`, ok);
  }catch(e){res.textContent='Error: '+e; res.style.color='var(--rd)';}
}
async function reloadScrip(){
  const res=document.getElementById('scrip-result');
  toast('t-scrip','Reloading…',true);
  res.style.display='block'; res.textContent='Re-downloading scrip master CSV…';
  try{
    const r=await fetch('/api/reload-scrip',{method:'POST'}); const d=await r.json();
    const ok=d.ok&&d.stocks_with_id>50;
    if(d.ok){
      const li=d.load_info||{};
      const cv=li.col_values||{};
      let colLines='';
      for(const [col,vals] of Object.entries(cv)){
        colLines+=`  ${col}:\n    ${vals.join(', ')}\n`;
      }
      res.textContent=
        `Reload complete.\n`+
        `CSV rows: ${li.csv_rows||'?'}  |  A(FNO): ${li.fno_eq_count||'?'}  |  B(EQ-series): ${li.eq_series_count||'?'}  |  Merged: ${li.eq_merged_count||'?'}\n`+
        `sym_col detected as: "${li.sym_col||'?'}"\n`+
        `Stocks with ID: ${d.stocks_with_id} / ${d.total}\n`+
        (d.missing_sample&&d.missing_sample.length?`Still missing : ${d.missing_sample.join(', ')}\n`:'')+
        `\nSample symbols from CSV equity rows:\n  ${(li.sample_eq_syms||[]).join(', ')}\n`+
        `\nALL CSV columns:\n  ${(li.all_columns||[]).join(', ')}\n`+
        `\nColumn values in CSV:\n${colLines}`;
    }else{
      res.textContent=`Reload failed: ${d.error}`;
    }
    res.style.color=ok?'var(--gr)':'var(--rd)';
    toast('t-scrip', ok?`✓ ${d.stocks_with_id}/${d.total} stocks resolved`:'✗ Reload failed — see details', ok);
  }catch(e){res.textContent='Error: '+e; res.style.color='var(--rd)';}
}

// ─────────────────── BOOT ────────────────────────
setInterval(fetchData,5000); setInterval(updateClock,1000);
fetchData(); updateClock();
</script>
</body>
</html>"""
