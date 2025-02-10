# [Welcome to Coxcox AI](https://coxcoxai.com)

Coxcox AI is an agent designed to perform telemarketing work

<img src='./assets/coxcox-logo.webp' alt='coxcoxai agent replace telemaketing jobs'/>

# Connecting to WhatsApp

To connect and manage messages for WhatsApp Business accounts of other companies through your backend, the **Cloud API** provided by Meta is the best option:  
**Documentation**: [WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)

---

## Cloud API Overview

- **Hosted by Meta**: No need for self-hosting or maintenance.
- **Messaging Functions**: Provides direct access to send/receive messages, templates, and media.
- **Ideal for Customer Support**: Supports quick setup and scalability.
- **Cost**: Based on usage but simplifies real-time, AI-driven messaging integration.

For an application that manages conversations via WhatsApp Business for customer service, the **Cloud API** is specifically designed for this purpose, making it efficient and easy to implement.

---

## Business Portfolios

To use the Cloud API, you must have a **Business Portfolio**.  
A **Business Portfolio** serves as a container for your WhatsApp Business Accounts (WABA) and associated business phone numbers.

### Test Resources

When completing the initial setup as described in the **Getting Started** guide, a test **WABA** and business phone number are automatically created.

### Deleting Your Business Portfolio

You can delete your Business Portfolio and its test resources under these conditions:

1. You are the **administrator** of the associated Business Portfolio.
2. No other apps are associated with the Business Portfolio.
3. The Business Portfolio is not associated with any other WABA.
4. The WABA is not associated with any other business phone number.

### Steps to Delete

1. Go to the **App Dashboard** > **WhatsApp** > **Settings**.
2. Locate the **Test Account** section.
3. Click the **Delete** button.

---

## Version Control

The Cloud API uses the **Graph API Versioning Protocol**. This means:

- All endpoint requests must include a version number.
- Each version remains available for approximately 2 years before being deprecated.

---

## Access Tokens

The API supports the following types of tokens:

1. **System User Access Token**
2. **Business Integration System User Access Token**
3. **User Access Token**

For more information, refer to the official guide: [Access Tokens](https://developers.facebook.com/docs/whatsapp/business-management-api/get-started#informaci-n-general)

---

## Permissions

The Cloud API requires the following **Graph API permissions**. The exact combination depends on the endpoints your app needs to access:

- `business_management`: Required to interact with a Business Portfolio.
- `whatsapp_business_management`: Required to interact with a WABA, its stats, templates, or business phone numbers.
- `whatsapp_business_messaging`: Required to send and receive WhatsApp messages.

---

## Webhooks

Webhooks allow you to receive **real-time HTTP notifications** about changes to specific objects.

### Key Events with Webhooks

In WhatsApp, webhooks can notify you about events such as:

- Message delivery and read notifications.
- Account-level changes.

### Important Note

Once you migrate a phone number to the **WhatsApp Business Platform**, you cannot use it with the **WhatsApp Business App**.

**Meta Apps Limitation**: Only one endpoint can be configured per Meta app. If you need to send webhook notifications to multiple endpoints, you must use multiple Meta apps.

### Example Webhook Payload

**Incoming Webhook Example**:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "500456646489703",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15551576865",
              "phone_number_id": "468853166319123"
            },
            "contacts": [
              {
                "profile": {
                  "name": "."
                },
                "wa_id": "5214428968441"
              }
            ],
            "messages": [
              {
                "from": "5214428968441",
                "id": "wamid.HBgNNTIxNDQyODk2ODQ0MRUCABIYFDNBQzU1MTI5MkJBNkVGRjBDN0U5AA==",
                "timestamp": "1734487099",
                "text": {
                  "body": "Thanks"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}
```

# Getting Started with Webhooks

To set up any webhook, follow these steps:

---

## 1. Create a Secure Endpoint

You need to create an endpoint on a secure server capable of processing HTTPS requests.  
Your endpoint must handle **two types** of HTTPS requests:

1. **Verification Requests**
2. **Event Notifications**

### Requirements:

- The server must have a valid **TLS/SSL certificate** correctly configured and installed.
- **Self-signed certificates are not supported.**

---

## Verification Requests

When configuring the Webhooks product in your **App Dashboard**, Meta will send a **GET request** to your endpoint URL.

**Example Verification Request**:

```http
GET https://www.your-clever-domain-name.com/webhooks?
  hub.mode=subscribe&
  hub.challenge=1158201444&
  hub.verify_token=meatyhamhock
```

### Validating Verification Requests

Whenever your endpoint receives a **verification request**, it must:

1. Verify that the `hub.verify_token` value matches the token string you set in the **Verify Token** field during Webhook configuration in the **App Dashboard**.
2. Respond with the `hub.challenge` value sent in the request.

---

## 2. Configure the Webhooks Product in Your App Dashboard

Follow the detailed steps in the [**DOCS**](https://developers.facebook.com/docs/graph-api/webhooks/getting-started#configure-webhooks-product) to configure your Webhook in Facebook.

---

## Event Notifications

When you configure the **Webhooks** product, you will subscribe to specific fields on an object type (e.g., the `photos` field on a `user` object).

When any subscribed field changes, Meta will send a **POST request** to your endpoint with a **JSON payload** describing the change.

---

### Responding to Event Notifications

Your endpoint must respond to all **Event Notifications** with a `200 OK` HTTPS response.

---

### Important Notes:

- Meta **does not store** any Webhook event notification data.
- Ensure you **capture and store** any payload content that you want to keep.

---

## Learn More

For the complete documentation, visit:  
[Meta Webhooks Getting Started](https://developers.facebook.com/docs/graph-api/webhooks/getting-started)
