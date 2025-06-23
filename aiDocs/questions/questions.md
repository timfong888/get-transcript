# Questions Document

## June 23, 2025 - Review of Migrate-to-Fly-Tasks.md

Based on the questions guide framework, I've identified several areas in the migration task plan where assumptions have been made that should be clarified before proceeding.

**Question 1:** Which web framework would you prefer for converting the Firebase Function to a web server?

**Hypothesized Answer:** You would prefer FastAPI due to its automatic API documentation generation, type hints support, and async capabilities, which would be beneficial for handling proxy requests efficiently.

**Answer:** Agree: FastAPI.

---

**Question 2:** Do you have any budget constraints or cost targets for the Fly.io deployment?

**Hypothesized Answer:** You want to keep costs similar to or lower than Firebase Functions, with a preference for predictable pricing over variable costs based on usage.

**Answer:** Yes, lower than firebase functions.

---

**Question 3:** What is your target timeline for completing this migration?

**Hypothesized Answer:** The estimated 2-3 weeks aligns with your expectations, but you'd prefer to prioritize getting the proxy authentication working first, even if other optimization phases take longer.

**Answer:** 10 minutes.

---

**Question 4:** Should we keep the Firebase Functions deployment as a backup during the migration?

**Hypothesized Answer:** Yes, you want to maintain the Firebase Functions deployment until the Fly.io version is fully tested and proven to work reliably with proxy authentication.

**Answer:** Yes.

---

**Question 5:** Do you have specific geographic regions where your users are located that should influence the deployment strategy?

**Hypothesized Answer:** Your primary users are in North America, so deploying to US regions would be optimal for latency, but you don't need multi-region deployment initially.

**Answer:** yes, US only, one region.

---

**Question 6:** What level of monitoring and observability do you need for this application?

**Hypothesized Answer:** You want basic health monitoring and error tracking, but don't need complex metrics dashboards or advanced monitoring tools initially. Simple logging and alerts for failures would be sufficient.

**Answer:** yes, primarily logging to Google logs (which is where I am logging other things)

---

**Question 7:** Do you want to implement caching for transcript requests, and if so, what type?

**Hypothesized Answer:** You would like simple in-memory caching for frequently requested transcripts to reduce proxy usage and improve response times, but don't need persistent caching across deployments.

**Answer:** yes, in-memory caching is fine, but if this involves more than 5 lines of code, don't worry about it since all transcripts need to be persisted to Firebase firestore anyway.

---

**Question 8:** Should we prioritize getting the basic proxy authentication working first, or complete all phases systematically?

**Hypothesized Answer:** You want to prioritize getting the proxy authentication working (Phases 1-3 and basic deployment from Phase 5) before moving to optimization phases, since that's the core problem we're solving.

**Answer:** yes, start with the core problem and then move to the optimization phases.

---

**Question 9:** Do you have any preferences for machine size or scaling configuration on Fly.io?

**Hypothesized Answer:** You prefer to start with the smallest machine size that works reliably and only scale up if performance issues arise, prioritizing cost efficiency over performance initially.

**Answer:** yes, start with the smallest machine size that works reliably and only scale up if performance issues arise, prioritizing cost efficiency over performance initially.

---

**Question 10:** Should we implement the full retry logic and circuit breaker patterns mentioned in Phase 3, or start with simpler error handling?

**Hypothesized Answer:** You want to start with basic retry logic (simple exponential backoff) and add more sophisticated patterns like circuit breakers only if needed based on real-world usage patterns.

**Answer:** yes, start with the basic retry logic and add more sophisticated patterns like circuit breakers only if needed based on real-world usage patterns.

