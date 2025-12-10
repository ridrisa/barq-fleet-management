# Support API Documentation

The Support API provides endpoints for managing support tickets, FAQ, knowledge base, feedback, and chat functionality.

## Base URL

```
/api/v1/support
```

## Authentication

All endpoints require a valid JWT token.

---

## Tickets

### List Tickets

```http
GET /tickets
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number |
| `limit` | integer | Items per page |
| `status` | string | Filter by status: `open`, `in_progress`, `pending`, `resolved`, `closed` |
| `priority` | string | Filter by priority: `low`, `medium`, `high`, `urgent` |
| `category` | string | Filter by category |
| `assigned_to` | integer | Filter by assignee |
| `created_by` | integer | Filter by creator |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "ticket_number": "TKT-2024-001234",
      "subject": "Delivery not received",
      "status": "open",
      "priority": "high",
      "category": "delivery_issue",
      "created_by": 5,
      "created_by_name": "Ahmed Al-Rashid",
      "assigned_to": null,
      "created_at": "2024-12-10T10:00:00Z",
      "updated_at": "2024-12-10T10:00:00Z",
      "response_due_at": "2024-12-10T14:00:00Z"
    }
  ],
  "total": 45,
  "page": 1
}
```

### Get Ticket

```http
GET /tickets/{id}
```

**Response:**

```json
{
  "id": 1,
  "ticket_number": "TKT-2024-001234",
  "subject": "Delivery not received",
  "description": "I ordered a package but it shows delivered when I haven't received it.",
  "status": "open",
  "priority": "high",
  "category": "delivery_issue",
  "subcategory": "missing_delivery",
  "created_by": 5,
  "created_by_name": "Ahmed Al-Rashid",
  "assigned_to": 10,
  "assigned_to_name": "Support Agent Ali",
  "related_delivery_id": 12345,
  "attachments": [
    {
      "id": 1,
      "filename": "screenshot.png",
      "url": "https://storage.barq.com/attachments/tkt1_1.png",
      "size": 125000
    }
  ],
  "messages": [
    {
      "id": 1,
      "sender_id": 5,
      "sender_name": "Ahmed Al-Rashid",
      "sender_type": "customer",
      "message": "I ordered a package but it shows delivered when I haven't received it.",
      "created_at": "2024-12-10T10:00:00Z"
    }
  ],
  "history": [
    {
      "action": "created",
      "timestamp": "2024-12-10T10:00:00Z",
      "user_id": 5
    }
  ],
  "created_at": "2024-12-10T10:00:00Z",
  "updated_at": "2024-12-10T10:00:00Z"
}
```

### Create Ticket

```http
POST /tickets
```

**Request Body:**

```json
{
  "subject": "Delivery delayed",
  "description": "My delivery was supposed to arrive yesterday but it's still in transit.",
  "category": "delivery_issue",
  "subcategory": "delayed_delivery",
  "priority": "medium",
  "related_delivery_id": 12346
}
```

**Categories:**
- `delivery_issue` - Delivery problems
- `payment_issue` - Payment/COD issues
- `courier_complaint` - Courier behavior
- `app_issue` - Mobile/web app issues
- `account_issue` - Account problems
- `billing` - Billing inquiries
- `general` - General inquiries

### Update Ticket

```http
PUT /tickets/{id}
```

**Request Body:**

```json
{
  "status": "in_progress",
  "priority": "urgent",
  "assigned_to": 10
}
```

### Add Message to Ticket

```http
POST /tickets/{id}/messages
```

**Request Body:**

```json
{
  "message": "We are investigating your issue and will update you shortly.",
  "internal": false
}
```

### Add Attachment

```http
POST /tickets/{id}/attachments
```

**Request:** `multipart/form-data`

### Resolve Ticket

```http
POST /tickets/{id}/resolve
```

**Request Body:**

```json
{
  "resolution": "Contacted courier - delivery was left with neighbor. Customer confirmed receipt.",
  "resolution_category": "resolved_with_customer"
}
```

### Close Ticket

```http
POST /tickets/{id}/close
```

---

## FAQ

### List FAQs

```http
GET /faq
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category |
| `search` | string | Search in question/answer |
| `language` | string | Language: `en`, `ar` |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "question": "How do I track my delivery?",
      "answer": "You can track your delivery by entering your tracking number on our website or app.",
      "category": "tracking",
      "views": 1250,
      "helpful_count": 320,
      "language": "en"
    }
  ],
  "categories": [
    {"id": "tracking", "name": "Tracking", "count": 5},
    {"id": "payment", "name": "Payment", "count": 8}
  ]
}
```

### Get FAQ

```http
GET /faq/{id}
```

### Create FAQ

```http
POST /faq
```

**Request Body:**

```json
{
  "question": "What payment methods do you accept?",
  "answer": "We accept cash on delivery (COD), credit cards, and bank transfers.",
  "category": "payment",
  "language": "en",
  "tags": ["payment", "cod", "credit card"]
}
```

### Update FAQ

```http
PUT /faq/{id}
```

### Delete FAQ

```http
DELETE /faq/{id}
```

### Mark FAQ Helpful

```http
POST /faq/{id}/helpful
```

**Request Body:**

```json
{
  "helpful": true
}
```

---

## Knowledge Base

### List Articles

```http
GET /kb/articles
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `category` | string | Filter by category |
| `search` | string | Full-text search |
| `status` | string | Filter by status: `draft`, `published`, `archived` |

**Response:**

```json
{
  "items": [
    {
      "id": 1,
      "title": "How to Use the Courier App",
      "slug": "how-to-use-courier-app",
      "excerpt": "A complete guide to using the BARQ courier mobile application.",
      "category": "courier_guides",
      "status": "published",
      "views": 5200,
      "last_updated": "2024-12-01T10:00:00Z"
    }
  ]
}
```

### Get Article

```http
GET /kb/articles/{id}
```

**Response:**

```json
{
  "id": 1,
  "title": "How to Use the Courier App",
  "slug": "how-to-use-courier-app",
  "content": "## Introduction\n\nThe BARQ courier app helps you manage your daily deliveries...",
  "category": "courier_guides",
  "status": "published",
  "author_id": 10,
  "author_name": "Documentation Team",
  "views": 5200,
  "related_articles": [
    {
      "id": 2,
      "title": "Troubleshooting App Issues"
    }
  ],
  "tags": ["courier", "mobile app", "guide"],
  "created_at": "2024-06-15T08:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z"
}
```

### Create Article

```http
POST /kb/articles
```

**Request Body:**

```json
{
  "title": "Understanding COD Collections",
  "content": "## Overview\n\nCash on Delivery (COD) is a popular payment method...",
  "category": "courier_guides",
  "status": "draft",
  "tags": ["cod", "payment", "collections"]
}
```

### Update Article

```http
PUT /kb/articles/{id}
```

### Delete Article

```http
DELETE /kb/articles/{id}
```

### Search Knowledge Base

```http
GET /kb/search
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `q` | string | Search query |
| `limit` | integer | Max results |

**Response:**

```json
{
  "query": "COD collection",
  "results": [
    {
      "type": "article",
      "id": 5,
      "title": "Understanding COD Collections",
      "excerpt": "...COD collection process explained...",
      "relevance": 0.95
    },
    {
      "type": "faq",
      "id": 12,
      "question": "How do I settle COD?",
      "relevance": 0.82
    }
  ]
}
```

---

## Feedback

### Submit Feedback

```http
POST /feedback
```

**Request Body:**

```json
{
  "type": "suggestion",
  "category": "app_feature",
  "subject": "Add dark mode",
  "message": "It would be great to have a dark mode option in the app.",
  "rating": 4
}
```

**Feedback Types:**
- `bug` - Bug report
- `suggestion` - Feature suggestion
- `compliment` - Positive feedback
- `complaint` - Complaint

### List Feedback

```http
GET /feedback
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | string | Filter by type |
| `status` | string | Filter by status |
| `rating` | integer | Filter by rating |

### Update Feedback Status

```http
PUT /feedback/{id}
```

**Request Body:**

```json
{
  "status": "reviewed",
  "internal_notes": "Added to feature backlog"
}
```

---

## Chat (WebSocket)

### Connect to Chat

```
WS /chat/connect
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `token` | string | JWT token |

### Send Message

```json
{
  "type": "message",
  "content": "Hello, I need help with my delivery",
  "conversation_id": "conv_123"
}
```

### Receive Message

```json
{
  "type": "message",
  "id": "msg_456",
  "sender": {
    "id": 10,
    "name": "Support Agent",
    "type": "agent"
  },
  "content": "Hello! How can I help you today?",
  "timestamp": "2024-12-10T10:30:00Z"
}
```

### Chat REST Endpoints

#### Start Chat Session

```http
POST /chat/sessions
```

**Request Body:**

```json
{
  "subject": "Help with delivery",
  "category": "delivery_issue"
}
```

#### Get Chat History

```http
GET /chat/sessions/{session_id}/messages
```

#### End Chat Session

```http
POST /chat/sessions/{session_id}/end
```

---

## Contact

### Get Contact Information

```http
GET /contact
```

**Response:**

```json
{
  "phone": "+966920012345",
  "email": "support@barq.com",
  "whatsapp": "+966501234567",
  "working_hours": {
    "weekdays": "8:00 AM - 10:00 PM",
    "weekends": "10:00 AM - 6:00 PM"
  },
  "social_media": {
    "twitter": "@BarqDelivery",
    "instagram": "@barqdelivery"
  }
}
```

### Submit Contact Form

```http
POST /contact
```

**Request Body:**

```json
{
  "name": "Mohammed Ali",
  "email": "mohammed@example.com",
  "phone": "+966501234567",
  "subject": "Partnership Inquiry",
  "message": "I would like to discuss a business partnership."
}
```

---

## Analytics

### Get Support Analytics

```http
GET /analytics
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `start_date` | string | Start date |
| `end_date` | string | End date |

**Response:**

```json
{
  "period": {
    "start": "2024-12-01",
    "end": "2024-12-10"
  },
  "tickets": {
    "total": 450,
    "resolved": 380,
    "resolution_rate": 84.4,
    "average_response_time_hours": 2.5,
    "average_resolution_time_hours": 18.2
  },
  "by_category": [
    {"category": "delivery_issue", "count": 180},
    {"category": "payment_issue", "count": 95}
  ],
  "satisfaction": {
    "average_rating": 4.2,
    "responses": 320,
    "nps_score": 45
  }
}
```
