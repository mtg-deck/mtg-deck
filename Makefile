all: node_modules
	npm run build --prefix editor/frontend

node_modules: editor/frontend/package.json
	npm install -C editor/frontend/

editor/frontend/package.json: editor/frontend/
	git submodule update --remote

editor/frontend/: 
	mkdir -p editor/frontend
