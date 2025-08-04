# Rate Limiting Documentation

## Overview

The Patient Dashboard API implements comprehensive rate limiting to protect against abuse and ensure fair usage. Rate limiting is implemented using a distributed sliding window algorithm with SurrealDB as the backend storage.

## Features

- **Distributed Rate Limiting**: Works across multiple server instances
- **Sliding Window Algorithm**: Accurate request counting
- **Per-Endpoint Limits**: Different limits for sensitive endpoints
- **Method-Based Limits**: Different limits for GET, POST, PUT, DELETE
- **Informative Headers**: Clients receive rate limit status in response headers
- **Graceful Degradation**: Falls back to allowing requests if rate limiting fails

## Configuration

Rate limiting is configured through environment variables:

```bash
PFINNI_RATE_LIMIT_ENABLED=true          # Enable/disable rate limiting
PFINNI_RATE_LIMIT_REQUESTS=100          # Default requests per window
PFINNI_RATE_LIMIT_WINDOW=60             # Default window in seconds
```

## Rate Limits

### Global Limits (per minute)

- **GET requests**: 100 requests/minute
- **POST requests**: 50 requests/minute
- **PUT requests**: 50 requests/minute
- **DELETE requests**: 20 requests/minute

### Authentication Endpoint Limits

| Endpoint | Limit | Window | Reason |
|----------|-------|---------|---------|
| `/api/v1/auth/login` | 5 | 5 minutes | Prevent brute force attacks |
| `/api/v1/auth/register` | 3 | 1 hour | Prevent spam registrations |
| `/api/v1/auth/forgot-password` | 3 | 1 hour | Prevent email spam |
| `/api/v1/auth/reset-password` | 3 | 1 hour | Prevent token guessing |
| `/api/v1/auth/change-password` | 5 | 1 hour | Prevent unauthorized changes |
| `/api/v1/auth/refresh` | 10 | 5 minutes | Allow reasonable token refresh |

### Exemptions

The following endpoints are exempt from rate limiting:
- `/health` - Health checks
- `/docs` - API documentation
- `/redoc` - API documentation
- `/openapi.json` - OpenAPI specification

## Response Headers

All rate-limited endpoints include the following headers:

```
X-RateLimit-Limit: 100          # Maximum requests allowed
X-RateLimit-Remaining: 45       # Requests remaining in window
X-RateLimit-Reset: 1704067200   # Unix timestamp when window resets
X-RateLimit-Window: 60          # Window duration in seconds
```

## Rate Limit Exceeded Response

When rate limit is exceeded, the API returns:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1704067200
X-RateLimit-Window: 60

{
    "detail": "Rate limit exceeded",
    "error_code": "RATE_LIMIT_EXCEEDED"
}
```

## Implementation Details

### Storage

Rate limit data is stored in SurrealDB with the following structure:

```sql
DEFINE TABLE rate_limit_entry SCHEMALESS;
DEFINE INDEX rate_limit_bucket_idx ON TABLE rate_limit_entry COLUMNS bucket;
DEFINE INDEX rate_limit_timestamp_idx ON TABLE rate_limit_entry COLUMNS timestamp;
```

### Algorithm

The implementation uses a sliding window algorithm:

1. Each request creates an entry with current timestamp
2. Entries older than the window are deleted
3. Current entries are counted
4. Request is allowed if count < limit

### Client Identification

Clients are identified by:
- IP address (from `X-Forwarded-For` header or direct connection)
- Future: Can be extended to use API keys or user IDs

## Best Practices for Clients

1. **Monitor Headers**: Check rate limit headers in responses
2. **Implement Backoff**: When limited, wait until `X-RateLimit-Reset`
3. **Batch Requests**: Combine multiple operations when possible
4. **Cache Responses**: Reduce unnecessary API calls
5. **Use Webhooks**: For real-time updates instead of polling

## Testing

Run the rate limit tests:

```bash
cd backend
python tests/test_rate_limit.py
```

## Monitoring

Rate limit violations are logged with:
- Client identifier
- Endpoint accessed
- Current request count
- Configured limits

Example log entry:
```
WARNING: Endpoint rate limit exceeded
  client_id: ip:192.168.1.100
  endpoint: /api/v1/auth/login
  limit: {"requests": 5, "window": 300}
```

## Future Enhancements

1. **User-Based Limits**: Different limits for authenticated users
2. **Tier-Based Limits**: Different limits based on subscription tier
3. **Dynamic Limits**: Adjust limits based on system load
4. **IP Whitelist**: Exempt trusted IPs from rate limiting
5. **Cost-Based Limiting**: Weight expensive operations differently