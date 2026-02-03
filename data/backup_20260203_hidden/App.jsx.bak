import React, { useState, useEffect, useRef } from 'react';

const tg = window.Telegram?.WebApp;

// Получаем API URL из параметра (для PROD/DEV)
const API_PATH = new URLSearchParams(window.location.search).get('env') === 'dev' ? '/api-dev' : '/api';

const formatPrice = (p) => p >= 1e6 ? `${(p/1e6).toFixed(1)} млн` : `${Math.round(p/1e3)} тыс`;
const shortPrice = (p) => p >= 1e6 ? `${(p/1e6).toFixed(1)}` : `${Math.round(p/1e3)}т`;

export default function App() {
  const [lots, setLots] = useState([]);
  const [stats, setStats] = useState({available:0,booked:0,sold:0,total:0});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sending, setSending] = useState(false);
  const [building, setBuilding] = useState(1);
  const [floor, setFloor] = useState(null);
  const [lot, setLot] = useState(null);
  const [filter, setFilter] = useState('all');
  
  const lotRef = useRef(lot);
  useEffect(() => { lotRef.current = lot; }, [lot]);

  useEffect(() => { 
    tg?.ready(); 
    tg?.expand(); 
  }, []);
  
  const sendToBot = () => {
    const currentLot = lotRef.current;
    if (!currentLot || sending) return;
    
    setSending(true);
    
    const payload = {
      lot: {
        code: currentLot.code,
        building: currentLot.building,
        floor: currentLot.floor,
        price: currentLot.price,
        area: currentLot.area
      },
      user_id: tg?.initDataUnsafe?.user?.id
    };
    
    fetch(API_PATH + '/miniapp-action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    }).catch(() => {});
    
    setTimeout(() => {
      try { tg?.close(); } catch(e) {}
    }, 100);
  };
  
  useEffect(() => {
    if (!tg) return;
    tg.MainButton.onClick(sendToBot);
    return () => tg.MainButton.offClick(sendToBot);
  }, []);
  
  useEffect(() => {
    if (!tg) return;
    
    if (lot && !sending) {
      tg.MainButton.setText('✓ В работу');
      tg.MainButton.show();
      tg.MainButton.enable();
    } else if (sending) {
      tg.MainButton.setText('⏳ Отправка...');
      tg.MainButton.disable();
    } else {
      tg.MainButton.hide();
    }
  }, [lot, sending]);
  
  // Загрузка с retry
  useEffect(() => {
    let retries = 3;
    
    const fetchLots = async () => {
      while (retries > 0) {
        try {
          const response = await fetch('/api/lots', { 
            cache: 'no-store',
            headers: { 'Cache-Control': 'no-cache' }
          });
          if (!response.ok) throw new Error('HTTP ' + response.status);
          const d = await response.json();
          if (d.ok && d.lots?.length > 0) {
            setLots(d.lots);
            setStats(d.stats);
            setLoading(false);
            return;
          }
          throw new Error('Empty response');
        } catch (e) {
          retries--;
          if (retries > 0) {
            await new Promise(r => setTimeout(r, 1000));
          } else {
            setError(e.message);
            setLoading(false);
          }
        }
      }
    };
    
    fetchLots();
  }, []);

  const bLots = lots.filter(l => l.building === building);
  const floors = [...new Set(bLots.map(l => l.floor))].sort((a,b) => b-a);
  const fLots = (f) => {
    let fl = bLots.filter(l => l.floor === f).sort((a, b) => a.area - b.area);
    return filter === 'all' ? fl : fl.filter(l => l.status === filter);
  };
  const bStats = {
    available: bLots.filter(l => l.status === 'available').length,
    booked: bLots.filter(l => l.status === 'booked').length,
    sold: bLots.filter(l => l.status === 'sold').length,
  };

  const color = (s) => s === 'available' ? 'bg-emerald-500' : s === 'booked' ? 'bg-amber-500' : 'bg-gray-500';

  if (loading) return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white">
      <div className="w-10 h-10 border-4 border-amber-500 border-t-transparent rounded-full animate-spin mb-4"/>
      <p>Загрузка лотов...</p>
    </div>
  );

  if (error) return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center text-white p-4">
      <p className="text-red-400 mb-2">❌ Ошибка загрузки</p>
      <p className="text-slate-400 text-sm mb-4">{error}</p>
      <button onClick={() => window.location.reload()} className="bg-amber-500 text-black px-4 py-2 rounded-lg">
        Повторить
      </button>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white pb-20">
      <div className="bg-amber-500 px-4 py-3 flex justify-between items-center sticky top-0 z-40">
        <div><h1 className="font-bold">RIZALTA</h1><p className="text-xs text-amber-100">Выбор лота</p></div>
        <div className="text-right"><p className="text-2xl font-bold">{stats.available}</p><p className="text-xs text-amber-100">свободно</p></div>
      </div>

      <div className="flex border-b border-slate-700 sticky top-12 z-30 bg-slate-900">
        {[1,2].map(b => (
          <button key={b} onClick={() => {setBuilding(b);setLot(null);setFloor(null)}}
            className={`flex-1 py-3 ${building===b ? 'text-amber-400 border-b-2 border-amber-400 bg-slate-800' : 'text-slate-400'}`}>
            Корпус {b}<span className="block text-xs opacity-70">{b===1?'Family':'Business'}</span>
          </button>
        ))}
      </div>

      <div className="flex gap-2 p-2 overflow-x-auto sticky top-24 z-20 bg-slate-900">
        {[{k:'all',l:'Все',c:bLots.length,i:'📋'},{k:'available',l:'Свободно',c:bStats.available,i:'🟢'},{k:'booked',l:'Бронь',c:bStats.booked,i:'🟡'},{k:'sold',l:'Продано',c:bStats.sold,i:'⚫'}].map(f => (
          <button key={f.k} onClick={() => setFilter(f.k)}
            className={`px-3 py-1 rounded-full text-xs whitespace-nowrap ${filter===f.k ? 'bg-amber-500 text-black' : 'bg-slate-700 text-slate-300'}`}>
            {f.i} {f.l} ({f.c})
          </button>
        ))}
      </div>

      {lot && (
        <div className="mx-2 mb-2 p-3 bg-slate-800 border border-amber-500 rounded-xl">
          <div className="flex gap-3">
            {lot.layout_url ? (
              <div className="w-24 h-24 flex-shrink-0 bg-white rounded-lg overflow-hidden">
                <img src={lot.layout_url} alt="План" className="w-full h-full object-contain"/>
              </div>
            ) : (
              <div className="w-24 h-24 flex-shrink-0 bg-slate-700 rounded-lg flex items-center justify-center">
                <span className="text-slate-500 text-xs">Нет плана</span>
              </div>
            )}
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-amber-400 font-bold text-xl">{lot.code}</span>
                  <span className={`px-2 py-0.5 rounded text-xs text-white ${color(lot.status)}`}>
                    {lot.status === 'available' ? '✓' : lot.status === 'booked' ? '◐' : '✕'}
                  </span>
                </div>
                <button onClick={() => setLot(null)} className="text-slate-400 text-lg">✕</button>
              </div>
              
              <p className="text-slate-400 text-sm mt-1">
                Корпус {lot.building} ({lot.building === 1 ? 'Family' : 'Business'}) • {lot.floor} этаж
              </p>
              
              <div className="flex justify-between mt-2">
                <div>
                  <p className="text-slate-500 text-xs">Площадь</p>
                  <p className="text-white font-semibold">{lot.area} м²</p>
                </div>
                <div className="text-right">
                  <p className="text-slate-500 text-xs">Стоимость</p>
                  <p className="text-amber-400 font-bold">{formatPrice(lot.price)} ₽</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="p-2 space-y-2">
        {floors.map(f => {
          const fl = fLots(f);
          const all = bLots.filter(l => l.floor === f);
          const avail = all.filter(l => l.status === 'available');
          const minP = avail.length ? Math.min(...avail.map(l=>l.price)) : Math.min(...all.map(l=>l.price));
          const open = floor === f;
          if (!fl.length && filter !== 'all') return null;
          return (
            <div key={f} className="bg-slate-800 rounded-xl">
              <button onClick={() => setFloor(open ? null : f)} className="w-full flex items-center justify-between p-3">
                <div className="flex items-center gap-3">
                  <span className="w-9 h-9 bg-slate-700 rounded-lg flex items-center justify-center font-bold text-amber-400">{f}</span>
                  <div className="text-left">
                    <p className="font-medium">{f} этаж</p>
                    <p className="text-xs text-slate-400"><span className="text-emerald-400">{avail.length}</span> / {all.length}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <p className="text-amber-400 font-medium">от {formatPrice(minP)}</p>
                  <span className={`text-slate-500 transition-transform ${open ? 'rotate-180' : ''}`}>▼</span>
                </div>
              </button>
              {open && fl.length > 0 && (
                <div className="p-2 pt-0 grid grid-cols-4 gap-1.5">
                  {fl.map(l => (
                    <button key={l.code} onClick={() => l.status !== 'sold' && setLot(l)}
                      disabled={l.status === 'sold'}
                      className={`rounded-lg p-1.5 flex flex-col items-center justify-center border-2
                        ${color(l.status)} ${l.status === 'sold' ? 'opacity-40' : ''} 
                        ${lot?.code === l.code ? 'border-white scale-105' : 'border-transparent'}`}>
                      <span className="text-white font-bold text-sm">{l.area} м²</span>
                      <span className="text-white/80 text-xs font-medium">{shortPrice(l.price)} млн</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
