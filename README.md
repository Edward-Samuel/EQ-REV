# Stock Availability API

A comprehensive Node.js API for managing and querying stock availability data with web scraping capabilities for product information.

## 🚀 Features

- **RESTful API** for stock availability queries
- **SQLite Database** for efficient data storage and retrieval
- **Web Scraping** for real-time product data from Zepto
- **Advanced Filtering** with city, SKU, date range, and search capabilities
- **Pagination & Sorting** for large datasets
- **Health Monitoring** with built-in health check endpoint
- **CSV Data Import** functionality
- **Security** with Helmet middleware and CORS support

## 📁 Project Structure

```
eq-rev/
├── server.js              # Main Express server
├── routes.js              # API route definitions
├── database.js            # SQLite database wrapper
├── loadData.js            # CSV data import utility
├── scraper.py             # Python web scraper for Zepto
├── example_usage.js       # API usage examples
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── stock_data.csv         # Stock data in CSV format
├── products.csv           # Scraped product data
├── stock_data.db          # SQLite database file
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites

- Node.js (v14 or higher)
- Python 3.7+
- npm or yarn

### Setup

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd eq-rev
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   npm run load-data
   ```

## 🚀 Usage

### Starting the Server

```bash
# Production mode
npm start

# Development mode with auto-reload
npm run dev
```

The server will start on `http://localhost:8000` by default.

### API Endpoints

#### 1. Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy"
}
```

#### 2. Stock Availability Query

```http
POST /api/stock-availability
```

**Request Body:**

```json
{
  "city": "chennai",
  "skus": ["SKU4"],
  "page": 1,
  "pageSize": 10,
  "sortBy": "TOTAL STOCK",
  "sortOrder": "DESC",
  "dateFrom": "2025-09-01",
  "dateTo": "2025-09-30",
  "search": "toothbrush"
}
```

**Parameters:**

- `city` (optional): Filter by city name
- `skus` (optional): Array of SKU IDs to filter
- `page` (optional): Page number for pagination (default: 1)
- `pageSize` (optional): Items per page (default: 10, max: 100)
- `sortBy` (optional): Sort field (`TOTAL STOCK`, `INSTOCK DARKSTORES`, `TOTAL DARKSTORES`, `DAYS OF STOCK`, `SKU`)
- `sortOrder` (optional): Sort direction (`ASC` or `DESC`)
- `dateFrom` (optional): Start date filter (YYYY-MM-DD)
- `dateTo` (optional): End date filter (YYYY-MM-DD)
- `search` (required): Search term for product name, ID, or category

**Response:**

```json
{
  "city": "chennai",
  "data": [
    {
      "sku": "SKU4",
      "instock_darkstores": 15,
      "instock_darkstores_percentage": 75.5,
      "total_darkstores": 20,
      "total_stock": 150,
      "days_of_stock": 12.5,
      "out_of_stock_flag": false
    }
  ]
}
```

## 🐍 Web Scraping

The project includes a Python scraper for collecting product data from Zepto:

### Running the Scraper

```bash
python scraper.py
```

### Scraper Features

- **Multi-location scraping** (Mumbai, Delhi, Bangalore)
- **Product data extraction** (name, price, availability, images)
- **CSV export** functionality
- **Respectful scraping** with delays and proper headers
- **Error handling** and logging

### Scraped Data Fields

- Product Name
- Product Image URL
- Product ID
- Stock Availability
- Sponsored Status
- MRP (Maximum Retail Price)
- Selling Price
- Product Position

## 📊 Database Schema

The SQLite database contains a `stock_data` table with the following structure:

```sql
CREATE TABLE stock_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    city_name TEXT,
    product_id TEXT,
    product_name TEXT,
    category TEXT,
    total_orders INTEGER,
    total_sales REAL,
    stock_quantity INTEGER,
    instock_darkstores INTEGER,
    oos_darkstores INTEGER,
    total_darkstores INTEGER
);
```

## 🔧 Configuration

### Environment Variables

- `PORT`: Server port (default: 8000)
- `NODE_ENV`: Environment mode (`development` or `production`)

### Database Configuration

The database file (`stock_data.db`) is automatically created if it doesn't exist. The system will automatically load data from `stock_data.csv` on first startup.

## 📝 API Examples

### Example 1: Basic Search

```javascript
const response = await fetch("http://localhost:8000/api/stock-availability", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    city: "chennai",
    search: "toothbrush",
    page: 1,
    pageSize: 5,
  }),
});
```

### Example 2: Advanced Filtering

```javascript
const response = await fetch("http://localhost:8000/api/stock-availability", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    city: "delhi",
    skus: ["SKU1", "SKU2"],
    dateFrom: "2025-09-01",
    dateTo: "2025-09-30",
    sortBy: "TOTAL STOCK",
    sortOrder: "DESC",
    search: "baby wipes",
  }),
});
```

## 🧪 Testing

Run the example usage script to test the API:

```bash
node example_usage.js
```

This will execute several test scenarios and display the results.

## 📦 Dependencies

### Node.js Dependencies

- `express`: Web framework
- `sqlite3`: SQLite database driver
- `cors`: Cross-origin resource sharing
- `helmet`: Security middleware
- `morgan`: HTTP request logger
- `axios`: HTTP client
- `csv-parser`: CSV file parser
- `nodemon`: Development auto-reload

### Python Dependencies

- `requests`: HTTP library
- `beautifulsoup4`: HTML parsing
- `csv`: CSV file handling

## 🔒 Security Features

- **Helmet.js** for security headers
- **CORS** configuration
- **Input validation** and sanitization
- **Error handling** with proper HTTP status codes
- **Rate limiting** considerations in scraper

## 🚀 Deployment

### Production Deployment

1. Set environment variables:

   ```bash
   export NODE_ENV=production
   export PORT=8000
   ```

2. Start the server:
   ```bash
   npm start
   ```

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --production
COPY . .
EXPOSE 8000
CMD ["npm", "start"]
```

## 📈 Performance Considerations

- **Database indexing** on frequently queried fields
- **Pagination** to handle large datasets
- **Connection pooling** for database connections
- **Caching** strategies for frequently accessed data
- **Rate limiting** for web scraping

## 🐛 Troubleshooting

### Common Issues

1. **Database not found**: Run `npm run load-data` to initialize
2. **Port already in use**: Change the PORT environment variable
3. **CSV loading errors**: Check file format and permissions
4. **Scraper failures**: Verify network connectivity and target site availability

### Logs

The application provides detailed logging for:

- Server startup and shutdown
- Database operations
- API requests and responses
- Scraping activities
- Error conditions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:

- Check the troubleshooting section
- Review the example usage file
- Examine the API documentation above

---

**Note**: This API is designed for internal use and educational purposes. Ensure compliance with target websites' terms of service when using the web scraping functionality.
