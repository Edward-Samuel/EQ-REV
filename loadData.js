const fs = require('fs');
const csv = require('csv-parser');
const Database = require('./database');
const path = require('path');

async function loadDataFromCSV() {
    const db = new Database();
    
    try {
        // Connect to database
        await db.connect();
        
        // Create table
        await db.createTable();
        
        // Clear existing data
        await db.clearData();
        
        // Read and parse CSV file
        const csvFilePath = path.join(__dirname, 'stock_data.csv');
        
        if (!fs.existsSync(csvFilePath)) {
            throw new Error(`CSV file not found: ${csvFilePath}`);
        }

        console.log('Loading data from CSV file...');
        
        const records = [];
        
        await new Promise((resolve, reject) => {
            fs.createReadStream(csvFilePath)
                .pipe(csv())
                .on('data', (row) => {
                    // Convert date format from M/D/YYYY to YYYY-MM-DD
                    const dateParts = row.date.split('/');
                    const formattedDate = `${dateParts[2]}-${dateParts[0].padStart(2, '0')}-${dateParts[1].padStart(2, '0')}`;
                    
                    const record = {
                        date: formattedDate,
                        city_name: row.city_name,
                        product_id: row.product_id,
                        product_name: row.product_name,
                        category: row.category,
                        total_orders: parseInt(row.total_orders),
                        total_sales: parseFloat(row.total_sales),
                        stock_quantity: parseInt(row.stock_quantity),
                        instock_darkstores: parseInt(row.instock_darkstores),
                        oos_darkstores: parseInt(row.OOS_darkstores),
                        total_darkstores: parseInt(row.total_darkstores)
                    };
                    
                    records.push(record);
                })
                .on('end', () => {
                    console.log(`Parsed ${records.length} records from CSV`);
                    resolve();
                })
                .on('error', (err) => {
                    console.error('Error reading CSV file:', err);
                    reject(err);
                });
        });

        // Insert records into database
        console.log('Inserting records into database...');
        let insertedCount = 0;
        
        for (const record of records) {
            try {
                await db.insertRecord(record);
                insertedCount++;
                
                if (insertedCount % 100 === 0) {
                    console.log(`Inserted ${insertedCount} records...`);
                }
            } catch (err) {
                console.error('Error inserting record:', err);
            }
        }
        
        console.log(`Successfully loaded ${insertedCount} records into database`);
        
    } catch (error) {
        console.error('Error loading data:', error);
    } finally {
        await db.close();
    }
}

// Run if called directly
if (require.main === module) {
    loadDataFromCSV()
        .then(() => {
            console.log('Data loading completed');
            process.exit(0);
        })
        .catch((err) => {
            console.error('Data loading failed:', err);
            process.exit(1);
        });
}

module.exports = loadDataFromCSV;
