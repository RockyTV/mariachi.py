import telepot

def requirements():
	"""Build the requirements list for this project"""
	requirements = []

	with open('requirements.txt') as list:
		for install in list:
			requirements.append(install.strip())

	return requirements