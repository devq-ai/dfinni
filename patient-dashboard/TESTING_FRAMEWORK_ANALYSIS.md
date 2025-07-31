# Testing Framework Analysis: Jest vs Vitest for PFINNI Frontend

## Overview
This document analyzes the two main testing framework options for the PFINNI frontend rebuild, comparing Jest and Vitest to determine which provides the most PyTest-like experience.

## Jest

### Pros:
- **Mature and Stable**: Industry standard for React/Next.js testing
- **Excellent Next.js Integration**: Official support and documentation
- **Comprehensive Features**: Mocking, snapshot testing, coverage out-of-box
- **Large Community**: Extensive documentation and community support
- **Good IDE Support**: Excellent debugging and test runner integration

### Cons:
- **Configuration Complexity**: Requires more setup for modern features
- **Performance**: Slower than Vitest, especially in watch mode
- **Module Resolution**: Sometimes struggles with ESM modules

### PyTest Similarity Score: 7/10
- Good fixture support via beforeEach/afterEach
- Parameterized tests available but more verbose
- Less elegant than PyTest's approach

## Vitest

### Pros:
- **Performance**: 10-100x faster than Jest due to Vite integration
- **Modern Design**: Built for ESM-first development
- **PyTest-like Features**:
  - Better fixture system with `beforeEach` hooks
  - More elegant parameterized testing
  - Better async handling
- **Zero Config**: Works out of the box with modern TypeScript/React
- **Compatible API**: Jest-compatible API for easy migration
- **Better Error Messages**: Clearer, more informative test failures

### Cons:
- **Newer**: Less mature ecosystem (but rapidly growing)
- **Next.js Integration**: Requires additional setup for Next.js specific features
- **Smaller Community**: Growing but smaller than Jest

### PyTest Similarity Score: 9/10
- Fixtures feel more natural
- Better parameterized test syntax
- More pythonic API design
- Better test discovery

## Recommendation: Vitest

### Reasoning:
1. **PyTest-like Experience**: Vitest provides a more elegant, PyTest-like testing experience
2. **Performance**: Critical for maintaining 90% coverage requirement - faster feedback loop
3. **Modern Stack**: Aligns with Next.js 15 and modern tooling
4. **Developer Experience**: Better watch mode, clearer errors, faster iteration

### Implementation Plan:
```json
{
  "devDependencies": {
    "vitest": "^2.1.8",
    "@vitejs/plugin-react": "^4.3.4",
    "@testing-library/react": "^16.1.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^14.5.2",
    "@vitest/coverage-v8": "^2.1.8",
    "@vitest/ui": "^2.1.8",
    "jsdom": "^25.0.1"
  }
}
```

### Vitest Configuration:
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/mockData.ts',
        'src/main.tsx',
      ],
      threshold: {
        global: {
          branches: 90,
          functions: 90,
          lines: 90,
          statements: 90
        }
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src')
    }
  }
})
```

### Example Test (PyTest-like):
```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PatientList } from '@/components/PatientList'

describe('PatientList', () => {
  // PyTest-like fixtures
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Parameterized test (PyTest-like)
  it.each([
    { status: 'ACTIVE', expected: 'text-green-500' },
    { status: 'INQUIRY', expected: 'text-yellow-500' },
    { status: 'CHURNED', expected: 'text-red-500' },
  ])('renders patient with $status status correctly', ({ status, expected }) => {
    render(<PatientList patients={[{ id: 1, status }]} />)
    expect(screen.getByText(status)).toHaveClass(expected)
  })

  // Async test with better syntax
  it('loads patients on mount', async () => {
    const { getByTestId } = render(<PatientList />)
    await expect(getByTestId('patient-list')).toBeTruthy()
  })
})
```

## Conclusion
Vitest provides the most PyTest-like experience while offering superior performance and modern features essential for achieving the 90% coverage requirement efficiently.