# Example 3: Mock and Stub Usage

## Problem Statement

Your code depends on external services (APIs, databases, file systems) that are slow, expensive, or unreliable in tests. You need to isolate your code and test it independently without actual external dependencies.

## Use Case

Use mocks and stubs when testing code that:
- Makes HTTP API calls
- Interacts with third-party services (payment gateways, email services)
- Accesses file systems
- Has time-dependent behavior
- Requires expensive resources

## Solution Overview

We'll demonstrate comprehensive mocking strategies including:
1. Mocking external API calls
2. Stubbing return values
3. Verifying function calls and arguments
4. Mocking time-dependent code
5. Creating custom test doubles

## Complete Code

### JavaScript (Jest) - API Service Testing

```javascript
// paymentService.js
import axios from 'axios';
import { EmailService } from './emailService';
import { Logger } from './logger';

export class PaymentService {
  constructor(apiKey, emailService, logger) {
    this.apiKey = apiKey;
    this.emailService = emailService;
    this.logger = logger;
  }

  async processPayment(amount, cardToken) {
    try {
      this.logger.info(`Processing payment of $${amount}`);

      // Call external payment API
      const response = await axios.post(
        'https://api.payment-gateway.com/charge',
        {
          amount,
          currency: 'USD',
          source: cardToken
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`
          }
        }
      );

      if (response.data.success) {
        this.logger.info(`Payment successful: ${response.data.transactionId}`);

        // Send confirmation email
        await this.emailService.sendEmail(
          'customer@example.com',
          'Payment Confirmation',
          `Your payment of $${amount} was successful.`
        );

        return {
          success: true,
          transactionId: response.data.transactionId,
          amount
        };
      }

      throw new Error('Payment failed');
    } catch (error) {
      this.logger.error(`Payment error: ${error.message}`);
      throw error;
    }
  }

  async refundPayment(transactionId) {
    this.logger.info(`Refunding transaction ${transactionId}`);

    const response = await axios.post(
      `https://api.payment-gateway.com/refund/${transactionId}`,
      {},
      {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      }
    );

    return {
      success: response.data.success,
      refundId: response.data.refundId
    };
  }
}
```

```javascript
// paymentService.test.js
import axios from 'axios';
import { PaymentService } from './paymentService';
import { EmailService } from './emailService';
import { Logger } from './logger';

// Mock axios module
jest.mock('axios');

describe('PaymentService', () => {
  let paymentService;
  let mockEmailService;
  let mockLogger;

  beforeEach(() => {
    // Create mock dependencies
    mockEmailService = {
      sendEmail: jest.fn().mockResolvedValue(true)
    };

    mockLogger = {
      info: jest.fn(),
      error: jest.fn()
    };

    // Reset axios mocks
    jest.clearAllMocks();

    paymentService = new PaymentService(
      'test-api-key',
      mockEmailService,
      mockLogger
    );
  });

  describe('processPayment', () => {
    test('should process successful payment', async () => {
      // Arrange: Mock successful API response
      axios.post.mockResolvedValue({
        data: {
          success: true,
          transactionId: 'txn_12345'
        }
      });

      // Act
      const result = await paymentService.processPayment(100, 'tok_visa');

      // Assert: Verify API was called correctly
      expect(axios.post).toHaveBeenCalledWith(
        'https://api.payment-gateway.com/charge',
        {
          amount: 100,
          currency: 'USD',
          source: 'tok_visa'
        },
        {
          headers: {
            'Authorization': 'Bearer test-api-key'
          }
        }
      );

      // Assert: Verify email was sent
      expect(mockEmailService.sendEmail).toHaveBeenCalledWith(
        'customer@example.com',
        'Payment Confirmation',
        'Your payment of $100 was successful.'
      );

      // Assert: Verify logging
      expect(mockLogger.info).toHaveBeenCalledWith('Processing payment of $100');
      expect(mockLogger.info).toHaveBeenCalledWith('Payment successful: txn_12345');

      // Assert: Verify result
      expect(result).toEqual({
        success: true,
        transactionId: 'txn_12345',
        amount: 100
      });
    });

    test('should handle payment failure', async () => {
      // Arrange: Mock failed API response
      axios.post.mockRejectedValue(new Error('Insufficient funds'));

      // Act & Assert
      await expect(
        paymentService.processPayment(100, 'tok_visa')
      ).rejects.toThrow('Insufficient funds');

      // Verify error was logged
      expect(mockLogger.error).toHaveBeenCalledWith(
        'Payment error: Insufficient funds'
      );

      // Verify email was not sent
      expect(mockEmailService.sendEmail).not.toHaveBeenCalled();
    });

    test('should handle email service failure gracefully', async () => {
      // Arrange: Payment succeeds but email fails
      axios.post.mockResolvedValue({
        data: {
          success: true,
          transactionId: 'txn_67890'
        }
      });

      mockEmailService.sendEmail.mockRejectedValue(
        new Error('Email service unavailable')
      );

      // Act & Assert
      await expect(
        paymentService.processPayment(50, 'tok_mastercard')
      ).rejects.toThrow('Email service unavailable');
    });
  });

  describe('refundPayment', () => {
    test('should process refund successfully', async () => {
      axios.post.mockResolvedValue({
        data: {
          success: true,
          refundId: 'ref_12345'
        }
      });

      const result = await paymentService.refundPayment('txn_12345');

      expect(axios.post).toHaveBeenCalledWith(
        'https://api.payment-gateway.com/refund/txn_12345',
        {},
        {
          headers: {
            'Authorization': 'Bearer test-api-key'
          }
        }
      );

      expect(result).toEqual({
        success: true,
        refundId: 'ref_12345'
      });

      expect(mockLogger.info).toHaveBeenCalledWith(
        'Refunding transaction txn_12345'
      );
    });
  });
});
```

### Time-Dependent Code Mocking

```javascript
// scheduler.js
export class Scheduler {
  scheduleTask(callback, delayMs) {
    return setTimeout(callback, delayMs);
  }

  scheduleRecurring(callback, intervalMs) {
    return setInterval(callback, intervalMs);
  }

  getCurrentTimestamp() {
    return Date.now();
  }

  isBusinessHours() {
    const hour = new Date().getHours();
    return hour >= 9 && hour < 17;
  }
}
```

```javascript
// scheduler.test.js
import { Scheduler } from './scheduler';

describe('Scheduler', () => {
  let scheduler;

  beforeEach(() => {
    scheduler = new Scheduler();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  describe('scheduleTask', () => {
    test('should call callback after delay', () => {
      const callback = jest.fn();

      scheduler.scheduleTask(callback, 1000);

      expect(callback).not.toHaveBeenCalled();

      // Fast-forward time
      jest.advanceTimersByTime(1000);

      expect(callback).toHaveBeenCalledTimes(1);
    });

    test('should not call callback before delay', () => {
      const callback = jest.fn();

      scheduler.scheduleTask(callback, 5000);

      jest.advanceTimersByTime(4999);
      expect(callback).not.toHaveBeenCalled();

      jest.advanceTimersByTime(1);
      expect(callback).toHaveBeenCalledTimes(1);
    });
  });

  describe('scheduleRecurring', () => {
    test('should call callback multiple times', () => {
      const callback = jest.fn();

      scheduler.scheduleRecurring(callback, 1000);

      jest.advanceTimersByTime(3000);

      expect(callback).toHaveBeenCalledTimes(3);
    });
  });

  describe('isBusinessHours', () => {
    test('should return true during business hours', () => {
      // Set time to 10 AM
      jest.setSystemTime(new Date('2024-01-01T10:00:00'));

      expect(scheduler.isBusinessHours()).toBe(true);
    });

    test('should return false outside business hours', () => {
      // Set time to 8 AM
      jest.setSystemTime(new Date('2024-01-01T08:00:00'));
      expect(scheduler.isBusinessHours()).toBe(false);

      // Set time to 6 PM
      jest.setSystemTime(new Date('2024-01-01T18:00:00'));
      expect(scheduler.isBusinessHours()).toBe(false);
    });
  });
});
```

### Python Mocking with unittest.mock

```python
# payment_service.py
import requests
from typing import Dict

class PaymentService:
    def __init__(self, api_key: str, email_service, logger):
        self.api_key = api_key
        self.email_service = email_service
        self.logger = logger

    def process_payment(self, amount: float, card_token: str) -> Dict:
        try:
            self.logger.info(f"Processing payment of ${amount}")

            response = requests.post(
                'https://api.payment-gateway.com/charge',
                json={
                    'amount': amount,
                    'currency': 'USD',
                    'source': card_token
                },
                headers={'Authorization': f'Bearer {self.api_key}'}
            )

            data = response.json()

            if data['success']:
                self.logger.info(f"Payment successful: {data['transactionId']}")

                self.email_service.send_email(
                    'customer@example.com',
                    'Payment Confirmation',
                    f'Your payment of ${amount} was successful.'
                )

                return {
                    'success': True,
                    'transactionId': data['transactionId'],
                    'amount': amount
                }

            raise Exception('Payment failed')

        except Exception as e:
            self.logger.error(f"Payment error: {str(e)}")
            raise
```

```python
# test_payment_service.py
import pytest
from unittest.mock import Mock, patch, MagicMock
from payment_service import PaymentService

class TestPaymentService:
    @pytest.fixture
    def mock_email_service(self):
        return Mock()

    @pytest.fixture
    def mock_logger(self):
        return Mock()

    @pytest.fixture
    def payment_service(self, mock_email_service, mock_logger):
        return PaymentService('test-api-key', mock_email_service, mock_logger)

    @patch('payment_service.requests.post')
    def test_process_successful_payment(
        self,
        mock_post,
        payment_service,
        mock_email_service,
        mock_logger
    ):
        # Arrange
        mock_response = Mock()
        mock_response.json.return_value = {
            'success': True,
            'transactionId': 'txn_12345'
        }
        mock_post.return_value = mock_response

        # Act
        result = payment_service.process_payment(100, 'tok_visa')

        # Assert API call
        mock_post.assert_called_once_with(
            'https://api.payment-gateway.com/charge',
            json={
                'amount': 100,
                'currency': 'USD',
                'source': 'tok_visa'
            },
            headers={'Authorization': 'Bearer test-api-key'}
        )

        # Assert email sent
        mock_email_service.send_email.assert_called_once_with(
            'customer@example.com',
            'Payment Confirmation',
            'Your payment of $100 was successful.'
        )

        # Assert logging
        assert mock_logger.info.call_count == 2
        mock_logger.info.assert_any_call('Processing payment of $100')
        mock_logger.info.assert_any_call('Payment successful: txn_12345')

        # Assert result
        assert result == {
            'success': True,
            'transactionId': 'txn_12345',
            'amount': 100
        }

    @patch('payment_service.requests.post')
    def test_handle_payment_failure(
        self,
        mock_post,
        payment_service,
        mock_email_service,
        mock_logger
    ):
        # Arrange
        mock_post.side_effect = Exception('Insufficient funds')

        # Act & Assert
        with pytest.raises(Exception, match='Insufficient funds'):
            payment_service.process_payment(100, 'tok_visa')

        # Verify error logged
        mock_logger.error.assert_called_once()

        # Verify email not sent
        mock_email_service.send_email.assert_not_called()
```

## Key Concepts

### Mock vs Stub vs Spy

**Mock**: Verifies interactions (calls, arguments)
```javascript
const mock = jest.fn();
mock('arg1', 'arg2');
expect(mock).toHaveBeenCalledWith('arg1', 'arg2');
```

**Stub**: Provides predefined responses
```javascript
const stub = jest.fn().mockReturnValue('fixed response');
const result = stub(); // Always returns 'fixed response'
```

**Spy**: Tracks calls while preserving real behavior
```javascript
const spy = jest.spyOn(object, 'method');
object.method(); // Real method executes
expect(spy).toHaveBeenCalled(); // But calls are tracked
```

## Common Pitfalls

### Pitfall 1: Over-mocking
```javascript
// ❌ BAD: Mocking too much
const result = mockFunction.mockReturnValue({ deeply: { nested: { value: 42 } } });

// ✅ GOOD: Mock only what's needed
const result = mockFunction.mockReturnValue({ value: 42 });
```

### Pitfall 2: Not Resetting Mocks
```javascript
// ✅ GOOD: Reset between tests
afterEach(() => {
  jest.clearAllMocks();
});
```

## Next Steps

- [Intermediate Pattern 1: Test Organization Architecture](../intermediate/pattern-1.md)
- [Advanced Topics: Contract Testing](../../docs/advanced-topics.md#contract-testing)
- [Best Practices: Mock Strategies](../../docs/best-practices.md#mock-and-stub-strategies)
