#!/usr/bin/env node
import { exec } from 'child_process'
import { promisify } from 'util'
import chalk from 'chalk'

const execAsync = promisify(exec)

interface TestSuite {
  name: string
  pattern: string
  threshold: number
}

const testSuites: TestSuite[] = [
  {
    name: 'Unit Tests',
    pattern: 'src/**/*.test.{ts,tsx}',
    threshold: 90
  },
  {
    name: 'Integration Tests',
    pattern: 'src/test/integration/**/*.test.{ts,tsx}',
    threshold: 85
  },
  {
    name: 'Performance Tests',
    pattern: 'src/test/performance/**/*.test.{ts,tsx}',
    threshold: 80
  },
  {
    name: 'Accessibility Tests',
    pattern: 'src/test/accessibility/**/*.test.{ts,tsx}',
    threshold: 95
  }
]

async function runTestSuite(suite: TestSuite) {
  console.log(chalk.blue(`\n🧪 Running ${suite.name}...\n`))
  
  try {
    const command = `npm test -- ${suite.pattern} --coverage --coverage.enabled --coverage.reporter=json-summary`
    const { stdout, stderr } = await execAsync(command)
    
    console.log(stdout)
    if (stderr) console.error(chalk.yellow(stderr))
    
    // Check coverage threshold
    try {
      const coverageData = require('../coverage/coverage-summary.json')
      const statements = coverageData.total.statements.pct
      
      if (statements < suite.threshold) {
        console.log(chalk.red(`❌ Coverage below threshold: ${statements}% < ${suite.threshold}%`))
        return false
      } else {
        console.log(chalk.green(`✅ Coverage passed: ${statements}% >= ${suite.threshold}%`))
      }
    } catch (e) {
      console.log(chalk.yellow('⚠️  Could not read coverage data'))
    }
    
    return true
  } catch (error) {
    console.error(chalk.red(`❌ ${suite.name} failed:`), error)
    return false
  }
}

async function runAllTests() {
  console.log(chalk.bold.green('🚀 Running Comprehensive Test Suite\n'))
  
  const results: Record<string, boolean> = {}
  
  // Run each test suite
  for (const suite of testSuites) {
    results[suite.name] = await runTestSuite(suite)
  }
  
  // Generate overall coverage report
  console.log(chalk.blue('\n📊 Generating coverage report...\n'))
  try {
    await execAsync('npm test -- --coverage --coverage.enabled --coverage.reporter=html --coverage.reporter=text')
    console.log(chalk.green('✅ Coverage report generated in coverage/'))
  } catch (error) {
    console.error(chalk.red('❌ Failed to generate coverage report'))
  }
  
  // Summary
  console.log(chalk.bold.blue('\n📋 Test Summary:\n'))
  
  let allPassed = true
  for (const [name, passed] of Object.entries(results)) {
    const icon = passed ? '✅' : '❌'
    const color = passed ? chalk.green : chalk.red
    console.log(color(`${icon} ${name}: ${passed ? 'PASSED' : 'FAILED'}`))
    if (!passed) allPassed = false
  }
  
  // Exit with appropriate code
  if (allPassed) {
    console.log(chalk.bold.green('\n🎉 All tests passed!\n'))
    process.exit(0)
  } else {
    console.log(chalk.bold.red('\n💥 Some tests failed!\n'))
    process.exit(1)
  }
}

// Run tests
runAllTests().catch(error => {
  console.error(chalk.red('Fatal error:'), error)
  process.exit(1)
})