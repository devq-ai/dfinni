'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'
import { useDashboardStore } from '@/stores/dashboard-store'
import { logger } from '@/lib/logfire'

const COLORS = {
  inquiry: '#eab308',    // yellow-500
  onboarding: '#3b82f6', // blue-500
  active: '#22c55e',     // green-500
  churned: '#ef4444',    // red-500
}

export function StatusDistributionChart() {
  const { metrics } = useDashboardStore()

  if (!metrics) {
    return (
      <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6 h-[400px]">
        <h3 className="text-lg font-semibold text-zinc-100 mb-4">Patient Status Distribution</h3>
        <div className="flex items-center justify-center h-[320px]">
          <div className="animate-pulse">
            <div className="w-64 h-64 bg-zinc-800 rounded-full" />
          </div>
        </div>
      </div>
    )
  }

  const data = [
    { name: 'Inquiry', value: metrics.statusDistribution.inquiry, color: COLORS.inquiry },
    { name: 'Onboarding', value: metrics.statusDistribution.onboarding, color: COLORS.onboarding },
    { name: 'Active', value: metrics.statusDistribution.active, color: COLORS.active },
    { name: 'Churned', value: metrics.statusDistribution.churned, color: COLORS.churned },
  ].filter(item => item.value > 0)

  const handlePieClick = (data: any) => {
    logger.userAction('status_chart_segment_click', { 
      status: data.name.toLowerCase(),
      value: data.value 
    })
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0]
      const total = metrics.totalPatients
      const percentage = total > 0 ? ((data.value / total) * 100).toFixed(1) : '0'
      
      return (
        <div className="bg-zinc-800 border border-zinc-700 rounded-lg p-3 shadow-lg">
          <p className="text-zinc-100 font-medium">{data.name}</p>
          <p className="text-zinc-400 text-sm">
            {data.value} patients ({percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, value, index }: any) => {
    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)
    
    const total = metrics.totalPatients
    const percentage = total > 0 ? ((value / total) * 100).toFixed(0) : '0'

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        className="text-sm font-medium"
      >
        {`${percentage}%`}
      </text>
    )
  }

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-zinc-100 mb-4">Patient Status Distribution</h3>
      
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="value"
            onClick={handlePieClick}
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.color}
                className="hover:opacity-80 transition-opacity cursor-pointer"
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            iconType="circle"
            formatter={(value) => (
              <span className="text-zinc-300 text-sm">{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-2 gap-4">
        {data.map((item) => (
          <div key={item.name} className="flex items-center space-x-2">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: item.color }}
            />
            <span className="text-sm text-zinc-400">
              {item.name}: {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}