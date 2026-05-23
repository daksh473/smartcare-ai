import { useState, useEffect } from "react";
import { Users, Target, Activity, DollarSign, Brain, Search, Plus, Trash2, Calendar, FileText } from "lucide-react";
import "./CrmView.css";

const API = "http://localhost:8000";

const STAGES = ["lead", "qualified", "proposal", "negotiation", "won", "lost"];
const STAGE_LABELS = {
  lead: "Lead", qualified: "Qualified", proposal: "Proposal",
  negotiation: "Negotiation", won: "Won", lost: "Lost"
};

const STATUS_COLORS = {
  lead: { bg: "rgba(59,130,246,0.1)", text: "#3B82F6" },
  prospect: { bg: "rgba(245,166,35,0.1)", text: "#F5A623" },
  customer: { bg: "rgba(48,164,108,0.1)", text: "#30A46C" },
  churned: { bg: "rgba(229,72,77,0.1)", text: "#E5484D" }
};

export default function CrmView() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [deals, setDeals] = useState([]);
  const [pipeline, setPipeline] = useState({});
  const [loading, setLoading] = useState(true);

  // Modals
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const [customerTimeline, setCustomerTimeline] = useState([]);
  const [forecastData, setForecastData] = useState(null);
  const [forecasting, setForecasting] = useState(false);
  const [showAddDeal, setShowAddDeal] = useState(false);
  const [newDeal, setNewDeal] = useState({ title: "", value: 0, stage: "lead", customer_id: "", expected_close: "" });

  const fetchData = async () => {
    try {
      const [stRes, cRes, dRes, pRes] = await Promise.all([
        fetch(`${API}/crm/stats`),
        fetch(`${API}/crm/customers`),
        fetch(`${API}/crm/deals`),
        fetch(`${API}/crm/pipeline`)
      ]);
      setStats(await stRes.json());
      setCustomers(await cRes.json());
      setDeals(await dRes.json());
      setPipeline(await pRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  // Actions
  const handleGenerateForecast = async () => {
    setForecasting(true);
    try {
      const res = await fetch(`${API}/crm/forecast`, { method: "POST" });
      setForecastData(await res.json());
    } catch (e) {
      console.error(e);
    } finally {
      setForecasting(false);
    }
  };

  const openCustomer = async (cust) => {
    setSelectedCustomer(cust);
    try {
      const res = await fetch(`${API}/crm/customers/${cust.id}/timeline`);
      setCustomerTimeline(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const generateRiskScore = async () => {
    if(!selectedCustomer) return;
    try {
      const res = await fetch(`${API}/crm/customers/${selectedCustomer.id}/risk-score`, { method: "POST" });
      const data = await res.json();
      setSelectedCustomer(prev => ({...prev, risk_score: data.risk_score}));
      alert(`AI Risk Analysis:\nScore: ${data.risk_score}\nReason: ${data.reason}\nAction: ${data.recommendation}`);
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const createDeal = async () => {
    try {
      await fetch(`${API}/crm/deals`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({...newDeal, customer_id: parseInt(newDeal.customer_id)})
      });
      setShowAddDeal(false);
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  // Drag and Drop for Kanban
  const handleDragStart = (e, dealId) => {
    e.dataTransfer.setData("dealId", dealId);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (e, stage) => {
    const dealId = e.dataTransfer.getData("dealId");
    if(!dealId) return;
    try {
      await fetch(`${API}/crm/deals/${dealId}`, {
        method: "PUT", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stage })
      });
      fetchData();
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) return <div className="crm-loading">Loading CRM...</div>;

  return (
    <div className="crm-view">
      {/* HEADER NAV */}
      <div className="crm-header">
        <h2 className="crm-title">SmartCare CRM</h2>
        <div className="crm-tabs">
          {["overview", "customers", "pipeline", "deals"].map(t => (
            <button 
              key={t} 
              className={`crm-tab-btn ${activeTab === t ? "active" : ""}`}
              onClick={() => setActiveTab(t)}
            >
              {t.charAt(0).toUpperCase() + t.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="crm-content">
        {/* ================= OVERVIEW TAB ================= */}
        {activeTab === "overview" && stats && (
          <div className="crm-overview animate-in fade-in">
            <div className="crm-kpi-grid">
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-blue"><Users size={18}/></div>
                <div className="kpi-info"><span>Total Customers</span><strong>{stats.total_customers}</strong></div>
              </div>
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-emerald"><Plus size={18}/></div>
                <div className="kpi-info"><span>New This Month</span><strong>{stats.new_this_month}</strong></div>
              </div>
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-purple"><Target size={18}/></div>
                <div className="kpi-info"><span>Pipeline Value</span><strong>${stats.total_deals_value.toLocaleString()}</strong></div>
              </div>
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-green"><DollarSign size={18}/></div>
                <div className="kpi-info"><span>Won Revenue</span><strong>${stats.won_deals_value.toLocaleString()}</strong></div>
              </div>
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-red"><Activity size={18}/></div>
                <div className="kpi-info"><span>At-Risk Customers</span><strong className={stats.at_risk_customers > 0 ? "text-red-500" : ""}>{stats.at_risk_customers}</strong></div>
              </div>
              <div className="crm-kpi-card">
                <div className="kpi-icon bg-yellow"><Activity size={18}/></div>
                <div className="kpi-info"><span>Win Rate</span><strong>{stats.conversion_rate}%</strong></div>
              </div>
            </div>

            <div className="crm-forecast-panel">
              <div className="forecast-header">
                <h3><Brain size={18}/> AI Revenue Forecast</h3>
                <button className="btn-primary" onClick={handleGenerateForecast} disabled={forecasting}>
                  {forecasting ? "Analyzing..." : "Generate AI Forecast"}
                </button>
              </div>
              {forecastData ? (
                <div className="forecast-body">
                  <div className="forecast-bars">
                    <div className="f-bar-wrap">
                      <div className="f-bar" style={{height: '60%'}}></div>
                      <span>30 Days: ${forecastData.forecast["30_days"]}</span>
                    </div>
                    <div className="f-bar-wrap">
                      <div className="f-bar" style={{height: '80%'}}></div>
                      <span>60 Days: ${forecastData.forecast["60_days"]}</span>
                    </div>
                    <div className="f-bar-wrap">
                      <div className="f-bar" style={{height: '100%'}}></div>
                      <span>90 Days: ${forecastData.forecast["90_days"]}</span>
                    </div>
                  </div>
                  <div className="forecast-top-deals">
                    <h4>Top Deals to Focus On</h4>
                    {forecastData.top_deals.map((id, i) => {
                      const d = deals.find(x => x.id === id);
                      return d ? <div key={i} className="f-deal">⭐ {d.title} (${d.value})</div> : null;
                    })}
                  </div>
                </div>
              ) : (
                <div className="forecast-empty">Click generate to let AI analyze your pipeline and predict upcoming revenue.</div>
              )}
            </div>
          </div>
        )}

        {/* ================= CUSTOMERS TAB ================= */}
        {activeTab === "customers" && (
          <div className="crm-table-container animate-in fade-in">
            <div className="crm-table-header">
              <div className="search-box">
                <Search size={16}/> <input type="text" placeholder="Search customers..." />
              </div>
            </div>
            <table className="crm-table">
              <thead>
                <tr>
                  <th>Name</th><th>Company</th><th>Status</th><th>Risk Score</th><th>Avg Sentiment</th><th>Last Contact</th>
                </tr>
              </thead>
              <tbody>
                {customers.map(c => (
                  <tr key={c.id} onClick={() => openCustomer(c)}>
                    <td>
                      <div className="font-semibold text-white">{c.name}</div>
                      <div className="text-xs text-gray-400">{c.email}</div>
                    </td>
                    <td>{c.company || "-"}</td>
                    <td>
                      <span className="crm-badge" style={{background: STATUS_COLORS[c.status]?.bg, color: STATUS_COLORS[c.status]?.text}}>
                        {c.status.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <div className="risk-bar-container">
                        <div className="risk-bar-fill" style={{width: `${c.risk_score * 100}%`, background: c.risk_score < 0.3 ? '#E5484D' : '#30A46C'}}></div>
                      </div>
                    </td>
                    <td>{c.avg_sentiment.toFixed(2)}</td>
                    <td>{new Date(c.last_contact || c.created_at).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ================= PIPELINE (KANBAN) TAB ================= */}
        {activeTab === "pipeline" && (
          <div className="crm-kanban animate-in fade-in">
            {STAGES.map(stage => {
              const colDeals = pipeline[stage]?.deals || [];
              const colValue = pipeline[stage]?.total_value || 0;
              return (
                <div 
                  key={stage} 
                  className="kanban-col"
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, stage)}
                >
                  <div className={`kanban-col-header ${stage}`}>
                    <span className="col-title">{STAGE_LABELS[stage]} ({colDeals.length})</span>
                    <span className="col-val">${colValue.toLocaleString()}</span>
                  </div>
                  <div className="kanban-cards">
                    {colDeals.map(d => (
                      <div 
                        key={d.id} 
                        className="kanban-card"
                        draggable
                        onDragStart={(e) => handleDragStart(e, d.id)}
                      >
                        <div className="k-card-title">{d.title}</div>
                        <div className="k-card-val">${d.value.toLocaleString()}</div>
                        <div className="k-card-cust"><Users size={12}/> {d.customer_name}</div>
                        <div className="k-card-meta">
                          <span>{d.probability}% Prob</span>
                          <span><Calendar size={12}/> {new Date(d.expected_close).toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* ================= DEALS TAB ================= */}
        {activeTab === "deals" && (
          <div className="crm-table-container animate-in fade-in">
            <div className="crm-table-header">
              <h3>All Deals</h3>
              <button className="btn-primary" onClick={() => setShowAddDeal(true)}><Plus size={16}/> Add Deal</button>
            </div>
            <table className="crm-table">
              <thead>
                <tr>
                  <th>Title</th><th>Customer</th><th>Value</th><th>Stage</th><th>Probability</th><th>Expected Close</th>
                </tr>
              </thead>
              <tbody>
                {deals.map(d => (
                  <tr key={d.id}>
                    <td className="font-semibold text-white">{d.title}</td>
                    <td>{d.customer_name}</td>
                    <td>${d.value.toLocaleString()}</td>
                    <td>
                      <span className={`kanban-badge ${d.stage}`}>{STAGE_LABELS[d.stage]}</span>
                    </td>
                    <td>{d.probability}%</td>
                    <td>{new Date(d.expected_close).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* CUSTOMER PROFILE MODAL */}
      {selectedCustomer && (
        <div className="modal-overlay" onClick={() => setSelectedCustomer(null)}>
          <div className="crm-modal profile-modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedCustomer.name}</h2>
              <button className="btn-close" onClick={() => setSelectedCustomer(null)}>×</button>
            </div>
            <div className="modal-body profile-grid">
              <div className="prof-left">
                <div className="prof-card">
                  <h4>Contact Info</h4>
                  <p><strong>Email:</strong> {selectedCustomer.email}</p>
                  <p><strong>Phone:</strong> {selectedCustomer.phone || "N/A"}</p>
                  <p><strong>Company:</strong> {selectedCustomer.company || "N/A"}</p>
                  <p><strong>Source:</strong> {selectedCustomer.source}</p>
                </div>
                <div className="prof-card">
                  <div className="flex-between">
                    <h4>AI Risk Score</h4>
                    <button className="btn-outline-small" onClick={generateRiskScore}><Brain size={12}/> Analyze</button>
                  </div>
                  <div className="risk-display">
                    <div className="risk-num" style={{color: selectedCustomer.risk_score < 0.3 ? '#E5484D' : '#30A46C'}}>
                      {selectedCustomer.risk_score.toFixed(2)}
                    </div>
                  </div>
                </div>
              </div>
              <div className="prof-right">
                <div className="prof-card timeline-card">
                  <h4>Activity Timeline</h4>
                  <div className="timeline">
                    {customerTimeline.map((t, i) => (
                      <div key={i} className="timeline-item">
                        <div className="t-dot"></div>
                        <div className="t-content">
                          <span className="t-time">{new Date(t.created_at).toLocaleString()}</span>
                          <span className="t-type badge-small">{t.type}</span>
                          <p>{t.description}</p>
                          {t.sentiment_score !== null && <span className="t-sent">Sentiment: {t.sentiment_score}</span>}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ADD DEAL MODAL */}
      {showAddDeal && (
        <div className="modal-overlay" onClick={() => setShowAddDeal(false)}>
          <div className="crm-modal" onClick={e => e.stopPropagation()}>
            <h3>New Deal</h3>
            <div className="form-group">
              <label>Customer</label>
              <select value={newDeal.customer_id} onChange={e => setNewDeal({...newDeal, customer_id: e.target.value})}>
                <option value="">Select Customer...</option>
                {customers.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>Deal Title</label>
              <input type="text" value={newDeal.title} onChange={e => setNewDeal({...newDeal, title: e.target.value})} />
            </div>
            <div className="form-group">
              <label>Value ($)</label>
              <input type="number" value={newDeal.value} onChange={e => setNewDeal({...newDeal, value: parseFloat(e.target.value)})} />
            </div>
            <div className="form-group">
              <label>Expected Close</label>
              <input type="date" value={newDeal.expected_close} onChange={e => setNewDeal({...newDeal, expected_close: e.target.value})} />
            </div>
            <div className="modal-actions">
              <button className="btn-outline" onClick={() => setShowAddDeal(false)}>Cancel</button>
              <button className="btn-primary" onClick={createDeal}>Create Deal</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
