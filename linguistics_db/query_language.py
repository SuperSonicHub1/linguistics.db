from textx import metamodel_from_str, get_children_of_type

with open("search_engine.tx") as f:
	grammar = f.read()

metamodel = metamodel_from_str(grammar)

query_template = """SELECT *, length(spelling) AS spelling_length, length(pronunciation) as pronunciation_length, json_array_length(syllables) as syllables_length
FROM words
{where_clause}
{order_clause};"""

def name(o: object) -> str:
	return o.__class__.__name__

def brace_to_inequality_sign(brace: str) -> str:
	if brace == '[': return ">="
	elif brace == '(': return ">"
	elif brace == ']': return "<="
	elif brace == ')': return "<"
	else:
		raise ValueError(f'Unexpected brace for Interval: {brace}')

def process_query(query: str) -> tuple[str, list]:
	model = metamodel.model_from_str(query)
	arguments = []
	where_clause_parts = []
	order_clause_parts = []
	for part in model.parts:
		part_name = name(part)
		if part_name == "LikeFixture":
			where_clause_parts.append(f"{part.column} LIKE ?")
			arguments.append(f"%{part.value}%")
		elif part_name == "ContainsFixture":
			where_clause_parts.append(f"EXISTS (SELECT 1 from json_each({part.column}) WHERE value = ?")
			arguments.append(part.value)
		elif part_name == "StartsWithFixture":
			column = part.column
			if column == "syllables":
				where_clause_parts.append(f"{column} -> '$.[0]' = ?")
				arguments.append(f"{part.value}")
			else:
				where_clause_parts.append(f"{part.column} LIKE ?")
				arguments.append(f"{part.value}%")
		elif part_name == "EndsWithFixture":
			column = part.column
			if column == "syllables":
				where_clause_parts.append(f"{column} -> '$.[#-1]' = ?")
				arguments.append(f"{part.value}")
			else:
				where_clause_parts.append(f"{part.column} LIKE ?")
				arguments.append(f"%{part.value}")
		elif part_name == "LengthFixture":
			value = part.value
			if isinstance(value, int):
				where_clause_parts.append(f"{part.column}_length = ?")
				arguments.append(value)
			elif name(value) == 'Interval':
				where_clause_parts.append(f"{part.column}_length {brace_to_inequality_sign(value.left_brace)} ?")
				arguments.append(value.left_value)
				where_clause_parts.append(f"{part.column}_length {brace_to_inequality_sign(value.right_brace)} ?")
				arguments.append(value.right_value)
			else:
				raise ValueError(f'Unknown argument to LengthFixture: {part.value}')
		elif part_name == "OrderFixture":
			order_clause_parts.append(f'{part.column}_{part.value} {part.direction}')
	where_clause = f"WHERE {' AND '.join(where_clause_parts)}" if len(where_clause_parts) else ""
	order_clause = f"ORDER BY {', '.join(order_clause_parts)}" if len(order_clause_parts) else ""
	return query_template.format(where_clause=where_clause, order_clause=order_clause), arguments

if __name__ == "__main__":
	print(*process_query('syllables:length:2 spelling:length:[4, 6] order:desc:pronunciation:length'))
