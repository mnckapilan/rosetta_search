from pydriller import RepositoryMining
from time import time  # To time our operations

url = input("Enter the GitHub URL Here: ")
stub = url.rsplit('/', 1)[-1]

t = time()
filename = stub + "_commits"
text_file = open(filename, "w")

for commit in RepositoryMining(url).traverse_commits():
    text_file.write(commit.msg + " \n")

text_file.close()
print('Time taken: {} mins'.format(round((time() - t) / 60, 2)))



