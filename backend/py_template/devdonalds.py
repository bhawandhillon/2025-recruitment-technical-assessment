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
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
