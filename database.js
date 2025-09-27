const sqlite3 = require('sqlite3').verbose();
const path = require('path');

class Database {
    constructor() {
        this.db = null;
    }

    async connect() {
        return new Promise((resolve, reject) => {
            const dbPath = path.join(__dirname, 'stock_data.db');
            this.db = new sqlite3.Database(dbPath, (err) => {
                if (err) {
                    console.error('Error opening database:', err.message);
                    reject(err);
                } else {
                    console.log('Connected to SQLite database');
                    resolve();
                }
            });
        });
    }

    async createTable() {
        return new Promise((resolve, reject) => {
            const createTableSQL = `
                CREATE TABLE IF NOT EXISTS stock_data (
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
                )
            `;

            this.db.run(createTableSQL, (err) => {
                if (err) {
                    console.error('Error creating table:', err.message);
                    reject(err);
                } else {
                    console.log('Table created or already exists');
                    resolve();
                }
            });
        });
    }

    async clearData() {
        return new Promise((resolve, reject) => {
            this.db.run('DELETE FROM stock_data', (err) => {
                if (err) {
                    console.error('Error clearing data:', err.message);
                    reject(err);
                } else {
                    console.log('Data cleared from table');
                    resolve();
                }
            });
        });
    }

    async insertRecord(record) {
        return new Promise((resolve, reject) => {
            const insertSQL = `
                INSERT INTO stock_data (
                    date, city_name, product_id, product_name, category,
                    total_orders, total_sales, stock_quantity, instock_darkstores,
                    oos_darkstores, total_darkstores
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            `;

            const values = [
                record.date,
                record.city_name,
                record.product_id,
                record.product_name,
                record.category,
                record.total_orders,
                record.total_sales,
                record.stock_quantity,
                record.instock_darkstores,
                record.oos_darkstores,
                record.total_darkstores
            ];

            this.db.run(insertSQL, values, function(err) {
                if (err) {
                    console.error('Error inserting record:', err.message);
                    reject(err);
                } else {
                    resolve(this.lastID);
                }
            });
        });
    }

    async queryStockData(filters) {
        return new Promise((resolve, reject) => {
            let sql = 'SELECT * FROM stock_data WHERE 1=1';
            const params = [];

            // Apply filters
            if (filters.city) {
                sql += ' AND city_name = ?';
                params.push(filters.city);
            }

            if (filters.skus && filters.skus.length > 0) {
                const placeholders = filters.skus.map(() => '?').join(',');
                sql += ` AND product_id IN (${placeholders})`;
                params.push(...filters.skus);
            }

            if (filters.dateFrom) {
                sql += ' AND date >= ?';
                params.push(filters.dateFrom);
            }

            if (filters.dateTo) {
                sql += ' AND date <= ?';
                params.push(filters.dateTo);
            }

            if (filters.search) {
                sql += ' AND (product_name LIKE ? OR product_id LIKE ? OR category LIKE ?)';
                const searchTerm = `%${filters.search}%`;
                params.push(searchTerm, searchTerm, searchTerm);
            }

            // Apply sorting
            if (filters.sortBy) {
                const sortColumn = this.getSortColumn(filters.sortBy);
                if (sortColumn) {
                    const sortOrder = filters.sortOrder === 'DESC' ? 'DESC' : 'ASC';
                    sql += ` ORDER BY ${sortColumn} ${sortOrder}`;
                }
            }

            this.db.all(sql, params, (err, rows) => {
                if (err) {
                    console.error('Error querying data:', err.message);
                    reject(err);
                } else {
                    resolve(rows);
                }
            });
        });
    }

    getSortColumn(sortBy) {
        const sortColumns = {
            'TOTAL STOCK': 'stock_quantity',
            'TOTAL SALES': 'total_sales',
            'INSTOCK DARKSTORES': 'instock_darkstores',
            'TOTAL DARKSTORES': 'total_darkstores',
            'DATE': 'date',
            'CITY': 'city_name',
            'PRODUCT': 'product_name'
        };
        return sortColumns[sortBy.toUpperCase()];
    }

    async close() {
        return new Promise((resolve, reject) => {
            if (this.db) {
                this.db.close((err) => {
                    if (err) {
                        console.error('Error closing database:', err.message);
                        reject(err);
                    } else {
                        console.log('Database connection closed');
                        resolve();
                    }
                });
            } else {
                resolve();
            }
        });
    }
}

module.exports = Database;
