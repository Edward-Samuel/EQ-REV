const axios = require("axios");

// Example usage of the Stock Availability API

// API endpoint
const API_URL = "http://localhost:8000/api/stock-availability";

// Example 1: Basic search
const example1 = {
  city: "chennai",
  skus: ["SKU4"],
  page: 1,
  pageSize: 2,
  sortBy: "TOTAL STOCK",
  sortOrder: "DESC",
  dateFrom: "2025-09-01",
  dateTo: "2025-09-30",
  search: "toothbrush",
};

// Example 2: Search without city filter
const example2 = {
  skus: ["SKU4", "SKU5"],
  page: 1,
  pageSize: 10,
  sortBy: "INSTOCK DARKSTORES",
  sortOrder: "ASC",
  search: "baby",
};

// Example 3: Search with date range only
const example3 = {
  page: 1,
  pageSize: 5,
  sortBy: "DAYS OF STOCK",
  sortOrder: "DESC",
  dateFrom: "2025-09-10",
  dateTo: "2025-09-20",
  search: "cleaning",
};

// Example 4: Delhi baby wipes search
const example4 = {
  city: "delhi",
  skus: ["SKU1", "SKU2"],
  page: 1,
  pageSize: 2,
  sortBy: "TOTAL STOCK",
  sortOrder: "DESC",
  dateFrom: "2025-09-01",
  dateTo: "2025-09-30",
  search: "baby wipes",
};

async function testAPI(exampleData, exampleName) {
  console.log(`\n=== ${exampleName} ===`);
  console.log("Request JSON:");
  console.log(JSON.stringify(exampleData, null, 2));

  try {
    const response = await axios.post(API_URL, exampleData, {
      headers: {
        "Content-Type": "application/json",
      },
      timeout: 10000,
    });

    console.log(`\nResponse Status: ${response.status}`);
    console.log("Response JSON:");
    console.log(JSON.stringify(response.data, null, 2));
  } catch (error) {
    if (error.code === "ECONNREFUSED") {
      console.log(
        "Error: Could not connect to the API. Make sure the server is running on http://localhost:8000"
      );
    } else if (error.response) {
      console.log(
        `Error: ${error.response.status} - ${
          error.response.data.error || error.response.data.message
        }`
      );
    } else {
      console.log(`Error: ${error.message}`);
    }
  }
}

async function runTests() {
  console.log("Stock Availability API Test Examples");
  console.log("=".repeat(50));

  // Test all examples
  await testAPI(example1, "Example 1: Chennai toothbrush search");
  await testAPI(example2, "Example 2: Baby products search");
  await testAPI(example3, "Example 3: Cleaning products with date range");
  await testAPI(example4, "Example 4: Delhi baby wipes search");

  console.log("\n" + "=".repeat(50));
}

// Run if called directly
if (require.main === module) {
  runTests().catch(console.error);
}

module.exports = { testAPI, runTests };
