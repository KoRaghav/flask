import textrazor
textrazor.api_key = "a6fd329c7a2bbb934ac7bbe316c99c4b550ecfd7bc5f1a32385cf850"

client = textrazor.TextRazor()
client.set_classifiers(["tags"])

def api(question):
	response = client.analyze(question)

	return [(x.label,x.score) for x in response.categories()]

