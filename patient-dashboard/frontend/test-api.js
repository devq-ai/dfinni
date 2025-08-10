// Simple Node.js test to verify API calls work
const fetch = require('node-fetch');

async function testAPIs() {
  const API_BASE_URL = 'https://db.devq.ai';
  
  try {
    console.log('Testing dashboard stats API...');
    const response1 = await fetch(`${API_BASE_URL}/api/v1/test-dashboard-stats`, {
      headers: {
        'Content-Type': 'application/json'
      },
    });
    
    if (!response1.ok) {
      console.error('Dashboard stats error:', response1.status, response1.statusText);
      const errorText = await response1.text();
      console.error('Error details:', errorText);
      return;
    }
    
    const dashboardData = await response1.json();
    console.log('Dashboard stats success:', JSON.stringify(dashboardData, null, 2));
    
    console.log('\nTesting alerts stats API...');
    const response2 = await fetch(`${API_BASE_URL}/api/v1/test-alerts-stats`, {
      headers: {
        'Content-Type': 'application/json'
      },
    });
    
    if (!response2.ok) {
      console.error('Alerts stats error:', response2.status, response2.statusText);
      return;
    }
    
    const alertsData = await response2.json();
    console.log('Alerts stats success:', JSON.stringify(alertsData, null, 2));
    
    // Test how frontend would parse the data
    console.log('\n=== Frontend Data Parsing Test ===');
    console.log('Total Patients:', dashboardData.current.totalPatients);
    console.log('Active Patients:', dashboardData.current.activePatients); 
    console.log('High Risk Patients:', dashboardData.current.highRiskPatients);
    
    const alertsTotal = alertsData?.data?.stats?.total || alertsData?.total || 0;
    const alertsList = alertsData?.data?.alerts || alertsData?.alerts || [];
    console.log('Total Alerts:', alertsTotal);
    console.log('Alerts List Length:', alertsList.length);
    
  } catch (error) {
    console.error('Network error:', error.message);
    console.error('Full error:', error);
  }
}

testAPIs();