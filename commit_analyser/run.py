import os
from index import Index
from spacy_index import SpacyIndex

if __name__ == '__main__':
    # projects = next(os.walk('/Users/kapilan/githome/for_analysis/later'))[1]
    # project_paths = ["/Users/kapilan/githome/for_analysis/later/" + stub for stub in projects]
    # for project in project_paths:

    index = Index("//Users/kapilan/githome/for_analysis/now/crdt-canvas/")
