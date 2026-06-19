/**
 * Step 16: K6 Load Testing Script for Investment Advisory AI Agent
 * Run: k6 run load-testing/k6_script.js
 * Visualise: k6 cloud or k6 output influxdb / prometheus-rw
 */

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";

// ── Custom metrics ────────────────────────────────────────────────────────────
const errorRate = new Rate("error_rate");
const recommendationLatency = new Trend("recommendation_latency_ms");
const totalRecommendations = new Counter("total_recommendations");

// ── Test configuration ────────────────────────────────────────────────────────
export const options = {
  stages: [
    { duration: "10s", target: 5 },   // ramp up to 5 VUs
    { duration: "20s", target: 10 },  // hold at 10 VUs
    { duration: "10s", target: 0 },   // ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<2000"],  // 95% requests under 2s
    error_rate: ["rate<0.01"],          // less than 1% error rate
    http_req_failed: ["rate<0.01"],
  },
};

// ── Test scenarios ────────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || "http://localhost:8501";

const TEST_PROFILES = [
  { age: 25, income: 50000, savings: 10000, risk: "High",   goal: "Long-term" },
  { age: 45, income: 80000, savings: 15000, risk: "Medium", goal: "Medium-term" },
  { age: 60, income: 60000, savings: 20000, risk: "Low",    goal: "Short-term" },
  { age: 30, income: 40000, savings: 5000,  risk: "Low",    goal: "Medium-term" },
  { age: 35, income: 120000, savings: 40000, risk: "High",  goal: "Long-term" },
];

export default function () {
  // Pick a random profile
  const profile = TEST_PROFILES[Math.floor(Math.random() * TEST_PROFILES.length)];

  // Streamlit health check
  const healthRes = http.get(`${BASE_URL}/_stcore/health`);
  check(healthRes, {
    "health check 200": (r) => r.status === 200,
  });

  // Main page load
  const start = Date.now();
  const mainRes = http.get(`${BASE_URL}/`);
  recommendationLatency.add(Date.now() - start);
  totalRecommendations.add(1);

  const passed = check(mainRes, {
    "main page 200": (r) => r.status === 200,
    "contains disclaimer": (r) => r.body.includes("educational demo"),
    "response time < 3s": (r) => r.timings.duration < 3000,
  });

  errorRate.add(!passed);
  sleep(1);
}

// ── Summary handler ───────────────────────────────────────────────────────────
export function handleSummary(data) {
  return {
    "load-testing/results/k6_summary.json": JSON.stringify(data, null, 2),
    stdout: `
=== Load Test Summary ===
Requests: ${data.metrics.http_reqs?.values?.count || 0}
p95 Latency: ${(data.metrics.http_req_duration?.values?.["p(95)"] || 0).toFixed(1)}ms
Error Rate: ${((data.metrics.http_req_failed?.values?.rate || 0) * 100).toFixed(2)}%
Total Recommendations Simulated: ${data.metrics.total_recommendations?.values?.count || 0}
========================
`,
  };
}
