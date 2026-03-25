
translate:
	python main.py --translation

dot:
	python main.py --graph

graph: dot
	cd output/graph && time dot -Tsvg -o main.svg -v main.dot
# 	cd output && dot -Tpng -o main.png -v main.dot
# 	cd output && dot -Tsvg -o main.svg -v main.dot
