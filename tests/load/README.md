# Load Testing with K6

This directory contains K6 load tests for BARQ Fleet Management system.

## Prerequisites

Install K6:

```bash
# macOS
brew install k6

# Linux
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Windows
choco install k6
```

## Available Tests

### 1. API Load Test (`api-load-test.js`)

Tests core API endpoints under varying load conditions.

**Run:**
```bash
k6 run tests/load/api-load-test.js
```

**With custom base URL:**
```bash
k6 run -e BASE_URL=https://api.barq.com tests/load/api-load-test.js
```

**Test Profile:**
- Ramp up: 20 → 50 → 100 users
- Duration: ~7 minutes
- Endpoints tested: Auth, Couriers, Vehicles, Workflows, Dashboard, Search

**Thresholds:**
- p95 response time < 500ms
- p99 response time < 1000ms
- Error rate < 1%

### 2. Workflow Load Test (`workflow-load-test.js`)

Tests workflow operations including creation and approvals.

**Run:**
```bash
k6 run tests/load/workflow-load-test.js
```

**Test Profile:**
- Users: 30 concurrent
- Duration: ~4.5 minutes
- Operations: Create workflow, Approve, List

**Thresholds:**
- p95 response time < 1000ms
- Error rate < 2%

### 3. Concurrent Users Test (`concurrent-users-test.js`)

Simulates realistic user behavior patterns throughout the day.

**Run:**
```bash
k6 run tests/load/concurrent-users-test.js
```

**Test Profile:**
- Peak users: 150 concurrent
- Duration: ~17 minutes
- Scenarios: Dashboard viewer, Courier manager, Fleet supervisor, HR officer, Workflow approver

**Thresholds:**
- p95 response time < 500ms
- Error rate < 1%

## Running All Tests

```bash
#!/bin/bash
# Run all load tests sequentially

echo "Running API Load Test..."
k6 run tests/load/api-load-test.js

echo "Running Workflow Load Test..."
k6 run tests/load/workflow-load-test.js

echo "Running Concurrent Users Test..."
k6 run tests/load/concurrent-users-test.js
```

## Output Files

Tests generate the following outputs:

- `load-test-summary.json` - Detailed metrics in JSON format
- Console output with real-time metrics

## Interpreting Results

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| http_req_duration (p95) | 95% of requests completed within | < 500ms |
| http_req_duration (p99) | 99% of requests completed within | < 1000ms |
| http_req_failed | Percentage of failed requests | < 1% |
| vus_max | Peak virtual users | As configured |

### Success Criteria

✅ **Pass:** All thresholds met
⚠️ **Warning:** Some thresholds exceeded by < 20%
❌ **Fail:** Thresholds exceeded by > 20%

## Customization

### Adjust Load Profile

Edit the `stages` in `options`:

```javascript
export const options = {
  stages: [
    { duration: '1m', target: 50 },   // Adjust users and duration
    { duration: '5m', target: 100 },
    { duration: '1m', target: 0 },
  ],
}
```

### Adjust Thresholds

```javascript
thresholds: {
  http_req_duration: ['p(95)<300'],  // Stricter: 300ms
  http_req_failed: ['rate<0.005'],   // Stricter: 0.5%
}
```

### Cloud Execution

Run tests in K6 Cloud:

```bash
k6 cloud tests/load/api-load-test.js
```

## CI/CD Integration

Add to your pipeline:

```yaml
load-test:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v3
    - name: Install K6
      run: |
        sudo gpg -k
        curl -s https://dl.k6.io/key.gpg | sudo apt-key add -
        sudo apt-get update
        sudo apt-get install k6
    - name: Run load tests
      run: k6 run tests/load/api-load-test.js
```

## Best Practices

1. **Start Small:** Begin with lower VU counts and gradually increase
2. **Test Production-like:** Use staging environment with production-like data
3. **Monitor:** Watch server metrics (CPU, memory, DB) during tests
4. **Baseline:** Establish baseline metrics before optimizations
5. **Schedule:** Run regularly (daily/weekly) to catch regressions

## Troubleshooting

### High Error Rates

- Check server logs for errors
- Verify API endpoints are correct
- Ensure test data is valid
- Check authentication tokens

### Slow Response Times

- Monitor database query performance
- Check network latency
- Review application logs
- Verify server resources (CPU, memory)

### Connection Errors

- Verify BASE_URL is correct
- Check firewall/network settings
- Ensure services are running
- Test with single VU first

## Additional Resources

- [K6 Documentation](https://k6.io/docs/)
- [K6 Examples](https://k6.io/docs/examples/)
- [Performance Testing Guide](https://k6.io/docs/testing-guides/)
