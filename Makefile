version = 0.71

translate:
	python main.py --translation

rmduplicates:
	python main.py --rmduplicates

dot:
	python main.py --graph

graph: dot
	cd output/graph && time dot -Tsvg -o main.svg -v main.dot
# 	cd output && dot -Tpng -o main.png -v main.dot
# 	cd output && dot -Tsvg -o main.svg -v main.dot

pack:
	./pack.sh "translate.$(version).7z"
