# Pattern 2: Advanced Coverage Strategies

## Problem Statement

Achieving meaningful code coverage requires strategic testing beyond just running tests. You need to identify coverage gaps, prioritize untested code, and systematically improve coverage without wasting effort on low-value tests.

## Key Strategies

### 1. Coverage Gap Analysis

```bash
# Generate detailed coverage report
npm test -- --coverage --coverageReporters=html lcov text

# Open HTML report to visualize gaps
open coverage/lcov-report/index.html
```

### 2. Differential Coverage

```bash
# Check coverage only for changed files
npm test -- --coverage --changedSince=main --collectCoverageFrom='<rootDir>/src/**/*.{js,ts}'
```

### 3. Critical Path Coverage

Focus on high-value code first:

**Priority Order:**
1. Payment processing (95%+ coverage required)
2. Authentication/authorization (90%+)
3. Data validation (85%+)
4. Business logic (80%+)
5. Utility functions (70%+)

### Configuration

```javascript
// jest.config.js
module.exports = {
  coverageThreshold: {
    './src/services/payment/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    },
    './src/services/auth/': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90
    },
    './src/utils/': {
      branches: 70,
      functions: 75,
      lines: 75,
      statements: 75
    }
  }
};
```

## See Also

- [Pattern 3: Continuous Testing Pipeline](pattern-3.md)
- [Core Concepts: Coverage Metrics](../../docs/core-concepts.md#coverage-metrics)
