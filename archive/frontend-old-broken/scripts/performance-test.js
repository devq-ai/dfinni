const puppeteer = require('puppeteer')
const fs = require('fs').promises

const TEST_URL = process.env.TEST_URL || 'http://localhost:3002'
const ITERATIONS = 5

async function measurePageLoad(browser, url) {
  const page = await browser.newPage()
  
  // Enable performance tracking
  await page.evaluateOnNewDocument(() => {
    window.performanceMetrics = {
      firstPaint: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      domContentLoaded: 0,
      loadComplete: 0,
    }
  })

  // Listen for performance metrics
  await page.evaluateOnNewDocument(() => {
    // First Paint & First Contentful Paint
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-paint') {
          window.performanceMetrics.firstPaint = entry.startTime
        }
        if (entry.name === 'first-contentful-paint') {
          window.performanceMetrics.firstContentfulPaint = entry.startTime
        }
      }
    }).observe({ entryTypes: ['paint'] })

    // Largest Contentful Paint
    new PerformanceObserver((list) => {
      const entries = list.getEntries()
      const lastEntry = entries[entries.length - 1]
      window.performanceMetrics.largestContentfulPaint = lastEntry.renderTime || lastEntry.loadTime
    }).observe({ entryTypes: ['largest-contentful-paint'] })

    // DOM Content Loaded
    document.addEventListener('DOMContentLoaded', () => {
      window.performanceMetrics.domContentLoaded = performance.now()
    })

    // Page Load Complete
    window.addEventListener('load', () => {
      window.performanceMetrics.loadComplete = performance.now()
    })
  })

  const startTime = Date.now()
  
  try {
    await page.goto(url, { waitUntil: 'networkidle0' })
    
    // Wait a bit for all metrics to be collected
    await page.waitForTimeout(1000)
    
    // Get performance metrics
    const metrics = await page.evaluate(() => window.performanceMetrics)
    const totalLoadTime = Date.now() - startTime
    
    // Get resource timing
    const resourceTimings = await page.evaluate(() => {
      return performance.getEntriesByType('resource').map(entry => ({
        name: entry.name,
        duration: entry.duration,
        size: entry.transferSize,
        type: entry.initiatorType
      }))
    })
    
    // Get memory usage (Chrome only)
    const memoryUsage = await page.evaluate(() => {
      if (performance.memory) {
        return {
          usedJSHeapSize: performance.memory.usedJSHeapSize,
          totalJSHeapSize: performance.memory.totalJSHeapSize,
          jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
        }
      }
      return null
    })
    
    await page.close()
    
    return {
      url,
      totalLoadTime,
      metrics,
      resourceTimings,
      memoryUsage,
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    await page.close()
    throw error
  }
}

async function runPerformanceTests() {
  console.log(`🚀 Starting performance tests for ${TEST_URL}`)
  console.log(`Running ${ITERATIONS} iterations...\n`)
  
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  })
  
  const results = []
  const pagesToTest = [
    '/',
    '/dashboard',
    '/patients',
    '/alerts',
    '/ai'
  ]
  
  for (const page of pagesToTest) {
    console.log(`Testing ${page}...`)
    const pageResults = []
    
    for (let i = 0; i < ITERATIONS; i++) {
      try {
        const result = await measurePageLoad(browser, `${TEST_URL}${page}`)
        pageResults.push(result)
        console.log(`  Iteration ${i + 1}: ${result.totalLoadTime}ms`)
      } catch (error) {
        console.error(`  Iteration ${i + 1} failed:`, error.message)
      }
    }
    
    // Calculate averages
    const avgMetrics = {
      page,
      iterations: pageResults.length,
      avgTotalLoadTime: pageResults.reduce((sum, r) => sum + r.totalLoadTime, 0) / pageResults.length,
      avgFirstPaint: pageResults.reduce((sum, r) => sum + r.metrics.firstPaint, 0) / pageResults.length,
      avgFirstContentfulPaint: pageResults.reduce((sum, r) => sum + r.metrics.firstContentfulPaint, 0) / pageResults.length,
      avgLargestContentfulPaint: pageResults.reduce((sum, r) => sum + r.metrics.largestContentfulPaint, 0) / pageResults.length,
      avgDomContentLoaded: pageResults.reduce((sum, r) => sum + r.metrics.domContentLoaded, 0) / pageResults.length,
      avgLoadComplete: pageResults.reduce((sum, r) => sum + r.metrics.loadComplete, 0) / pageResults.length,
    }
    
    results.push({
      ...avgMetrics,
      allResults: pageResults
    })
    
    console.log(`  Average load time: ${avgMetrics.avgTotalLoadTime.toFixed(2)}ms`)
    console.log(`  Average LCP: ${avgMetrics.avgLargestContentfulPaint.toFixed(2)}ms\n`)
  }
  
  await browser.close()
  
  // Generate report
  const report = {
    testUrl: TEST_URL,
    timestamp: new Date().toISOString(),
    summary: {
      totalPages: results.length,
      overallAvgLoadTime: results.reduce((sum, r) => sum + r.avgTotalLoadTime, 0) / results.length,
      pagesUnder3s: results.filter(r => r.avgTotalLoadTime < 3000).length,
      slowestPage: results.reduce((slowest, r) => 
        r.avgTotalLoadTime > slowest.avgTotalLoadTime ? r : slowest
      ),
      fastestPage: results.reduce((fastest, r) => 
        r.avgTotalLoadTime < fastest.avgTotalLoadTime ? r : fastest
      )
    },
    results
  }
  
  // Save report
  await fs.writeFile(
    `performance-report-${Date.now()}.json`,
    JSON.stringify(report, null, 2)
  )
  
  // Print summary
  console.log('\n📊 Performance Test Summary:')
  console.log('==========================')
  console.log(`Overall average load time: ${report.summary.overallAvgLoadTime.toFixed(2)}ms`)
  console.log(`Pages under 3s: ${report.summary.pagesUnder3s}/${report.summary.totalPages}`)
  console.log(`Slowest page: ${report.summary.slowestPage.page} (${report.summary.slowestPage.avgTotalLoadTime.toFixed(2)}ms)`)
  console.log(`Fastest page: ${report.summary.fastestPage.page} (${report.summary.fastestPage.avgTotalLoadTime.toFixed(2)}ms)`)
  
  // Check if we meet the < 3s requirement
  const meetsRequirement = report.summary.overallAvgLoadTime < 3000
  console.log(`\n${meetsRequirement ? '✅' : '❌'} ${meetsRequirement ? 'PASSED' : 'FAILED'}: Target < 3s initial load`)
  
  return report
}

// Run the tests
runPerformanceTests()
  .then(() => {
    console.log('\n✨ Performance tests completed!')
    process.exit(0)
  })
  .catch(error => {
    console.error('\n❌ Performance tests failed:', error)
    process.exit(1)
  })