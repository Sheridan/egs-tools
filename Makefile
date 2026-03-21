
translate:
	python main.py --translation

graph:
	python main.py --graph
# 	cd output && neato -Tsvg -o output.svg -v main.dot
# 	cd output && dot -Tsvg -o output.svg -v main.dot
# 	cd output && fdp -Tsvg -o output.svg -v main.dot
	cd output && circo -Tsvg -o output.svg -v main.dot
