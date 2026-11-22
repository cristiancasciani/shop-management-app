"""Demo catalogue for Circuito, a fictional electronics shop.

Fields: sku, name, brand, category, cost, price, min_stock, average units sold per day.
"""

CATEGORIES = ['smartphones', 'laptops', 'tablets', 'audio', 'wearables', 'gaming', 'smart_home', 'accessories']

PRODUCTS = [
    # Smartphones
    ('SPH-001', 'iPhone 17 128 GB', 'Apple', 'smartphones', 720.0, 979.0, 4, 0.45),
    ('SPH-002', 'iPhone 17 Pro 256 GB', 'Apple', 'smartphones', 980.0, 1339.0, 3, 0.25),
    ('SPH-003', 'Galaxy S26 256 GB', 'Samsung', 'smartphones', 640.0, 899.0, 4, 0.35),
    ('SPH-004', 'Galaxy A57 128 GB', 'Samsung', 'smartphones', 260.0, 379.0, 5, 0.55),
    ('SPH-005', 'Pixel 11 128 GB', 'Google', 'smartphones', 560.0, 799.0, 3, 0.2),
    ('SPH-006', 'Redmi Note 16 Pro', 'Xiaomi', 'smartphones', 210.0, 319.0, 5, 0.5),
    # Laptops
    ('LAP-001', 'MacBook Air 13" M5', 'Apple', 'laptops', 920.0, 1249.0, 2, 0.15),
    ('LAP-002', 'ThinkPad E14 Gen 7', 'Lenovo', 'laptops', 610.0, 849.0, 2, 0.1),
    ('LAP-003', 'Zenbook 14 OLED', 'ASUS', 'laptops', 690.0, 999.0, 2, 0.1),
    ('LAP-004', 'Aspire 5 15"', 'Acer', 'laptops', 420.0, 599.0, 3, 0.15),
    ('LAP-005', 'Victus 16 Gaming', 'HP', 'laptops', 780.0, 1099.0, 2, 0.08),
    # Tablets
    ('TAB-001', 'iPad 11" 128 GB', 'Apple', 'tablets', 330.0, 449.0, 3, 0.25),
    ('TAB-002', 'Galaxy Tab S10 FE', 'Samsung', 'tablets', 380.0, 529.0, 2, 0.12),
    ('TAB-003', 'Redmi Pad 2', 'Xiaomi', 'tablets', 140.0, 219.0, 4, 0.2),
    # Audio
    ('AUD-001', 'AirPods Pro 3', 'Apple', 'audio', 190.0, 279.0, 6, 0.7),
    ('AUD-002', 'WH-1000XM6', 'Sony', 'audio', 280.0, 399.0, 3, 0.25),
    ('AUD-003', 'Galaxy Buds 4', 'Samsung', 'audio', 110.0, 169.0, 5, 0.4),
    ('AUD-004', 'Flip 7 speaker', 'JBL', 'audio', 85.0, 139.0, 4, 0.35),
    ('AUD-005', 'QuietComfort Ultra', 'Bose', 'audio', 300.0, 449.0, 2, 0.1),
    ('AUD-006', 'Soundcore Q30', 'Anker', 'audio', 45.0, 79.0, 6, 0.45),
    # Wearables
    ('WEA-001', 'Apple Watch Series 11', 'Apple', 'wearables', 310.0, 449.0, 3, 0.2),
    ('WEA-002', 'Galaxy Watch 8', 'Samsung', 'wearables', 210.0, 319.0, 3, 0.15),
    ('WEA-003', 'Smart Band 10', 'Xiaomi', 'wearables', 28.0, 49.0, 8, 0.6),
    ('WEA-004', 'Forerunner 175', 'Garmin', 'wearables', 190.0, 279.0, 2, 0.08),
    # Gaming
    ('GAM-001', 'PlayStation 5 Slim', 'Sony', 'gaming', 390.0, 499.0, 3, 0.25),
    ('GAM-002', 'Nintendo Switch 2', 'Nintendo', 'gaming', 360.0, 469.0, 3, 0.3),
    ('GAM-003', 'DualSense controller', 'Sony', 'gaming', 48.0, 74.0, 6, 0.4),
    ('GAM-004', 'Xbox Series S', 'Microsoft', 'gaming', 230.0, 299.0, 2, 0.1),
    # Smart home
    ('SMH-001', 'Echo Dot 6', 'Amazon', 'smart_home', 32.0, 59.0, 6, 0.4),
    ('SMH-002', 'Nest Cam Indoor', 'Google', 'smart_home', 60.0, 99.0, 3, 0.15),
    ('SMH-003', 'Hue starter kit', 'Philips', 'smart_home', 95.0, 149.0, 3, 0.15),
    ('SMH-004', 'Robot vacuum S8', 'Roborock', 'smart_home', 290.0, 429.0, 2, 0.08),
    # Accessories
    ('ACC-001', 'USB-C cable 2 m', 'Anker', 'accessories', 6.0, 14.9, 20, 1.6),
    ('ACC-002', '65 W GaN charger', 'Anker', 'accessories', 24.0, 44.9, 10, 0.8),
    ('ACC-003', '20 000 mAh power bank', 'Xiaomi', 'accessories', 18.0, 34.9, 10, 0.7),
    ('ACC-004', 'iPhone 17 silicone case', 'Apple', 'accessories', 22.0, 49.0, 10, 0.9),
    ('ACC-005', 'Tempered glass protector', 'Belkin', 'accessories', 4.0, 19.9, 25, 1.9),
    ('ACC-006', 'MX Master 4 mouse', 'Logitech', 'accessories', 70.0, 119.0, 3, 0.2),
    ('ACC-007', 'microSD 256 GB', 'SanDisk', 'accessories', 16.0, 32.9, 8, 0.5),
    ('ACC-008', 'HDMI 2.1 cable 2 m', 'Belkin', 'accessories', 9.0, 24.9, 8, 0.4),
]
