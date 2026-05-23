import { useState, useEffect } from 'react';

export function useTicketStream() {
  const [tickets, setTickets] = useState([]);
  
  useEffect(() => {
    // Polling simulation for inbox updates
    const interval = setInterval(() => {
      fetch('http://localhost:8000/api/agent/dashboard')
        .then(res => res.json())
        .then(data => setTickets(data.tickets || []))
        .catch(console.error);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return tickets;
}

export function useAnalytics() {
  const [data, setData] = useState(null);
  
  useEffect(() => {
    fetch('http://localhost:8000/api/analytics/sentiment-overview')
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
  }, []);
  
  return data;
}

export function useCRM(customerId) {
  const [profile, setProfile] = useState(null);
  
  useEffect(() => {
    if (!customerId) return;
    fetch(`http://localhost:8000/api/crm/customer/${customerId}`)
      .then(res => res.json())
      .then(setProfile)
      .catch(console.error);
  }, [customerId]);
  
  return profile;
}
