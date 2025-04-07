// frontend/src/App.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [latestData, setLatestData] = useState(null);
  const [historyData, setHistoryData] = useState([]);

  // Lấy dữ liệu mới nhất mỗi 2 giây
  useEffect(() => {
    const interval = setInterval(() => {
      axios.get('http://localhost:5000/api/latest')
        .then(response => {
          console.log("Latest data received:", response.data);  // In ra dữ liệu nhận được từ API
          setLatestData(response.data);
        })
        .catch(error => console.error(error));
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Lấy dữ liệu lịch sử khi nhấn nút
  const fetchHistory = () => {
    axios.get('http://localhost:5000/api/history')
      .then(response => setHistoryData(response.data))
      .catch(error => console.error(error));
  };

  // const HistoryDataComponent = () => {
  //   const [historyData, setHistoryData] = useState([]);
  //   const [loading, setLoading] = useState(false);
  
  //   const fetchHistory = async () => {
  //     setLoading(true);
  //     try {
  //       const response = await fetch('/api/history'); // Thay bằng API thực tế của bạn
  //       const data = await response.json();
  //       setHistoryData(data); // Giả sử data là một mảng chứa ít nhất 20 phần tử
  //     } catch (error) {
  //       console.error('Error fetching history:', error);
  //     } finally {
  //       setLoading(false);
  //     }
  //   };

  return (
    <div className="App">
      <h1>ESP32 Data Monitor</h1>
      
      <div>
        <h2>Latest Data</h2>
        {latestData ? (
          <div>
          <p><strong>Timestamp:</strong> {latestData.timestamp}</p>
          <p><strong>Humidity:</strong> {latestData.data.humidity}%</p>
          <p><strong>Temperature:</strong> {latestData.data.temperature}°C</p>
        </div>
        ) : (
          <p>Loading...</p>
        )}
      </div>

      <div id="button">
        <button onClick={fetchHistory}>Load History</button>
      </div>

      <div id="history_container">
        <h2>History Data</h2>
        <p><strong>Timestamp  |  Humidity  |  Temperature:</strong></p>
        {historyData.length > 0 && (
          <ul id="history_list">
            {historyData.map((item, index) => (
              <li key={index}>
                <div> 
                  <p>{item.timestamp} | {item.data.humidity}% | {item.data.temperature}°C</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default App;