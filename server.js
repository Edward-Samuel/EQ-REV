const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const path = require('path');
const fs = require('fs');

const routes = require('./routes');
const loadDataFromCSV = require('./loadData');

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(helmet()); // Security headers
app.use(cors()); // Enable CORS
app.use(morgan('combined')); // Logging
app.use(express.json({ limit: '10mb' })); // Parse JSON bodies
app.use(express.urlencoded({ extended: true })); // Parse URL-encoded bodies

// Routes
app.use('/', routes);

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err.stack);
    res.status(500).json({
        error: 'Something went wrong!',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Internal server error'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: 'Endpoint not found',
        message: `Cannot ${req.method} ${req.path}`
    });
});

// Initialize database and start server
async function startServer() {
    try {
        // Check if database exists, if not load data
        const dbPath = path.join(__dirname, 'stock_data.db');
        const csvPath = path.join(__dirname, 'stock_data.csv');
        
        if (!fs.existsSync(dbPath) && fs.existsSync(csvPath)) {
            console.log('Database not found. Loading data from CSV...');
            await loadDataFromCSV();
        }
        
        // Start the server
        app.listen(PORT, () => {
            console.log(`🚀 Stock Availability API server running on port ${PORT}`);
            console.log(`📊 API Documentation: http://localhost:${PORT}/`);
            console.log(`🔍 Health Check: http://localhost:${PORT}/health`);
            console.log(`📈 Stock Availability: http://localhost:${PORT}/api/stock-availability`);
        });
        
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Shutting down server gracefully...');
    process.exit(0);
});

// Start the server
startServer();
