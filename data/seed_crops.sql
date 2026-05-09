USE cropwise_db;

DELETE FROM farm_records;
DELETE FROM crops;
ALTER TABLE crops AUTO_INCREMENT = 1;

INSERT INTO crops
(common_name, botanical_name, category, planting_months, soil_type, water_requirement, harvest_weeks, avg_yield_kg_per_ha, description, image_filename)
VALUES
('Cassava', 'Manihot esculenta', 'Tuber', '[3,4,5,6,9,10]', 'loamy,sandy', 'medium', 36, 18000, 'Cassava is a major staple crop in Lagos and many parts of Nigeria. It tolerates moderate drought and performs well in sandy-loam and loamy soils.', 'crop_1.jpg'),

('Maize', 'Zea mays', 'Cereal', '[3,4,5,6,9,10]', 'loamy,sandy', 'medium', 12, 3500, 'Maize is widely grown during the rainy seasons and performs best in fertile, well-drained loamy soil with moderate rainfall.', 'crop_2.jpg'),

('Okra', 'Abelmoschus esculentus', 'Vegetable', '[3,4,5,6,7,9,10]', 'loamy,sandy', 'medium', 8, 7000, 'Okra is a fast-growing vegetable suitable for Lagos conditions. It grows well in warm weather and moderately fertile soil.', 'crop_3.jpg'),

('Tomato', 'Solanum lycopersicum', 'Vegetable', '[1,2,3,4,9,10,11,12]', 'loamy,sandy', 'medium', 12, 25000, 'Tomato is an important vegetable crop that requires good drainage, sunlight, and careful water management.', 'crop_4.jpg'),

('Pepper', 'Capsicum annuum', 'Vegetable', '[1,2,3,4,9,10,11,12]', 'loamy,sandy', 'medium', 14, 12000, 'Pepper grows well in warm climates and fertile soils. It is suitable for smallholder vegetable production in Lagos.', 'crop_5.jpg'),

('Yam', 'Dioscorea rotundata', 'Tuber', '[3,4,5]', 'loamy,sandy', 'medium', 36, 12000, 'Yam requires loose, well-drained soil and performs well when planted at the beginning of the rainy season.', 'crop_6.jpg'),

('Sweet Potato', 'Ipomoea batatas', 'Tuber', '[3,4,5,6,9,10]', 'loamy,sandy', 'low', 16, 10000, 'Sweet potato is a short-duration root crop that tolerates moderate dry conditions and grows well in sandy-loam soil.', 'crop_7.jpg'),

('Cocoyam', 'Colocasia esculenta', 'Tuber', '[4,5,6,7]', 'loamy,clay', 'high', 32, 8000, 'Cocoyam performs best in moist soils and areas with good rainfall. It is suitable for wetter parts of Lagos farmland.', 'crop_8.jpg'),

('Rice', 'Oryza sativa', 'Cereal', '[4,5,6,7,9]', 'clay,loamy', 'high', 18, 4000, 'Rice requires high moisture and performs well in clay or lowland soils with good water retention.', 'crop_9.jpg'),

('Sorghum', 'Sorghum bicolor', 'Cereal', '[5,6,7]', 'sandy,loamy', 'low', 16, 2500, 'Sorghum is drought-tolerant and can grow in lighter soils, although it is less common in coastal Lagos than maize.', 'crop_10.jpg'),

('Millet', 'Pennisetum glaucum', 'Cereal', '[5,6,7]', 'sandy', 'low', 14, 1800, 'Millet is a drought-tolerant cereal that performs better in sandy soils and low rainfall conditions.', 'crop_11.jpg'),

('Cowpea', 'Vigna unguiculata', 'Legume', '[3,4,5,8,9,10]', 'sandy,loamy', 'low', 10, 1500, 'Cowpea improves soil fertility through nitrogen fixation and grows well in warm conditions with moderate rainfall.', 'crop_12.jpg'),

('Soybean', 'Glycine max', 'Legume', '[5,6,7]', 'loamy', 'medium', 16, 2500, 'Soybean is a protein-rich legume that grows best in fertile loamy soils with steady rainfall.', 'crop_13.jpg'),

('Groundnut', 'Arachis hypogaea', 'Legume', '[4,5,6,9]', 'sandy,loamy', 'low', 16, 2000, 'Groundnut grows well in sandy-loam soil and requires good drainage for pod development.', 'crop_14.jpg'),

('Lima Bean', 'Phaseolus lunatus', 'Legume', '[3,4,5,9,10]', 'loamy', 'medium', 14, 1800, 'Lima bean is a useful legume crop for warm climates and benefits from fertile, well-drained soil.', 'crop_15.jpg'),

('Waterleaf', 'Talinum triangulare', 'Vegetable', '[3,4,5,6,7,8,9,10,11]', 'loamy,clay', 'high', 6, 9000, 'Waterleaf is a leafy vegetable that grows quickly in moist, fertile soil and is popular in southern Nigeria.', 'crop_16.jpg'),

('Amaranth', 'Amaranthus hybridus', 'Vegetable', '[3,4,5,6,7,9,10]', 'loamy', 'medium', 5, 8000, 'Amaranth, also called efo tete, is a fast-growing leafy vegetable suitable for urban and peri-urban farms.', 'crop_17.jpg'),

('Fluted Pumpkin', 'Telfairia occidentalis', 'Vegetable', '[3,4,5,6,9,10]', 'loamy', 'medium', 12, 10000, 'Fluted pumpkin, known as ugu, is widely cultivated for its nutritious leaves and performs best in fertile loamy soil.', 'crop_18.jpg'),

('Jute Leaf', 'Corchorus olitorius', 'Vegetable', '[3,4,5,6,7,9]', 'loamy,clay', 'medium', 6, 7000, 'Jute leaf, known as ewedu, is popular in Lagos diets and grows well in warm moist soil.', 'crop_19.jpg'),

('African Eggplant', 'Solanum aethiopicum', 'Vegetable', '[3,4,5,9,10]', 'loamy,sandy', 'medium', 14, 9000, 'African eggplant is a vegetable crop suitable for tropical environments and smallholder farms.', 'crop_20.jpg'),

('Plantain', 'Musa paradisiaca', 'Fruit', '[3,4,5,6,9,10]', 'loamy,clay', 'high', 48, 20000, 'Plantain requires moisture, fertile soil, and warm conditions. It is suitable for humid parts of Lagos.', 'crop_21.jpg'),

('Banana', 'Musa acuminata', 'Fruit', '[3,4,5,6,9,10]', 'loamy,clay', 'high', 44, 25000, 'Banana grows well in fertile, moist soils and benefits from consistent water availability.', 'crop_22.jpg'),

('Pawpaw', 'Carica papaya', 'Fruit', '[3,4,5,6,9,10]', 'loamy,sandy', 'medium', 36, 30000, 'Pawpaw is a tropical fruit crop that grows well in well-drained soil and warm climates.', 'crop_23.jpg'),

('Pineapple', 'Ananas comosus', 'Fruit', '[3,4,5,6,9,10]', 'sandy,loamy', 'low', 72, 40000, 'Pineapple performs well in sandy-loam soil and can tolerate lower water conditions once established.', 'crop_24.jpg'),

('Mango', 'Mangifera indica', 'Fruit', '[3,4,5,6]', 'loamy,sandy', 'medium', 156, 10000, 'Mango is a perennial fruit tree that requires space, sunlight, and well-drained soil.', 'crop_25.jpg'),

('Watermelon', 'Citrullus lanatus', 'Fruit', '[1,2,3,4,9,10,11,12]', 'sandy,loamy', 'medium', 12, 20000, 'Watermelon performs well in warm weather and sandy-loam soils with good drainage.', 'crop_26.jpg'),

('Oil Palm', 'Elaeis guineensis', 'Tree Crop', '[3,4,5,6,9,10]', 'loamy,clay', 'high', 156, 12000, 'Oil palm is a long-term tree crop suitable for humid tropical areas with deep fertile soil.', 'crop_27.jpg'),

('Coconut', 'Cocos nucifera', 'Tree Crop', '[3,4,5,6,9,10]', 'sandy,loamy', 'medium', 208, 8000, 'Coconut is suitable for coastal sandy soils and humid conditions, making it relevant to parts of Lagos.', 'crop_28.jpg'),

('Breadfruit', 'Treculia africana', 'Tree Crop', '[3,4,5,6]', 'loamy', 'medium', 208, 7000, 'Breadfruit is a perennial food tree that grows in humid tropical climates and fertile soils.', 'crop_29.jpg'),

('Ginger', 'Zingiber officinale', 'Spice', '[3,4,5]', 'loamy', 'medium', 36, 6000, 'Ginger requires warm conditions, partial shade, and fertile soil with good drainage.', 'crop_30.jpg'),

('Garlic', 'Allium sativum', 'Spice', '[10,11,12,1]', 'loamy,sandy', 'low', 20, 5000, 'Garlic performs better in cooler dry-season conditions with well-drained soil and controlled irrigation.', 'crop_31.jpg'),

('Onion', 'Allium cepa', 'Spice', '[10,11,12,1,2]', 'sandy,loamy', 'low', 16, 12000, 'Onion is suitable for dry-season vegetable farming where irrigation is available and soil drains well.', 'crop_32.jpg'),

('Cucumber', 'Cucumis sativus', 'Vegetable', '[1,2,3,4,9,10,11,12]', 'loamy,sandy', 'medium', 8, 18000, 'Cucumber is a short-duration vegetable crop that performs well with good drainage and regular watering.', 'crop_33.jpg'),

('Garden Egg', 'Solanum melongena', 'Vegetable', '[3,4,5,9,10]', 'loamy,sandy', 'medium', 14, 10000, 'Garden egg grows well in warm climates and is suitable for small-scale vegetable farming.', 'crop_34.jpg'),

('Lettuce', 'Lactuca sativa', 'Vegetable', '[11,12,1,2]', 'loamy', 'medium', 7, 10000, 'Lettuce grows best in cooler periods and fertile soil with moderate watering.', 'crop_35.jpg'),

('Cabbage', 'Brassica oleracea var. capitata', 'Vegetable', '[10,11,12,1,2]', 'loamy', 'medium', 12, 25000, 'Cabbage is better suited to cooler dry-season production with irrigation and good soil fertility.', 'crop_36.jpg'),

('Carrot', 'Daucus carota', 'Vegetable', '[10,11,12,1,2]', 'sandy,loamy', 'low', 12, 18000, 'Carrot requires loose soil for root formation and performs best in cooler dry-season conditions.', 'crop_37.jpg'),

('Spinach', 'Spinacia oleracea', 'Vegetable', '[10,11,12,1,2]', 'loamy', 'medium', 6, 9000, 'Spinach is a leafy vegetable that grows well in cooler periods and fertile loamy soil.', 'crop_38.jpg'),

('Bitter Leaf', 'Vernonia amygdalina', 'Vegetable', '[3,4,5,6,9,10]', 'loamy', 'medium', 12, 9000, 'Bitter leaf is a hardy leafy vegetable used widely in Nigerian cooking and grows well in tropical climates.', 'crop_39.jpg'),

('Scent Leaf', 'Ocimum gratissimum', 'Spice', '[3,4,5,6,9,10]', 'loamy,sandy', 'medium', 8, 5000, 'Scent leaf is an aromatic herb used for food and medicinal purposes. It grows well in warm conditions.', 'crop_40.jpg');