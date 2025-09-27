const express = require('express');
const Database = require('./database');
const router = express.Router();

// Stock Availability endpoint
router.post('/api/stock-availability', async (req, res) => {
    try {
        const {
            city,
            skus,
            page = 1,
            pageSize = 10,
            sortBy,
            sortOrder = 'ASC',
            dateFrom,
            dateTo,
            search
        } = req.body;

        // Validate required fields
        if (!search) {
            return res.status(400).json({
                error: 'Search parameter is required'
            });
        }

        // Validate pagination
        const pageNum = parseInt(page);
        const pageSizeNum = parseInt(pageSize);
        
        if (pageNum < 1 || pageSizeNum < 1 || pageSizeNum > 100) {
            return res.status(400).json({
                error: 'Invalid pagination parameters'
            });
        }

        // Create database connection
        const db = new Database();
        await db.connect();

        // Build filters
        const filters = {
            city,
            skus,
            dateFrom,
            dateTo,
            search,
            sortBy,
            sortOrder
        };

        // Query data
        const results = await db.queryStockData(filters);

        if (results.length === 0) {
            await db.close();
            return res.json({
                city: city || null,
                data: []
            });
        }

        // Group data by SKU and calculate metrics
        const skuData = {};
        
        results.forEach(record => {
            const sku = record.product_id;
            
            if (!skuData[sku]) {
                skuData[sku] = {
                    records: [],
                    total_stock: 0,
                    total_instock_darkstores: 0,
                    total_total_darkstores: 0,
                    total_sales: 0,
                    record_count: 0
                };
            }
            
            skuData[sku].records.push(record);
            skuData[sku].total_stock += record.stock_quantity;
            skuData[sku].total_instock_darkstores += record.instock_darkstores;
            skuData[sku].total_total_darkstores += record.total_darkstores;
            skuData[sku].total_sales += record.total_sales;
            skuData[sku].record_count += 1;
        });

        // Create SKU data list
        const skuListData = [];
        
        Object.keys(skuData).forEach(sku => {
            const data = skuData[sku];
            const recordCount = data.record_count;
            
            // Calculate averages
            const avgInstockDarkstores = data.total_instock_darkstores / recordCount;
            const avgTotalDarkstores = data.total_total_darkstores / recordCount;
            const avgDailySales = data.total_sales / recordCount;
            
            // Calculate metrics
            const totalStock = data.total_stock;
            const instockPercentage = avgTotalDarkstores > 0 
                ? (avgInstockDarkstores / avgTotalDarkstores * 100) 
                : 0;
            const daysOfStock = avgDailySales > 0 
                ? totalStock / avgDailySales 
                : 0;
            const outOfStockFlag = totalStock === 0;
            
            skuListData.push({
                sku: sku,
                instock_darkstores: Math.round(avgInstockDarkstores),
                instock_darkstores_percentage: Math.round(instockPercentage * 100) / 100,
                total_darkstores: Math.round(avgTotalDarkstores),
                total_stock: totalStock,
                days_of_stock: Math.round(daysOfStock * 100) / 100,
                out_of_stock_flag: outOfStockFlag
            });
        });

        // Apply sorting
        if (sortBy) {
            const sortKey = getSortKey(sortBy);
            if (sortKey) {
                skuListData.sort((a, b) => {
                    const aVal = a[sortKey];
                    const bVal = b[sortKey];
                    
                    if (sortOrder.toUpperCase() === 'DESC') {
                        return bVal > aVal ? 1 : bVal < aVal ? -1 : 0;
                    } else {
                        return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                    }
                });
            }
        }

        // Apply pagination
        const startIdx = (pageNum - 1) * pageSizeNum;
        const endIdx = startIdx + pageSizeNum;
        const paginatedData = skuListData.slice(startIdx, endIdx);

        await db.close();

        res.json({
            city: city || null,
            data: paginatedData
        });

    } catch (error) {
        console.error('Error in stock availability endpoint:', error);
        res.status(500).json({
            error: 'Internal server error'
        });
    }
});

// Helper function to get sort key
function getSortKey(sortBy) {
    const sortKeys = {
        'TOTAL STOCK': 'total_stock',
        'INSTOCK DARKSTORES': 'instock_darkstores',
        'TOTAL DARKSTORES': 'total_darkstores',
        'DAYS OF STOCK': 'days_of_stock',
        'SKU': 'sku'
    };
    return sortKeys[sortBy.toUpperCase()];
}

// Health check endpoint
router.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// Root endpoint
router.get('/', (req, res) => {
    res.json({
        message: 'Stock Availability API',
        version: '1.0.0'
    });
});

module.exports = router;
