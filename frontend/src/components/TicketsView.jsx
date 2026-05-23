import { useState, useEffect } from "react";
import { CheckCircle2, CircleDashed, AlertTriangle, LayoutDashboard } from "lucide-react";

export default function TicketsView() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState({ total: 0, open: 0, resolved: 0, high_priority: 0 });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [tRes, sRes] = await Promise.all([
        fetch("http://localhost:8000/tickets"),
        fetch("http://localhost:8000/tickets/stats")
      ]);
      setTickets(await tRes.json());
      setStats(await sRes.json());
    } catch (err) {
      console.error("Error fetching tickets:", err);
    }
  };

  const resolveTicket = async (id) => {
    try {
      await fetch(`http://localhost:8000/tickets/${id}/resolve`, { method: "PATCH" });
      fetchData(); // refresh
    } catch (err) {
      console.error("Error resolving ticket:", err);
    }
  };

  const priorityColor = (p) => {
    if (p === "HIGH") return "text-red-400 bg-red-400/10 border-red-400/20";
    if (p === "MEDIUM") return "text-yellow-400 bg-yellow-400/10 border-yellow-400/20";
    return "text-emerald-400 bg-emerald-400/10 border-emerald-400/20";
  };

  return (
    <div className="w-full h-full flex flex-col p-6 bg-[#1a1b1f] overflow-y-auto text-white">
      
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold flex items-center gap-2">
            <LayoutDashboard size={20} /> Tickets Management
          </h2>
          <p className="text-xs text-gray-500 mt-1">Manage and resolve auto-escalated issues</p>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-[#232323] border border-gray-800 p-4 rounded-xl flex flex-col justify-center">
          <div className="text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">Total Tickets</div>
          <div className="text-2xl font-mono">{stats.total}</div>
        </div>
        <div className="bg-[#232323] border border-gray-800 p-4 rounded-xl flex flex-col justify-center">
          <div className="text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">Open Tickets</div>
          <div className="text-2xl font-mono text-yellow-400">{stats.open}</div>
        </div>
        <div className="bg-[#232323] border border-gray-800 p-4 rounded-xl flex flex-col justify-center">
          <div className="text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">Resolved</div>
          <div className="text-2xl font-mono text-emerald-400">{stats.resolved}</div>
        </div>
        <div className="bg-red-500/10 border border-red-500/20 p-4 rounded-xl flex flex-col justify-center">
          <div className="text-red-400/80 text-xs font-bold uppercase tracking-wide mb-1">High Priority</div>
          <div className="text-2xl font-mono text-red-400">{stats.high_priority}</div>
        </div>
      </div>

      {/* Tickets Table */}
      <div className="bg-[#232323] border border-gray-800 rounded-xl overflow-hidden flex-1">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="bg-[#191919] border-b border-gray-800">
              <th className="p-4 font-semibold text-gray-400 w-16">ID</th>
              <th className="p-4 font-semibold text-gray-400">Customer / Session</th>
              <th className="p-4 font-semibold text-gray-400 w-1/3">Issue / Message</th>
              <th className="p-4 font-semibold text-gray-400">Priority</th>
              <th className="p-4 font-semibold text-gray-400">Status</th>
              <th className="p-4 font-semibold text-gray-400 text-right">Action</th>
            </tr>
          </thead>
          <tbody>
            {tickets.length === 0 ? (
              <tr>
                <td colSpan="6" className="p-8 text-center text-gray-500">No tickets found</td>
              </tr>
            ) : (
              tickets.map(t => (
                <tr key={t.id} className="border-b border-gray-800 hover:bg-white/5 transition-colors">
                  <td className="p-4 text-gray-500">#{t.id}</td>
                  <td className="p-4">{t.customer_name}</td>
                  <td className="p-4 text-gray-400">{t.issue}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-[10px] font-bold border uppercase tracking-wider ${priorityColor(t.priority)}`}>
                      {t.priority}
                    </span>
                  </td>
                  <td className="p-4">
                    {t.status === "OPEN" ? (
                      <span className="flex items-center gap-1 text-yellow-400 text-xs"><CircleDashed size={14}/> Open</span>
                    ) : (
                      <span className="flex items-center gap-1 text-emerald-400 text-xs"><CheckCircle2 size={14}/> Resolved</span>
                    )}
                  </td>
                  <td className="p-4 text-right">
                    {t.status === "OPEN" && (
                      <button 
                        onClick={() => resolveTicket(t.id)}
                        className="px-3 py-1 bg-white/10 hover:bg-white/20 rounded text-xs transition-colors"
                      >
                        Resolve
                      </button>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
