import sqlite3
from .query_language import process_query
from pprint import pprint
import json

with sqlite3.connect("file:linguistics.db?mode=ro", uri=True) as conn:
	conn.row_factory = sqlite3.Row

	while True:
		try:
			query = input("> ")
			sql, parameters = process_query(query)
			print(sql)
			print(parameters)
			results = [dict(row) for row in conn.execute(sql, parameters).fetchall()]
			pprint(results[:5])
			# with open('query_results.json', 'w', encoding='utf-8') as f:
			# 	json.dump(results, f, ensure_ascii=False)
		except KeyboardInterrupt as e:
			exit()
		except:
			print(e)
			pass
