from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int


# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook = []

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	 # Replace all hyphens and underscores with a whitespace
	recipeName = re.sub(r'[-_]', ' ', recipeName)

	# Remove any character that are not letters or whitespaces
	recipeName = re.sub(r'[^a-zA-Z ]', '', recipeName)

	# Remove multiple whitespaces between words and also remove leading and
	# trailing whitespaces
	recipeName = re.sub(r'\s+', ' ', recipeName).strip()

	# If the string does not have a length of > 0 characters, then return
	# none
	if not recipeName:
		return None
    
	# Capitalise the first letter of each word
	recipeName = recipeName.title()

	# If recipeName length in greather than 0 then return receipeName
	# otherwise return None
	return recipeName if len(recipeName) > 0 else None


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	
	# Extract the JSON body that is sent over HTTP
	data = request.get_json()
	
	# If the type of data recieved is ingredient or recipe then perform
	# relevant checks, otherwise return an error
	if data.get('type') == 'recipe':
		
		# Extract the requiredItems from the data and if it is not a list or
		# does not exist then return an error
		requiredItems = data.get('requiredItems')
		if requiredItems is None:
			return jsonify({"Error": "The requiredItems list is missing. Please fix this and try again."}), 400
		if not isinstance(requiredItems, list):
			return jsonify({"Error": "The requiredItems is not a list. Please fix this and try again."}), 400
		
		# Check to ensure that recipe requiredItems only has one element per
		# name. If this is not the case then return an error. Also check that
		# the names of all requiredItems are strings and their quantity is an
		# int. If this is not the case then also return an error
		alreadyExists = set()
		for item in requiredItems:
			name = item.get('name')
			quantity = item.get('quantity')
			if not isinstance(name, str):
				return jsonify({"Error": "The requiredItems list contains an invalid name which is not a string. Please fix this and try again."}), 400
			if not isinstance(quantity, int):
				return jsonify({"Error": "The requiredItems list contains an invalid quantity which is not a integer. Please fix this and try again."}), 400
			if name in alreadyExists:
				return jsonify({"Error": "The requiredItems list contains duplicate entries. Please fix this and try again."}), 400
			alreadyExists.add(name)
	elif data.get('type') == 'ingredient':
		
		# Check that the cookTime is an integer and is greater than or equal to
		# 0. If this is not the case return an error
		cookTime = data.get('cookTime')
		if not isinstance(cookTime, int):
			return jsonify({"Error": "The cookTime is not an integer. Please fix this and try again."}), 400
		if cookTime < 0:
			return jsonify({"Error": "The cookTime must be greater than or equal to 0. Please fix this and try again."}), 400		
	elif data.get('type') not in ["recipe", "ingredient"]:
		return jsonify({"Error": "The type is invalid. Please ensure that type is either 'recipe' or 'ingredient' and try again."}), 400
	
	# Check that the entry name is unique. If it is not then return an error
	for alreadyExistingEntry in cookbook:
		if alreadyExistingEntry["name"] == data["name"]:
			return jsonify({"Error": "An entry with this name already exists in the cookbook. Please fix this and try again."}), 400
	
	# All error cases have been tested. Add the new entry to the cookbook
	cookbook.append(data)

	# return a HTTP 200 status code and an empty response body
	return {}, 200



# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():

	# Extract the recipe name from the URL
	recipeName = request.args.get('name')

	# Check if a recipe with the corresponding name exists in the cookbook.
	# If it does not return an error
	recipeToSummarise = None

	for index in cookbook:
		if index['name'] == recipeName and index['type'] == 'recipe':
			recipeToSummarise = index
			break
	
	if recipeToSummarise is None:
		return jsonify({"Error": "A recipe with the corresponding name cannot be found."}), 400
	
	# Try a helper function which return a List of the base ingredients
	# and their quantity. It will raise an exception if the recipe contains
	# recipes or ingredients that aren't in the cookbook
	try:
		baseIngredientsList = baseIngredientsHelper(recipeToSummarise)
	except Exception as e:
		return jsonify({"Error": str(e)}), 400
	
	# Call a helper function with the baseIngredients to get the total
	# cooking time
	cookTime = cookTimeHelper(baseIngredientsList)

	# Create the summary object
	recipeSummary = {
		"name": recipeName, 
		"cookTime": cookTime,
		"ingredients": baseIngredientsList
	}


	return recipeSummary, 200

# This function takes in a recipe and returns a list containing the base
# ingredients and their quantity
def baseIngredientsHelper(recipe, factor=1):
	
	# The dictionary of base ingredients and their quantities to return
	baseIngredientsReturnDict = {}

	# For each required ingredient or recipe check that it is in the cookbook.
	# If it is the cookbook save it as we will need to explore it to determine
	# if it is a base ingredient or not and recurive in the latter case.
	# If the reqiured ingredient does not exist in the cookbook then
	# raise an exception
	for requiredItem in recipe["requiredItems"]:
		itemToExplore = None
		for existentItem in cookbook:
			if requiredItem["name"] == existentItem["name"]:
				itemToExplore = existentItem
				break
	
	if itemToExplore is None:
		raise Exception("The recipe contains recipes or ingredients that aren't in the cookbook. Please fix this and try again.")
	
	# Since the item does exist in the cookbook multiply the factor to account
	# for nested recipes
	quantity = requiredItem["quantity"] * factor

	# If the itemToExplore is a recipe then recurse to get the base ingredients
	# and also set the factor to the current quantity (to account for the
	# nesting of recipes). Then add those base ingredients to the 
	# baseIngredientsReturnDict.
	# If the itemToExplore is an ingredient and it exists in the 
	# baseIngredientsReturnDict then add the quantity to the
	# existing quantity otherwise add a new key value pair for the 
	# itemToExplore and its quantity.
	if itemToExplore["type"] == "recipe":
		baseIngredients = baseIngredientsHelper(itemToExplore, factor=quantity)
		for baseIngredientName, baseIngredientQuantity in baseIngredients.items():
			baseIngredientsReturnDict[baseIngredientName] = baseIngredientsReturnDict.get(baseIngredientName, 0) + baseIngredientQuantity
	elif itemToExplore["type"] == "ingredient":
		baseIngredientsReturnDict[itemToExplore["name"]] = baseIngredientsReturnDict.get(itemToExplore["name"], 0) + quantity
	
	return baseIngredientsReturnDict

# This function takes in a list of base ingredients 
# (their names and quantity) and returns the total cooking time
def cookTimeHelper(baseIngredientsList):
	
	# Create a dict of the ingredients and their cooking time for quick lookup
	cookTimeDict = {ingredient.name: ingredient.cookTime for ingredient in cookbook if hasattr(ingredient, 'cookTime')}

	# Return the sum of all the cooking times in the baseIngredientsDict
	return sum(cookTimeDict.get(ingredient) * quantity for ingredient, quantity in baseIngredientsList.items() if cookTimeDict.get(ingredient) is not None)


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
