import sqlite3
from .query_language import process_query
import json
from flask import Flask, request, render_template, abort

app = Flask(__name__)
def get_connection() -> sqlite3.Connection:
	conn = sqlite3.connect("file:linguistics.db?mode=ro", uri=True)
	conn.row_factory = sqlite3.Row
	return conn

@app.context_processor
def logo():
	return dict(logo='/lɪŋˈɡwɪs.tɪks.diː.biː/')

@app.route('/')
def index():
	return render_template('site.html')

@app.route('/search')
def search():
	query = request.args.get('query')
	if not query:
		abort(400)
	
	sql, parameters = process_query(query)
	with get_connection() as conn:
		results = [{**row, 'syllables': json.loads(row['syllables'])} for row in conn.execute(sql, parameters).fetchall()][:100]

	return render_template('site.html', results=results, query=query)
