# Email Worker — Dev Setup & Test Guide

This worker consumes messages from **RabbitMQ** and sends emails via **SMTP**.
For local development we use **Mailpit** as an SMTP catcher (no real emails go out).

---

## Prerequisites

* Docker
* Python 3.10+

---

## 1) Start infra: RabbitMQ & Mailpit
<!--[Sign in with app passwords - Gmail Help](https://support.google.com/mail/answer/185833)-->
```bash
cd infra
docker compose up -d
cd ..
```

**Ports**

* RabbitMQ AMQP: `5672`
* RabbitMQ UI: `http://localhost:15672` (user/pass: `guest` / `guest`)
* Mailpit SMTP: `1025`
* Mailpit UI: `http://localhost:8025`

> Tip: `docker compose logs -f` (in `infra/`) tails infra logs.

---

## 2) Install dependencies & set environment

Create/activate a virtual environment, then:

```bash
pip install -r requirements.txt
cp .env.example .env
```

---

## 3) Run the Flask worker

```bash
flask --app app worker
```

* Runs until you stop it (Ctrl+C).

> If you see “`SMTP AUTH extension not supported by server`”, you’re hitting Mailpit with creds. For dev, **leave `MAIL_USERNAME/MAIL_PASSWORD` empty** and **TLS/SSL false**.

---

## 4) Publish a test message (routing key: `send`)

The worker expects a JSON payload like:

```json
{
  "to": "you@example.com",
  "subject": "Test",
  "html": "<b>Hello</b>"
}
```

You can publish via **any** of the following:

### 4.a) RabbitMQ Management UI (easiest)

1. Open [http://localhost:15672](http://localhost:15672) → log in (`guest`/`guest`).
2. Go to **Exchanges** → click `email`.
3. In **Publish message**:

   * **Routing key**: `send`
   * **Payload**: paste the JSON above
   * **Properties**: (optional) `content_type` = `application/json`
4. Click **Publish message** → you should see the worker log a delivery.

### 4.b) HTTP API with cURL (reliable)

For the default vhost `/` (URL-encoded as `%2F`):

```bash
curl -u guest:guest \
  -H "Content-Type: application/json" \
  -X POST http://localhost:15672/api/exchanges/%2F/email/publish \
  -d '{
    "properties": { "content_type": "application/json", "delivery_mode": 2 },
    "routing_key": "send",
    "payload": "eyJ0byI6InlvdUBleGFtcGxlLmNvbSIsInN1YmplY3QiOiJUZXN0IiwiaHRtbCI6IjxiPkhlbGxvPC9iPiJ9",
    "payload_encoding": "base64"
  }'
```

> The `payload` above is base64 for `{"to":"you@example.com","subject":"Test","html":"<b>Hello</b>"}`.
> Using base64 avoids “`not_json`” errors caused by quoting/escaping.

### 4.c) Postman

Import the collection for email serive from [fa-api-collections](https://github.com/forum-app-team/fa-api-collections).

* **Auth** tab → **Basic Auth** (`guest`/`guest`)
* **POST** `http://localhost:15672/api/exchanges/%2F/email/publish`
* **Body (raw JSON)** (base64 approach):

  ```json
  {
    "properties": { "content_type": "application/json", "delivery_mode": 2 },
    "routing_key": "send",
    "payload": "{{payload_b64}}",
    "payload_encoding": "base64"
  }
  ```
* **Pre-request Script**:

  ```javascript
  const data = {
    to: 'you@example.com',
    subject: 'Test',
    html: '<b>Hello</b>'
  };
  pm.variables.set('payload_b64', Buffer.from(JSON.stringify(data)).toString('base64'));
  ```

---

## 5) View the email

Open **Mailpit UI**:
[http://localhost:8025](http://localhost:8025)

You should see the message in the inbox. Click to preview the HTML.

---

## Clean up

```bash
# stop worker
Ctrl+C

# stop infra (from infra/)
docker compose down
```
