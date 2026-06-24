- Make unit tests for `profiles`
- Make integration tests for `profiles`


---

### In-memory EventBus is not durable for production

Events are lost if the process crashes between the DB commit and the in-memory `event_bus.publish()` call (or vice versa).

**Fix:** Implement [Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) — write events to an `outbox` table in the same DB transaction, and have a background worker poll and publish them reliably.

---
