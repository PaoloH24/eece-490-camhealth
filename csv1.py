#%%
import csv
from io import StringIO
import math
import os  # <--- Import os module

# Paste the input CSV data here as a multi-line string
# (This data represents the *original* input format)
csv_data = """Label,Calories,Unit
Omelette ,200,serving
Omelette ,1.6,gram
Omelette Cheese,300,serving
Omelette Cheese,2,gram
Omelette Veggie,250,serving
Omelette Veggie,1.7,gram
Omelette Western,350,serving
Omelette Western,2.2,gram
Scrambled Eggs,180,serving
Scrambled Eggs,1.7,gram
Scrambled Eggs with Cheese,280,serving
Scrambled Eggs with Cheese,2.2,gram
Samosa, 3.0, gram  
Fried Egg,90,serving
Fried Egg,1.8,gram
Boiled Egg,75,serving
Boiled Egg,1.5,gram
Baby Back Ribs, 3.2, gram
Baby Back Ribs, 640, serving
Baklava, 4.1, gram
Baklava, 360, serving
Beet Salad, 0.6, gram  
Caesar Salad, 1.2, gram  
Chocolate Mousse, 2.7, gram  
Churros, 3.7, gram  
Cupcakes, 3.9, gram  
Donuts, 4.1, gram  
Falafel, 3.3, gram  
Grilled Salmon, 2.0, gram  
French Toast, 2.3, gram  
Hot Dog, 2.9, gram  
Hummus, 2.5, gram  
Ice Cream, 2.1, gram  
Nachos, 5.0, gram  
Poached Egg,70,serving
Poached Egg,1.4,gram
Eggs Benedict,700,serving
Eggs Benedict,2.5,gram
Pancakes Plain,150,serving
Pancakes Plain,2.5,gram
Pancakes with Syrup,350,serving
Waffles ,200,serving
Waffles ,2.8,gram
Waffles with Syrup,400,serving
French Toast Slice Plain,150,serving
French Toast Slice Plain,2.2,gram
French Toast with Syrup,300,serving
Cereal Generic Flakes,120,serving
Cereal Generic Flakes,3.8,gram
Cereal Granola,200,serving
Cereal Granola,4.5,gram
Cereal Shredded Wheat,160,serving
Cereal Shredded Wheat,3.5,gram
Cereal with Milk,250,serving
Oatmeal Plain,150,serving
Oatmeal Plain,0.6,gram
Oatmeal with Brown Sugar,200,serving
Oatmeal with Fruit,220,serving
Bagel Plain,300,serving
Bagel Plain,2.8,gram
Bagel with Cream Cheese,400,serving
Toast White Slice,80,serving
Toast White Slice,2.9,gram
Toast Whole Wheat Slice,75,serving
Toast Whole Wheat Slice,2.7,gram
Toast with Butter,150,serving
Toast with Jam,130,serving
English Muffin Plain,130,serving
English Muffin Plain,2.4,gram
Croissant Plain,250,serving
Croissant Plain,4.4,gram
Muffin Blueberry,350,serving
Muffin Blueberry,3.5,gram
Muffin Bran,300,serving
Muffin Bran,3,gram
Breakfast Burrito,500,serving
Breakfast Burrito,2,gram
Breakfast Sausage Link,80,serving
Breakfast Sausage Link,3.2,gram
Bacon Strip,45,serving
Bacon Strip,5,gram
Egg,1.5,gram
Tomato Soup,150,serving
Tomato Soup,0.6,gram
Cream of Tomato Soup,200,serving
Cream of Tomato Soup,0.8,gram
Chicken Noodle Soup,120,serving
Chicken Noodle Soup,0.5,gram
Cream of Chicken Soup,180,serving
Cream of Chicken Soup,0.7,gram
Lentil Soup,180,serving
Lentil Soup,0.7,gram
Minestrone Soup,150,serving
Minestrone Soup,0.6,gram
Vegetable Soup,100,serving
Vegetable Soup,0.4,gram
Cream of Mushroom Soup,180,serving
Cream of Mushroom Soup,0.7,gram
French Onion Soup,300,serving
French Onion Soup,0.8,gram
Clam Chowder New England,250,serving
Clam Chowder New England,1,gram
Clam Chowder Manhattan,150,serving
Clam Chowder Manhattan,0.6,gram
Beef Stew,350,serving
Beef Stew,1,gram
Chicken Stew,300,serving
Chicken Stew,0.9,gram
Irish Stew,400,serving
Irish Stew,1.1,gram
Chili con Carne,400,serving
Chili con Carne,1.2,gram
Vegetarian Chili,300,serving
Vegetarian Chili,0.9,gram
Pho Soup Beef,450,serving
Pho Soup,0.5,gram
Pho Soup Chicken,400,serving
Ramen Noodles Pork,500,serving
Ramen Noodles,0.7,gram
Ramen Noodles Miso,450,serving
Tom Yum Soup,100,serving
Tom Yum Soup,0.4,gram
Soup,0.6,gram
Stew,1,gram
Green Salad Simple,50,serving
Green Salad Simple,0.3,gram
Caesar Salad Plain,150,serving
Caesar Salad Plain,1,gram
Chicken Caesar Salad,350,serving
Chicken Caesar Salad,1.5,gram
Greek Salad,250,serving
Greek Salad,1.2,gram
Cobb Salad,400,serving
Cobb Salad,1.8,gram
Chef Salad,350,serving
Chef Salad,1.6,gram
Tuna Salad Plate,300,serving
Tuna Salad,2,gram
Chicken Salad Plate,320,serving
Chicken Salad,2.1,gram
Spinach Salad,150,serving
Spinach Salad,1,gram
Taco Salad,500,serving
Taco Salad,1.8,gram
Caprese Salad,300,serving
Caprese Salad,1.5,gram
Waldorf Salad,350,serving
Waldorf Salad,1.8,gram
Potato Salad,300,serving
Potato Salad,1.5,gram
Macaroni Salad,350,serving
Macaroni Salad,1.7,gram
Coleslaw Creamy,180,serving
Coleslaw Creamy,1.5,gram
Coleslaw Vinegar,100,serving
Coleslaw Vinegar,0.8,gram
Tabbouleh,120,serving
Tabbouleh,1,gram
Quinoa Salad,300,serving
Quinoa Salad,1.2,gram
Salad,0.4,gram
Burger Plain,450,serving
Burger Plain,2.9,gram
Cheeseburger,550,serving
Cheeseburger,3.1,gram
Lebanese Burger, 750, serving
Bacon Cheeseburger,650,serving
Bacon Cheeseburger,3.3,gram
Veggie Burger,400,serving
Veggie Burger,2.5,gram
Chicken Sandwich Grilled,400,serving
Chicken Sandwich Grilled,2.2,gram
Chicken Sandwich Fried,500,serving
Chicken Sandwich Fried,2.6,gram
Fish Sandwich Fried,480,serving
Fish Sandwich Fried,2.5,gram
Pulled Pork Sandwich,550,serving
Pulled Pork Sandwich,2.4,gram
Philly Cheesesteak,600,serving
Philly Cheesesteak,2.8,gram
Club Sandwich,600,serving
Club Sandwich,2.5,gram
BLT Sandwich,400,serving
BLT Sandwich,2.7,gram
Turkey Sandwich,350,serving
Turkey Sandwich,2,gram
Ham Sandwich,370,serving
Ham Sandwich,2.1,gram
Roast Beef Sandwich,400,serving
Roast Beef Sandwich,2.2,gram
Tuna Salad Sandwich,400,serving
Tuna Salad Sandwich,2.2,gram
Chicken Salad Sandwich,420,serving
Chicken Salad Sandwich,2.3,gram
Egg Salad Sandwich,380,serving
Egg Salad Sandwich,2.1,gram
Grilled Cheese Sandwich,400,serving
Grilled Cheese Sandwich,3,gram
Peanut Butter Jelly Sandwich,350,serving
Peanut Butter Jelly Sandwich,3.5,gram
Falafel Wrap,450,serving
Falafel Wrap,1.8,gram
Shawarma Wrap Chicken,550,serving
Shawarma Wrap,2.2,gram
Shawarma Wrap Beef,600,serving
Gyro,500,serving
Gyro,2.4,gram
Chicken Caesar Wrap,500,serving
Chicken Caesar Wrap,2,gram
Veggie Wrap,350,serving
Veggie Wrap,1.5,gram
Burrito Bean and Cheese,500,serving
Burrito Bean and Cheese,1.6,gram
Burrito Chicken,650,serving
Burrito Chicken,1.7,gram
Burrito Beef,700,serving
Burrito Beef,1.8,gram
Taco Hard Shell Beef,180,serving
Taco Hard Shell Beef,2.4,gram
Taco Soft Shell Chicken,200,serving
Taco Soft Shell Chicken,2.1,gram
Quesadilla Cheese,400,serving
Quesadilla Cheese,3.3,gram
Quesadilla Chicken,500,serving
Quesadilla Chicken,2.8,gram
Sandwich,2.5,gram
Burger,2.9,gram
Wrap,2.2,gram
Burrito,1.8,gram
Taco,2.3,gram
Quesadilla,3,gram
Pizza Slice Cheese,280,serving
Pizza Slice Cheese,2.7,gram
Pizza Slice Pepperoni,320,serving
Pizza Slice Pepperoni,2.9,gram
Pizza Slice Margherita,270,serving
Pizza Slice Margherita,2.6,gram
Pizza Slice Veggie,260,serving
Pizza Slice Veggie,2.5,gram
Pizza Slice Meat Lovers,350,serving
Pizza Slice Meat Lovers,3.1,gram
Pizza Slice Hawaiian,300,serving
Pizza Slice Hawaiian,2.8,gram
Pizza Slice Supreme,340,serving
Pizza Slice Supreme,3,gram
Pizza Slice BBQ Chicken,330,serving
Pizza Slice BBQ Chicken,2.9,gram
Pizza Slice White,300,serving
Pizza Slice White,2.9,gram
Personal Pizza Cheese,600,serving
Personal Pizza,2.7,gram
Pizza,2.7,gram
Grilled Chicken Breast Plain,280,serving
Grilled Chicken Breast Plain,1.6,gram
Roasted Chicken Quarter,350,serving
Roasted Chicken,2,gram
Fried Chicken Piece,380,serving
Fried Chicken Piece,2.8,gram
Chicken Stir-fry,450,serving
Chicken Stir-fry,1.5,gram
Chicken Parmesan,550,serving
Chicken Parmesan,2.2,gram
Chicken Piccata,400,serving
Chicken Piccata,2,gram
Chicken Marsala,450,serving
Chicken Marsala,2.1,gram
Chicken Curry,400,serving
Chicken Curry,1.4,gram
Chicken Tikka Masala,450,serving
Chicken Tikka Masala,1.5,gram
Chicken Teriyaki,400,serving
Chicken Teriyaki,2,gram
Chicken Wings Buffalo,90,serving
Chicken Wings,3,gram
Chicken Wings BBQ,85,serving
Turkey Breast Roasted,250,serving
Turkey Breast Roasted,1.5,gram
Ground Turkey Cooked,220,serving
Ground Turkey Cooked,2.2,gram
Chicken,1.9,gram
Turkey,1.6,gram
Steak ,600,serving
Steak ,2.6,gram
Roast Beef Slice,100,serving
Roast Beef,2.4,gram
Beef Stir-fry,500,serving
Beef Stir-fry,1.7,gram
Beef Stroganoff,550,serving
Beef Stroganoff,1.8,gram
Meatloaf Slice,300,serving
Meatloaf,2.5,gram
Shepherds Pie,500,serving
Shepherds Pie,1.6,gram
Hamburger Patty Cooked,300,serving
Hamburger Patty Cooked,2.7,gram
Pork Chop Grilled/Baked,400,serving
Pork Chop Cooked,2.5,gram
Pork Chop Fried,500,serving
Pork Chop Fried,3,gram
Pork Tenderloin Roasted,250,serving
Pork Tenderloin Roasted,1.8,gram
Pulled Pork,300,serving
Pulled Pork,2.4,gram
Ham Slice Baked,150,serving
Ham Cooked,1.8,gram
Sausage Italian Cooked,300,serving
Sausage Cooked,3.3,gram
Bratwurst Cooked,330,serving
Bratwurst Cooked,3.1,gram
Lamb Chop Grilled,300,serving
Lamb Chop Cooked,2.8,gram
Lamb Curry,450,serving
Lamb Curry,1.6,gram
Lamb Kebab,180,serving
Kebab Meat,2.5,gram
Beef,2.5,gram
Pork,2.6,gram
Lamb,2.8,gram
Sausage,3.3,gram
Salmon Grilled/Baked,400,serving
Salmon Cooked,2,gram
Tuna Steak Grilled,300,serving
Tuna Cooked,1.4,gram
Cod Baked/Broiled,200,serving
Cod Cooked,1,gram
Tilapia Baked/Broiled,180,serving
Tilapia Cooked,1,gram
Fried Fish Fillet,350,serving
Fried Fish Fillet,2.2,gram
Fish and Chips,800,serving
Fish and Chips,2.5,gram
Fish Tacos Grilled,250,serving
Fish Taco,2,gram
Fish Tacos Fried,300,serving
Shrimp Scampi,400,serving
Shrimp Scampi,1.5,gram
Grilled Shrimp Skewer,100,serving
Shrimp Cooked,1,gram
Fried Shrimp,250,serving
Fried Shrimp,2.5,gram
Crab Cakes,200,serving
Crab Cakes,1.8,gram
Lobster Tail Steamed,150,serving
Lobster Cooked,1,gram
Scallops Seared,150,serving
Scallops Cooked,1.1,gram
Fish,1.8,gram
Shrimp,1,gram
Tofu Stir-fry,350,serving
Tofu Stir-fry,1.2,gram
Tofu Scramble,250,serving
Tofu Scramble,1.4,gram
Baked Tofu,200,serving
Tofu Baked,1.5,gram
Tempeh Baked/Grilled,220,serving
Tempeh Cooked,1.9,gram
Lentil Loaf Slice,250,serving
Lentil Loaf,1.8,gram
Black Bean Burger Patty,150,serving
Black Bean Burger Patty,1.5,gram
Vegetable Curry,300,serving
Vegetable Curry,1,gram
Chickpea Curry,350,serving
Chickpea Curry,1.1,gram
Stuffed Bell Pepper Veggie,250,serving
Stuffed Bell Pepper,1,gram
Vegetable Lasagna Slice,400,serving
Vegetable Lasagna,1.5,gram
Eggplant Parmesan,450,serving
Eggplant Parmesan,1.8,gram
Falafel Plate,400,serving
Falafel,2.5,gram
Tofu,1.2,gram
Tempeh,1.9,gram
Curry,1.4,gram
Pasta Plain Cooked,200,serving
Pasta Plain Cooked,1.3,gram
Pasta Bolognese Dish,550,serving
Pasta Bolognese Dish,1.7,gram
Pasta Carbonara Dish,650,serving
Pasta Carbonara Dish,2,gram
Pasta Pesto Dish,500,serving
Pasta Pesto Dish,1.8,gram
Pasta Alfredo Dish,700,serving
Pasta Alfredo Dish,2.2,gram
Pasta Marinara Dish,400,serving
Pasta Marinara Dish,1.2,gram
Lasagna Meat Slice,450,serving
Lasagna,1.7,gram
Mac and Cheese Homemade,500,serving
Mac and Cheese,2,gram
Rice White Cooked,200,serving
Rice White Cooked,1.3,gram
Rice Brown Cooked,220,serving
Rice Brown Cooked,1.3,gram
Fried Rice Chicken,450,serving
Fried Rice,1.8,gram
Fried Rice Veggie,400,serving
Risotto Mushroom,500,serving
Risotto,1.5,gram
Paella Seafood,550,serving
Paella,1.6,gram
Biryani Chicken,500,serving
Biryani,1.7,gram
Biryani Vegetable,450,serving
Quinoa Cooked,220,serving
Quinoa Cooked,1.2,gram
Couscous Cooked,180,serving
Couscous Cooked,1.1,gram
Sushi Roll California,280,serving
Sushi Roll,1.8,gram
Sushi Roll Tuna,250,serving
Sushi Roll Salmon Avocado,320,serving
Nigiri Salmon,60,serving
Nigiri,1.5,gram
Nigiri Tuna,50,serving
Onigiri Tuna Mayo,200,serving
Onigiri,1.6,gram
Pad Thai Chicken,500,serving
Pad Thai,1.5,gram
Pad See Ew Beef,550,serving
Pad See Ew,1.6,gram
Pasta,1.6,gram
Rice,1.3,gram
Quinoa,1.2,gram
French Fries Medium,350,serving
French Fries,3.2,gram
Sweet Potato Fries,300,serving
Sweet Potato Fries,2.8,gram
Mashed Potatoes Plain,200,serving
Mashed Potatoes,1,gram
Mashed Potatoes with Gravy,280,serving
Roasted Potatoes,250,serving
Roasted Potatoes,1.3,gram
Baked Potato Plain,160,serving
Baked Potato,0.9,gram
Baked Potato with Butter Sour Cream,350,serving
Potato Wedges,300,serving
Potato Wedges,1.8,gram
Onion Rings,300,serving
Onion Rings,3.5,gram
Rice White Side,150,serving
Rice Brown Side,160,serving
Rice Pilaf Side,200,serving
Rice Pilaf,1.4,gram
Steamed Vegetables Mixed,80,serving
Steamed Vegetables,0.5,gram
Roasted Vegetables Mixed,150,serving
Roasted Vegetables,0.8,gram
Steamed Broccoli,50,serving
Broccoli Cooked,0.4,gram
Grilled Asparagus,60,serving
Asparagus Cooked,0.4,gram
Creamed Spinach,200,serving
Creamed Spinach,1.5,gram
Sauteed Mushrooms,100,serving
Sauteed Mushrooms,1,gram
Corn on the Cob,100,serving
Corn on the Cob,0.4,gram
Creamed Corn,180,serving
Creamed Corn,1,gram
Baked Beans,150,serving
Baked Beans,1.1,gram
Refried Beans,120,serving
Refried Beans,0.9,gram
Garlic Bread Slice,150,serving
Garlic Bread,3.8,gram
Dinner Roll Plain,100,serving
Dinner Roll,2.8,gram
Cornbread Piece,200,serving
Cornbread,3.2,gram
Pita Bread,170,serving
Pita Bread,2.8,gram
Naan Bread,300,serving
Naan Bread,3.3,gram
Potatoes,1,gram
Apple Medium,95,serving
Apple,0.5,gram
Banana Medium,105,serving
Banana,0.9,gram
Orange Medium,60,serving
Orange,0.4,gram
Grapes Cup,100,serving
Grapes,0.7,gram
Strawberries Cup,50,serving
Strawberries,0.3,gram
Blueberries Cup,85,serving
Blueberries,0.6,gram
Raspberries Cup,65,serving
Raspberries,0.5,gram
Watermelon Wedge,85,serving
Watermelon,0.3,gram
Cantaloupe Wedge,60,serving
Cantaloupe,0.3,gram
Pineapple Chunks Cup,80,serving
Pineapple,0.5,gram
Mango Medium,150,serving
Mango,0.6,gram
Pear Medium,100,serving
Pear,0.6,gram
Peach Medium,60,serving
Peach,0.4,gram
Plum Medium,30,serving
Plum,0.5,gram
Kiwi Fruit,40,serving
Kiwi,0.6,gram
Avocado Half,160,serving
Avocado,1.6,gram
Fruit,0.7,gram
Broccoli Cup Steamed,55,serving
Broccoli,0.3,gram
Carrot Sticks Cup,50,serving
Carrots,0.4,gram
Celery Sticks Cup,15,serving
Celery,0.1,gram
Cucumber Slices Cup,15,serving
Cucumber,0.1,gram
Tomato Medium,25,serving
Tomato,0.2,gram
Cherry Tomatoes Cup,30,serving
Cherry Tomatoes,0.2,gram
Bell Pepper Medium,30,serving
Bell Pepper,0.2,gram
Spinach Cup Raw,10,serving
Spinach Raw,0.2,gram
Spinach Cup Cooked,40,serving
Spinach Cooked,0.4,gram
Lettuce Cup Shredded,5,serving
Lettuce,0.1,gram
Kale Cup Raw,35,serving
Kale,0.3,gram
Green Beans Cup Steamed,45,serving
Green Beans Cooked,0.3,gram
Peas Cup Cooked,120,serving
Peas Cooked,0.8,gram
Corn Kernels Cup,130,serving
Corn Kernels,0.9,gram
Onion Medium Raw,45,serving
Onion Raw,0.4,gram
Mushroom Slices Cup Raw,20,serving
Mushrooms Raw,0.2,gram
Zucchini Slices Cup Raw,20,serving
Zucchini Raw,0.2,gram
Vegetables,0.5,gram
Water,0,serving
Water,0,gram
Coffee Black Cup,2,serving
Coffee,0.01,gram
Tea Black Cup,2,serving
Tea,0.01,gram
Milk Whole Cup,150,serving
Milk Whole,0.6,gram
Milk 2 Percent Cup,120,serving
Milk 2 Percent,0.5,gram
Milk 1 Percent Cup,100,serving
Milk 1 Percent,0.4,gram
Milk Skim Cup,80,serving
Milk Skim,0.3,gram
Soy Milk Plain Cup,100,serving
Soy Milk,0.4,gram
Almond Milk Unsweetened Cup,40,serving
Almond Milk,0.1,gram
Oat Milk Plain Cup,120,serving
Oat Milk,0.5,gram
Orange Juice Cup,110,serving
Orange Juice,0.5,gram
Apple Juice Cup,115,serving
Apple Juice,0.5,gram
Grape Juice Cup,150,serving
Grape Juice,0.6,gram
Cranberry Juice Cocktail Cup,140,serving
Cranberry Juice,0.6,gram
Tomato Juice Cup,40,serving
Tomato Juice,0.2,gram
Lemonade Cup,100,serving
Lemonade,0.4,gram
Iced Tea Unsweetened Cup,2,serving
Iced Tea,0.4,gram
Iced Tea Sweetened Cup,90,serving
Cola Soda Can,140,serving
Cola Soda,0.4,gram
Lemon Lime Soda Can,150,serving
Lemon Lime Soda,0.4,gram
Ginger Ale Can,130,serving
Ginger Ale,0.3,gram
Diet Soda Can,0,serving
Diet Soda,0,gram
Sports Drink Bottle,150,serving
Sports Drink,0.3,gram
Energy Drink Can,110,serving
Energy Drink,0.4,gram
Beer Regular Can,150,serving
Beer,0.4,gram
Beer Light Can,100,serving
Wine Red Glass,125,serving
Wine,0.8,gram
Wine White Glass,120,serving
Liquor Shot,100,serving
Liquor,2.2,gram
Smoothie Fruit,250,serving
Smoothie,0.8,gram
Milkshake Vanilla,400,serving
Milkshake,1.2,gram
Juice,0.5,gram
Soda,0.4,gram
Ice Cream Scoop Vanilla,150,serving
Ice Cream,2.1,gram
Ice Cream Scoop Chocolate,160,serving
Sorbet Scoop,120,serving
Sorbet,1.3,gram
Frozen Yogurt Cup,200,serving
Frozen Yogurt,1,gram
Chocolate Cake Slice,350,serving
Chocolate Cake,3.8,gram
Vanilla Cake Slice,300,serving
Vanilla Cake,3.5,gram
Carrot Cake Slice,400,serving
Carrot Cake,3.6,gram
Cheesecake Slice Plain,400,serving
Cheesecake,3.4,gram
Apple Pie Slice,400,serving
Apple Pie,2.8,gram
Pumpkin Pie Slice,320,serving
Pumpkin Pie,2.5,gram
Pecan Pie Slice,500,serving
Pecan Pie,4,gram
Brownie Fudge,250,serving
Brownie,4,gram
Blondie,230,serving
Blondie,3.8,gram
Chocolate Chip Cookie Large,180,serving
Cookie,4.5,gram
Oatmeal Raisin Cookie Large,160,serving
Sugar Cookie Medium,100,serving
Macaron,80,serving
Macaron,3,gram
Donut Glazed,250,serving
Donut,4,gram
Donut Cake,300,serving
Donut Jelly Filled,280,serving
Cupcake Frosted,300,serving
Cupcake,3.7,gram
Tiramisu Portion,450,serving
Tiramisu,2.5,gram
Creme Brulee,350,serving
Creme Brulee,2,gram
Pudding Cup,150,serving
Pudding,1,gram
Jello Cup,70,serving
Jello,0.6,gram
Fruit Salad Cup,100,serving
Fruit Salad,0.7,gram
Chocolate Bar Standard,220,serving
Chocolate Bar,5.5,gram
Cake,3.7,gram
Pie,3,gram
Oil Olive,8.8,gram
Oil Vegetable,8.8,gram
Oil Coconut,8.6,gram
Oil Avocado,8.8,gram
Oil Peanut,8.8,gram
Oil Sesame,8.8,gram
Oil,8.8,gram
Butter Salted,7.2,gram
Butter Unsalted,7.2,gram
Butter,7.2,gram
Margarine Stick,7.2,gram
Margarine Tub,6,gram
Margarine,7,gram
Lard,9,gram
Ghee,9,gram
Shortening Vegetable,8.8,gram
Cooking Spray,1,gram
Ketchup,1,gram
Mayonnaise,7,gram
Mayonnaise Full Fat,7,gram
Mayonnaise Light,3.5,gram
Mayonnaise Olive Oil,6.5,gram
Aioli,7,gram
Mustard,0.6,gram
Mustard Yellow,0.6,gram
Mustard Dijon,0.7,gram
Mustard Stone Ground,0.8,gram
Mustard Honey,2.5,gram
BBQ Sauce,1.3,gram
BBQ Sauce Original,1.3,gram
BBQ Sauce Honey,1.5,gram
Hot Sauce,0.2,gram
Hot Sauce Cayenne Pepper,0.2,gram
Hot Sauce Chipotle,0.5,gram
Sriracha,1,gram
Sriracha Sauce,1,gram
Gochujang Paste,2.5,gram
Chili Sauce Sweet Thai,1.2,gram
Chili Garlic Sauce,0.8,gram
Soy Sauce,0.6,gram
Soy Sauce Regular,0.6,gram
Soy Sauce Low Sodium,0.5,gram
Tamari,0.7,gram
Teriyaki Sauce,1.5,gram
Hoisin Sauce,2.2,gram
Oyster Sauce,1,gram
Fish Sauce,0.4,gram
Worcestershire Sauce,0.8,gram
Steak Sauce,1,gram
Pesto,5,gram
Pesto Basil,5,gram
Tapenade Olive,3.5,gram
Tahini,5.9,gram
Tahini Paste,5.9,gram
Garlic Sauce,4.2,gram
Garlic Sauce Creamy,4.2,gram
Salsa,0.4,gram
Salsa Pico de Gallo,0.3,gram
Salsa Jarred Mild,0.4,gram
Salsa Verde,0.4,gram
Guacamole,1.8,gram
Marinara Sauce,0.6,gram
Alfredo Sauce,3.5,gram
Alfredo Sauce Jarred,3.5,gram
Vodka Sauce,2.5,gram
Vodka Sauce Jarred,2.5,gram
Gravy,0.8,gram
Gravy Brown,0.7,gram
Gravy Brown Jarred,0.7,gram
Gravy Chicken,0.8,gram
Gravy Chicken Jarred,0.8,gram
Gravy Country White,1.5,gram
Dressing,4,gram
Ranch Dressing,4.5,gram
Ranch Dressing Regular,4.5,gram
Ranch Dressing Light,2.5,gram
Caesar Dressing,5,gram
Caesar Dressing Creamy,5,gram
Caesar Dressing Light,3,gram
Italian Dressing,3.5,gram
Italian Dressing Regular,3.5,gram
Italian Dressing Light,1.5,gram
Vinaigrette,4,gram
Vinaigrette Balsamic,3,gram
Vinaigrette Raspberry,2.5,gram
Vinaigrette Generic Oil Vinegar,4,gram
Blue Cheese Dressing,5,gram
Thousand Island Dressing,4,gram
French Dressing,4.5,gram
Honey Dijon Dressing,4,gram
Poppy Seed Dressing,4.2,gram
Sesame Ginger Dressing,3.8,gram
Milk,0.5,gram
Milk Whole,0.6,gram
Milk 2 Percent,0.5,gram
Milk Skim,0.3,gram
Soy Milk,0.4,gram
Soy Milk Unsweetened,0.3,gram
Almond Milk,0.2,gram
Almond Milk Unsweetened,0.1,gram
Oat Milk,0.5,gram
Oat Milk Plain,0.5,gram
Cheese,4,gram
Cheese Cheddar,4,gram
Cheese Mozzarella,3,gram
Cheese Mozzarella Part Skim,2.8,gram
Cheese Mozzarella Whole Milk,3.2,gram
Cheese Swiss,3.8,gram
Cheese Provolone,3.5,gram
Cheese American,3.7,gram
Cheese Parmesan,4.3,gram
Cheese Parmesan Grated,4.3,gram
Cheese Feta,2.6,gram
Cheese Goat,3.6,gram
Cheese Goat Soft,3.6,gram
Cheese Blue,3.5,gram
Cheese Ricotta,1.5,gram
Cheese Ricotta Whole Milk,1.7,gram
Cheese Ricotta Part Skim,1.4,gram
Cheese Cottage,1,gram
Cheese Cottage 4 Percent,1,gram
Cheese Cottage 2 Percent,0.9,gram
Cream Cheese,3.4,gram
Cream Cheese Regular,3.4,gram
Cream Cheese Light,2,gram
Sour Cream,2,gram
Sour Cream Regular,2,gram
Sour Cream Light,1.2,gram
Yogurt,0.6,gram
Yogurt Plain,0.6,gram
Yogurt Plain Whole Milk,0.7,gram
Yogurt Plain Low Fat,0.6,gram
Yogurt Plain Non Fat,0.5,gram
Greek Yogurt,1,gram
Greek Yogurt Plain,1,gram
Greek Yogurt Plain Full Fat,1.3,gram
Greek Yogurt Plain 2 Percent,1,gram
Greek Yogurt Plain Non Fat,0.6,gram
Cream,3.4,gram
Cream Heavy,3.4,gram
Cream Light,2,gram
Half and Half,1.3,gram
Half and Half Cream,1.3,gram
Evaporated Milk,1.4,gram
Condensed Milk Sweetened,3.2,gram
Labneh,1.3,gram
Mascarpone,4.5,gram
Hummus,2.7,gram
Peanut Butter,6,gram
Peanut Butter Natural,5.9,gram
Peanut Butter Regular,6,gram
Almond Butter,6.1,gram
Cashew Butter,6,gram
Sunflower Seed Butter,6.1,gram
Jam,2.7,gram
Jelly,2.7,gram
Marmalade,2.8,gram
Honey,3,gram
Maple Syrup,2.7,gram
Maple Syrup Pure,2.7,gram
Agave Nectar,3.1,gram
Nutella,5.3,gram
Nutella Hazelnut Spread,5.3,gram
Apple Butter,1.5,gram
Sugar,4,gram
Sugar White Granulated,4,gram
Sugar Brown,3.8,gram
Sugar Brown Packed,3.8,gram
Sugar Powdered Confectioners,4,gram
Sugar Raw Turbinado,3.9,gram
Coconut Sugar,3.8,gram
Molasses,2.9,gram
Corn Syrup,3.3,gram
Corn Syrup Light,3.3,gram
Simple Syrup,2.5,gram
Nuts,6,gram
Almonds,5.8,gram
Almonds Raw,5.8,gram
Almonds Roasted,5.9,gram
Walnuts,6.5,gram
Peanuts,5.7,gram
Peanuts Raw,5.7,gram
Peanuts Roasted,5.8,gram
Cashews,5.6,gram
Cashews Raw,5.5,gram
Cashews Roasted,5.7,gram
Pecans,6.9,gram
Pistachios,5.6,gram
Pistachios Shelled,5.6,gram
Macadamia Nuts,7.2,gram
Brazil Nuts,6.6,gram
Hazelnuts,6.3,gram
Mixed Nuts,6,gram
Mixed Nuts Roasted Salted,6,gram
Seeds,5.5,gram
Chia Seeds,4.9,gram
Flax Seeds,5.3,gram
Flax Seeds Whole,5.3,gram
Flax Seeds Ground,5.3,gram
Pumpkin Seeds,5.6,gram
Pumpkin Seeds Pepitas,5.6,gram
Sunflower Seeds,5.8,gram
Sunflower Seeds Kernels,5.8,gram
Sesame Seeds,5.7,gram
Hemp Seeds,5.5,gram
Hemp Seeds Hulled,5.5,gram
Flour,3.6,gram
Flour All Purpose White,3.6,gram
Flour Whole Wheat,3.4,gram
Flour Almond,5.8,gram
Flour Coconut,4.4,gram
Corn Starch,3.8,gram
Baking Soda,0,gram
Baking Powder,0.5,gram
Cocoa Powder,2.3,gram
Cocoa Powder Unsweetened,2.3,gram
Chocolate Chips,5.1,gram
Chocolate Chips Semi Sweet,5,gram
Chocolate Chips Milk,5.2,gram
Chocolate Chips White,5.4,gram
Bread Crumbs,3.9,gram
Bread Crumbs Plain,3.9,gram
Bread Crumbs Italian,3.8,gram
Panko Bread Crumbs,3.7,gram
Nutritional Yeast,3.3,gram
Nutritional Yeast Flakes,3.3,gram
Protein Powder,3.8,gram
Protein Powder Whey Isolate,3.7,gram
Protein Powder Plant Based,3.9,gram
Gelatin Powder Unflavored,3.4,gram
Yeast,3.1,gram
Yeast Active Dry,3.1,gram
Salt,0,gram
Pepper,2.5,gram
Pepper Black,2.5,gram
Dried Herbs,2.8,gram
Garlic Powder,3.3,gram
Onion Powder,3.4,gram
Paprika,2.8,gram
Chili Powder,2.8,gram
Chili Powder Blend,2.8,gram
Cumin,3.8,gram
Cumin Ground,3.8,gram
Cinnamon,2.5,gram
Cinnamon Ground,2.5,gram
Vinegar,0.2,gram
Vinegar White,0.2,gram
Vinegar Apple Cider,0.2,gram
Vinegar Balsamic,0.9,gram
Vinegar Red Wine,0.2,gram
Lemon Juice,0.3,gram
Lime Juice,0.3,gram
Croutons,4.2,gram
Croutons Garlic Herb,4.2,gram
Bacon Bits,4.8,gram
Bacon Bits Real,5,gram
Bacon Bits Imitation,4.5,gram
Olives,1.8,gram
Olives Green,1.4,gram
Olives Kalamata,2.3,gram
Pickles,0.4,gram
Pickles Dill,0.4,gram
Pickles Sweet Gherkin,1,gram
Relish,1.4,gram
Relish Sweet Pickle,1.4,gram
Pickled Onions,0.5,gram
Pickled Jalapenos,0.3,gram
Capers,0.2,gram
Capers Drained,0.2,gram
Sun Dried Tomatoes,2.6,gram
Sun Dried Tomatoes Oil Packed,2.6,gram
Sun Dried Tomatoes Dry,2.6,gram
Artichoke Hearts,0.8,gram
Artichoke Hearts Canned,0.6,gram
Artichoke Hearts Marinated,1.5,gram
Roasted Red Peppers,0.3,gram
Roasted Red Peppers Jarred,0.3,gram
Coconut Flakes,5.8,gram
Coconut Flakes Unsweetened,6.6,gram
Coconut Flakes Sweetened,4.9,gram
Raisins,3,gram
Craisins,3.1,gram
Craisins Dried Cranberries,3.1,gram
Dried Apricots,2.4,gram
Dates,2.8,gram
Dates Pitted,2.8,gram
Avocado,1.6,gram
Corn,0.9,gram
Corn Kernels,0.9,gram
Beet Salad, 120,serving  
Caesar Salad, 180, 150g serving  
Chocolate Mousse, 270, 100g cup  serving
Churros, 115, 1 piece (30g)  serving
Cupcakes, 195, 1 medium cupcake (50g) serving  
Donuts, 250, 1 medium donut (60g)  serving
Falafel, 165, 3 pieces (50g total)  serving
Grilled Salmon, 280, 140g fillet  serving
French Toast, 290, 2 slices (125g)  serving
Hot Dog, 210, 1 hot dog with bun (75g)  serving
Hummus, 150, 60g (large spoonful)  serving
Ice Cream, 130, 1 scoop (60g)  serving
Nachos, 340, 100g loaded plate  serving
Samosa, 130, 1 medium samosa (45g)  serving
"""

def estimate_portions(label_lower: str, cal_per_gram: float) -> tuple[float, float, float]:
    """Estimates small, medium, large portions in grams based on label."""
    label_lower = label_lower.strip()
    cal_per_gram = cal_per_gram if cal_per_gram > 0 else 0.1 # Avoid zero division

    # Default (fallback values)
    small_g, medium_g, large_g = 50.0, 120.0, 250.0

    # --- Category-Based Adjustments (Prioritized) ---

    # Liquids (Soup, Milk, Juice, Soda, Beer, Wine, Smoothie, Shake, Water, Tea, Coffee)
    if any(kw in label_lower for kw in ['soup', 'milk', 'juice', 'soda', 'ale', 'beer', 'wine', 'smoothie', 'milkshake', 'water', 'coffee', 'tea', 'broth', 'liquid', 'drink', 'beverage']):
        small_g, medium_g, large_g = 100.0, 240.0, 400.0 # ~half cup, cup, large cup/bowl
        if 'shot' in label_lower or 'liquor' in label_lower:
            small_g, medium_g, large_g = 20.0, 45.0, 70.0 # single, double, generous pour
        elif 'espresso' in label_lower:
             small_g, medium_g, large_g = 30.0, 60.0, 90.0

    # Fats & Oils (Oil, Butter, Margarine, Lard, Ghee, Shortening, Mayo, Pesto, Tahini, Nut Butter, Cream Cheese, Sour Cream, Cream, Mascarpone)
    elif any(kw in label_lower for kw in ['oil', 'butter', 'margarine', 'lard', 'ghee', 'shortening', 'mayonnaise', 'mayo', 'aioli', 'pesto', 'tahini', 'nut butter', 'peanut butter', 'almond butter', 'cashew butter', 'sunflower seed butter', 'cream cheese', 'sour cream', 'cream', 'mascarpone', 'nutella']):
        small_g, medium_g, large_g = 7.0, 15.0, 30.0 # ~tsp, tbsp, 2 tbsp
        if 'cooking spray' in label_lower:
             small_g, medium_g, large_g = 1.0, 2.0, 4.0 # very light coating

    # Spices, Seasonings, Tiny Condiments (Salt, Pepper, Herbs, Powders, Vinegar, Hot Sauce, Soy Sauce, Fish Sauce, Worcestershire)
    elif any(kw in label_lower for kw in ['salt', 'pepper', 'powder', 'herb', 'spice', 'cinnamon', 'cumin', 'paprika', 'chili powder', 'yeast', 'baking soda', 'baking powder', 'vinegar', 'hot sauce', 'soy sauce', 'tamari', 'fish sauce', 'worcestershire', 'mustard', 'capers']):
        small_g, medium_g, large_g = 1.0, 5.0, 10.0 # pinch, tsp, ~2tsp
        if 'salt' in label_lower or 'baking soda' in label_lower: # Very small amounts
             small_g, medium_g, large_g = 0.5, 1.0, 2.0
        if 'mustard' in label_lower and 'honey' not in label_lower : # Regular mustard is less dense/caloric than honey mustard
             small_g, medium_g, large_g = 5.0, 10.0, 20.0

    # Sweeteners & Syrups (Sugar, Honey, Syrup, Jam, Jelly, Molasses, Nectar)
    elif any(kw in label_lower for kw in ['sugar', 'honey', 'syrup', 'jam', 'jelly', 'marmalade', 'molasses', 'nectar', 'sweetened', 'confectioners']):
        small_g, medium_g, large_g = 5.0, 15.0, 30.0 # ~tsp, tbsp, 2 tbsp

    # Nuts & Seeds
    elif any(kw in label_lower for kw in ['nuts', 'almond', 'walnut', 'peanut', 'cashew', 'pecan', 'pistachio', 'macadamia', 'brazil', 'hazelnut', 'seed', 'chia', 'flax', 'pumpkin', 'sunflower', 'sesame', 'hemp']):
        small_g, medium_g, large_g = 10.0, 28.0, 45.0 # small handful, ~1oz, large handful

    # Flours & Starches
    elif any(kw in label_lower for kw in ['samosa','flour', 'starch', 'cornstarch']):
        small_g, medium_g, large_g = 15.0, 40.0, 120.0 # ~tbsp, 1/4 cup, cup

    # Cheese (General/Block/Shredded - Excludes Cream Cheese/Ricotta covered above)
    elif 'cheese' in label_lower and not any(kw in label_lower for kw in ['churros','cream cheese', 'cottage', 'ricotta', 'sauce', 'dressing', 'cake', 'burger', 'sandwich', 'quesadilla', 'pizza']):
        small_g, medium_g, large_g = 15.0, 30.0, 60.0 # sprinkle, ~1oz, generous portion
        if 'feta' in label_lower or 'goat' in label_lower or 'blue' in label_lower: # Often used more sparingly
             small_g, medium_g, large_g = 15.0, 25.0, 40.0
        if 'parmesan' in label_lower: # Usually grated
             small_g, medium_g, large_g = 5.0, 10.0, 20.0

    # Condiments (Ketchup, BBQ, Salsa, Gravy, Dressing, Hummus, Guac, Relish, Pickles etc.)
    elif any(kw in label_lower for kw in ['falafel','ketchup', 'bbq sauce', 'salsa', 'gravy', 'dressing', 'vinaigrette', 'hummus', 'guacamole', 'relish', 'pickles', 'olives', 'tapenade', 'chutney', 'sauce', 'dip', 'spread']) and not any(kw in label_lower for kw in ['oil', 'butter', 'mayo', 'pesto', 'tahini', 'nut butter', 'cream cheese', 'sour cream', 'cheese', 'apple butter', 'jam', 'jelly', 'syrup', 'honey', 'nutella', 'pasta', 'stir-fry', 'curry']): # Avoid re-categorizing things covered above or main dishes
        small_g, medium_g, large_g = 15.0, 30.0, 60.0 # dollop, standard side, large side/dip
        if 'pico de gallo' in label_lower or 'salsa verde' in label_lower or 'pickles' in label_lower: # Lighter
             small_g, medium_g, large_g = 20.0, 50.0, 80.0
        if 'dressing' in label_lower or 'vinaigrette' in label_lower: # Often high cal/g
             small_g, medium_g, large_g = 15.0, 30.0, 45.0

    # Grains & Starches (Cooked Rice, Pasta, Quinoa, Couscous, Oatmeal, Cereal, Potatoes)
    elif any(kw in label_lower for kw in ['rice', 'pasta', 'noodle', 'quinoa', 'couscous', 'oatmeal', 'cereal', 'potato', 'polenta', 'risotto', 'pilaf', 'grits', 'bulgur']):
        small_g, medium_g, large_g = 100.0, 180.0, 300.0 # side, standard main, large main
        if 'cereal' in label_lower: # Dry weight equivalent is much lighter
             small_g, medium_g, large_g = 20.0, 40.0, 60.0 # Dry approx weights
        if 'potato' in label_lower and 'salad' not in label_lower: # Baked/Mashed/Roasted
             small_g, medium_g, large_g = 100.0, 170.0, 250.0 # Small potato, medium, large

    # Legumes (Beans, Lentils, Peas, Chickpeas)
    elif any(kw in label_lower for kw in ['bean', 'lentil', 'pea', 'chickpea', 'edamame']):
        small_g, medium_g, large_g = 70.0, 130.0, 200.0 # side, standard serving, large serving

    # Fruits (Whole/Chunks - Apple, Banana, Orange, Berries etc.)
    elif any(kw in label_lower for kw in ['apple', 'banana', 'orange', 'pear', 'peach', 'plum', 'mango', 'grapes', 'berries', 'strawberry', 'blueberry', 'raspberry', 'melon', 'watermelon', 'cantaloupe', 'pineapple', 'kiwi', 'fruit']):
        small_g, medium_g, large_g = 80.0, 150.0, 220.0 # Small fruit/half cup, Med fruit/cup, Lrg fruit/generous cup
        if 'avocado' in label_lower: # Higher density/calories
             small_g, medium_g, large_g = 50.0, 100.0, 150.0 # Quarter, half, large half/whole small
        if 'dried' in label_lower or 'raisins' in label_lower or 'craisins' in label_lower or 'dates' in label_lower or 'apricots' in label_lower: # Dried fruit is dense
             small_g, medium_g, large_g = 20.0, 40.0, 60.0

    # Vegetables (Cooked/Raw Chunks - Broccoli, Carrots, Peppers, etc.)
    elif any(kw in label_lower for kw in ['grilled salmon','vegetable', 'broccoli', 'carrot', 'celery', 'cucumber', 'tomato', 'pepper', 'spinach', 'lettuce', 'kale', 'bean', 'pea', 'corn', 'onion', 'mushroom', 'zucchini', 'asparagus', 'eggplant', 'artichoke']):
        small_g, medium_g, large_g = 75.0, 150.0, 250.0 # Small side, standard side/cup, large serving
        if any(kw in label_lower for kw in ['spinach', 'lettuce', 'kale', 'greens']): # Leafy greens are light
             small_g, medium_g, large_g = 30.0, 70.0, 120.0 # By volume these look large but weigh less

    # Meats & Poultry (Cooked - Chicken, Beef, Pork, Lamb, Turkey)
    elif any(kw in label_lower for kw in ['chicken', 'beef', 'pork', 'lamb', 'turkey', 'steak', 'roast', 'chop', 'loin', 'patty', 'meatloaf', 'kebab', 'shawarma', 'gyro', 'sausage', 'bratwurst', 'ham', 'bacon', 'meat']) and not any(kw in label_lower for kw in ['sandwich', 'burger', 'wrap', 'taco', 'burrito', 'quesadilla', 'pizza', 'soup', 'stew', 'curry', 'salad', 'broth']): # Avoid combo dishes
        small_g, medium_g, large_g = 85.0, 140.0, 220.0 # ~3oz, ~5oz, ~8oz
        if 'bacon' in label_lower: # Strips are light
             small_g, medium_g, large_g = 10.0, 20.0, 35.0 # ~1-2 strips, 3-4, 5-6
        if 'sausage' in label_lower or 'bratwurst' in label_lower or 'link' in label_lower:
             small_g, medium_g, large_g = 50.0, 80.0, 120.0 # 1 link, 1 large/2 small, 2 large
        if 'ground' in label_lower or 'pulled' in label_lower or ' french toast' in label_lower: # Ground/shredded
             small_g, medium_g, large_g = 80.0, 120.0, 180.0
        if 'wing' in label_lower: # Chicken Wings
            small_g, medium_g, large_g = 60.0, 120.0, 200.0 # 2-3 wings, 5-6, 8-10 (adjusting for bone weight implicitly)


    # Fish & Seafood (Cooked - Salmon, Tuna, Cod, Shrimp, etc.)
    elif any(kw in label_lower for kw in ['fish', 'salmon', 'tuna', 'cod', 'tilapia', 'halibut', 'trout', 'shrimp', 'scallop', 'lobster', 'crab', 'seafood']):
        small_g, medium_g, large_g = 85.0, 140.0, 200.0 # ~3oz, ~5oz, ~7oz fillet/serving
        if 'shrimp' in label_lower or 'scallop' in label_lower: # Smaller pieces
             small_g, medium_g, large_g = 60.0, 100.0, 150.0
        if 'crab cake' in label_lower:
            small_g, medium_g, large_g = 70.0, 100.0, 150.0 # 1 small, 1 large, 2 small

    # Eggs
    elif 'egg' in label_lower and not any(kw in label_lower for kw in ['sandwich', 'salad', 'benedict', 'roll', 'noodle']):
        small_g, medium_g, large_g = 40.0, 55.0, 100.0 # ~Small/Med Egg, Large Egg, ~2 Eggs

    # Tofu & Tempeh
    elif any(kw in label_lower for kw in ['tofu', 'tempeh']):
        small_g, medium_g, large_g = 85.0, 140.0, 200.0 # Similar portioning to meat

    # Breads (Slice, Roll, Bagel, Muffin, Croissant, Pita, Naan)
    elif any(kw in label_lower for kw in ['hot dog','hummus','bread', 'toast', 'roll', 'bagel', 'muffin', 'croissant', 'pita', 'naan', 'cornbread', 'scone']):
        small_g, medium_g, large_g = 30.0, 60.0, 100.0 # 1 slice/small roll, bagel/large roll/muffin, large bagel/2 muffins
        if 'slice' in label_lower:
             small_g, medium_g, large_g = 25.0, 35.0, 50.0
        if 'bagel' in label_lower or 'croissant' in label_lower or 'muffin' in label_lower or 'naan' in label_lower or 'cornbread' in label_lower:
             small_g, medium_g, large_g = 50.0, 80.0, 120.0

    # Baked Goods & Desserts (Cake, Pie, Cookie, Brownie, Donut, Ice Cream, Yogurt)
    elif any(kw in label_lower for kw in ['nachos','cake', 'pie', 'cookie','Chocolate Mousse', 'brownie', 'blondie', 'macaron', 'donut', 'cupcake', 'tiramisu', 'creme brulee', 'pudding', 'jello', 'Ice Cream', 'sorbet', 'yogurt', 'dessert', 'pastry']):
        small_g, medium_g, large_g = 40.0, 80.0, 150.0 # Small portion/cookie, standard slice/scoop, large slice/2 scoops
        if 'cookie' in label_lower or 'macaron' in label_lower:
             small_g, medium_g, large_g = 20.0, 40.0, 70.0
        
        if 'cake' in label_lower or 'pie' in label_lower or 'cheesecake' in label_lower:
            small_g, medium_g, large_g = 70.0, 120.0, 180.0 # Thin slice, standard, generous
        if 'Donut' in label_lower or 'cupcakes' in label_lower:
            small_g, medium_g, large_g = 50.0, 75.0, 110.0 # Mini, Standard, Large/Filled

    # Combined Dishes (Estimate based on typical total weight)
    elif any(kw in label_lower for kw in ['pizza', 'burger', 'sandwich', 'wrap', 'burrito', 'taco', 'quesadilla', 'stir-fry', 'curry', 'stew', 'casserole', 'lasagna', 'paella', 'biryani', 'risotto', 'pad thai', 'ramen', 'pho', 'salad', 'benedict', 'omelette', 'frittata']):
        small_g, medium_g, large_g = 150.0, 280.0, 450.0 # General estimate for a mixed dish
        if 'pizza' in label_lower:
             if 'slice' in label_lower: small_g, medium_g, large_g = 100.0, 130.0, 180.0
             else: small_g, medium_g, large_g = 200.0, 300.0, 450.0 # Personal size range
        if 'burger' in label_lower or 'sandwich' in label_lower:
             small_g, medium_g, large_g = 180.0, 280.0, 400.0
        if 'wrap' in label_lower or 'burrito' in label_lower:
             small_g, medium_g, large_g = 200.0, 320.0, 500.0
        if 'taco' in label_lower:
             small_g, medium_g, large_g = 80.0, 120.0, 180.0 # Per taco estimate
        if 'quesadilla' in label_lower:
             small_g, medium_g, large_g = 120.0, 200.0, 300.0 # Half, whole small, whole large
        if 'salad' in label_lower and not any(kw in label_lower for kw in ['Beet Salad','fruit', 'potato', 'macaroni', 'tuna', 'chicken', 'egg']): # Leafy base salads
             small_g, medium_g, large_g = 150.0, 250.0, 400.0 # Including toppings tends to increase weight significantly
        if 'stir-fry' in label_lower or 'pad thai' in label_lower or 'noodles' in label_lower or 'pho' in label_lower or 'ramen' in label_lower:
             small_g, medium_g, large_g = 250.0, 400.0, 600.0 # Often larger portions
        if 'curry' in label_lower or 'stew' in label_lower:
             small_g, medium_g, large_g = 200.0, 350.0, 500.0
        if 'omelette' in label_lower:
             small_g, medium_g, large_g = 100.0, 150.0, 220.0 # 2-egg, 3-egg, large/loaded

    # --- Specific Item Overrides (Can fine-tune here) ---
    if 'french fries' in label_lower:
        small_g, medium_g, large_g = 70.0, 115.0, 160.0
    elif 'onion rings' in label_lower:
        small_g, medium_g, large_g = 60.0, 100.0, 150.0
    elif 'chips' in label_lower and 'fish' not in label_lower: # Potato chips, tortilla chips etc.
        small_g, medium_g, large_g = 15.0, 28.0, 50.0 # Snack bag sizes ~0.5oz, 1oz, 1.75oz
    elif 'popcorn' in label_lower:
        small_g, medium_g, large_g = 10.0, 25.0, 40.0 # Very light per volume (cups)
    elif 'pretzel' in label_lower:
        small_g, medium_g, large_g = 20.0, 40.0, 80.0
    elif 'chocolate bar' in label_lower:
        small_g, medium_g, large_g = 20.0, 45.0, 70.0 # Fun size, standard, king size
    elif 'chocolate chips' in label_lower:
         small_g, medium_g, large_g = 8.0, 15.0, 30.0 # ~Tbsp, 2 Tbsp, 1/4 cup
    # Round to nearest gram for cleanliness
    return round(small_g), round(medium_g), round(large_g)


# --- Processing Logic ---
food_data = {}
# Use StringIO to treat the string data as a file
csvfile = StringIO(csv_data)
reader = csv.DictReader(csvfile)

# Extract unique labels and their calories per gram
for row in reader:
    label_original = row.get('Label', '').strip()
    label_lower = label_original.lower()
    unit = row.get('Unit', '').strip().lower()
    calories_str = row.get('Calories', '').strip()

    if not label_original or not unit or not calories_str:
        continue # Skip incomplete rows

    # Only process 'gram' entries to get the base calorie density
    if unit == 'gram':
        try:
            calories_per_gram = float(calories_str)
            # Only add if not already present (first entry wins) or if calorie value is valid
            # And avoid overwriting if already processed (though duplicates shouldn't exist now)
            if label_lower not in food_data and calories_per_gram >= 0:
                 food_data[label_lower] = {
                     'original_label': label_original,
                     'calories_per_gram': calories_per_gram
                 }
            elif label_lower in food_data:
                # Optional: Could add logic here to compare/update if needed, but keeping first is simpler
                pass
        except ValueError:
            # Silently skip rows with invalid calorie numbers for gram entries
            # print(f"Skipping row due to invalid calorie value for 'gram' unit: {row}")
            continue

# --- Generate Output Data in the New Format ---
output_rows = []
# Define the new header
output_rows.append(['Label', 'Calories_per_Gram', 'Small_g', 'Medium_g', 'Large_g'])

# Sort by original label for consistent output order
# Use .get('original_label', '') as a fallback for sorting robustness
sorted_labels = sorted(food_data.keys(), key=lambda k: food_data.get(k, {}).get('original_label', k))

for label_lower in sorted_labels:
    data = food_data[label_lower]
    original_label = data['original_label']
    calories_per_gram = data['calories_per_gram']

    # Estimate the S/M/L portion sizes for this item
    small_g, medium_g, large_g = estimate_portions(label_lower, calories_per_gram)

    # Append the row in the new format
    output_rows.append([
        original_label,
        f"{calories_per_gram:.2f}", # Format calories to 2 decimal places
        small_g,
        medium_g,
        large_g
    ])

# --- Create the output CSV string (for printing) ---
output_csv_buffer = StringIO()
writer = csv.writer(output_csv_buffer)
writer.writerows(output_rows)

# --- Print the result ---
print("--- START OF PROCESSED CSV DATA ---")
print(output_csv_buffer.getvalue())
print("--- END OF PROCESSED CSV DATA ---")

# --- Save to the final file ('calorie_table_processed.csv') ---
# Using the corrected path logic
script_dir = os.path.dirname(__file__) # Gets the directory where this script is saved
# Use 'calorie_table_processed.csv' as the target filename for utils.py
output_filename = os.path.join(script_dir, "calorie_table_processed.csv")

print(f"\nAttempting to save processed CSV to: {output_filename}")

try:
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        # Reuse the writer with the actual file
        file_writer = csv.writer(f)
        file_writer.writerows(output_rows) # Write the data
    print(f"✅ Successfully saved processed data to {output_filename}")
except IOError as e:
    print(f"❌ Error saving file {output_filename}: {e}")
    print("   Please check write permissions for the script's directory.")
except Exception as e_gen: # Catch other potential errors during saving
     print(f"❌ An unexpected error occurred trying to save the file: {e_gen}")