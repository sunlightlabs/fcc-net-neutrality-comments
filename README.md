fcc-net-neutrality-comments
===========================

scraping, parsing and making sense of the flood of comments submitted to the FCC on net neutrality

FAQ (Read First!)
-----------------

**Will the code in this repo "just work"?**
No. It wasn't really written with any intent other than the short-term goals of a one-off project.

**Is the code in this repo useful?**
Qualified yes. There's solid, re-useable components here. However, it's very tightly fit to the circumstance we were in at the time. Some of the code here took us down blind alleys and probably shouldn't be used at all.

Depending on your timeline, you might be able to make use of this stuff, but see the sections below, which will show you around a bit.


Introduction & Background
-------------------------

Before you dive in, it's going to be realllly useful to check out the tutorial at gensim: https://radimrehurek.com/gensim/tutorial.html

Then, go to a few notebooks:

[how-to](https://github.com/sunlightlabs/fcc-net-neutrality-comments/blob/master/notebooks/howto.ipynb): an instructional notebook that @boblannon started but is woefully incomplete
[serializing-corpus](./notebooks/serializing_corpus.ipynb): the basic task of creating a dictionary, lazily reading a bunch of files and serializing everything important to disk. This is basically a record of me iterating on

A large part of the work, for us, was munging the (absolutely dreadful) data that we got from FCC.  Most of that work is in [fcc-split](https://github.com/boblannon/fcc-net-neutrality-comments/tree/master/fcc_split).  There's apparently now an API, which wasn't available back then, so maybe you can just ignore all of that. You can get a sense of the shape of the fcc-split's output [here](https://github.com/boblannon/fcc-net-neutrality-comments/blob/master/fcc_split/fcc_split.py#L166-L190).  Those are the source documents that all of the processing/corpus-building/modeling code is written for.


Here's a high-level tour:

Preprocessing
-------------

[process_all_json.sh](./scripts/process_all_json.sh): read the source files (the outputs of fcc-split), each of which is a single JSON object. for each file, it adds a "tagged" property, which is a  cleaned, normalized, and part-of-speech tagged version of the original document. it's calling [pos-tagger.py](./models/pos_tagger.py), so you can look there to get a sense of what exactly is being done.


Corpus-Building
---------------

[build_corpus_and_dictionary.py](./scripts/build_corpus_and_dictionary.py) lazily reads through the processed JSON files and creates two things: a gensim.Dictionary that will be used for mapping tokens to identifiers and a plaintext file that lists all of the document ids.

[serializing_corpus.py](./scripts/serializing_corpus.py) uses the dictionary to create a MatrixMarket serialization of the corpus (see [gensim "corpus formats" doc](https://radimrehurek.com/gensim/tut1.html#corpus-formats) for more on this)


Corpus Transformation
---------------------

[transform_corpus.py](./scripts/transform_corpus.py) opens the serialized corpus and transforms it to a tf-idf weighted corpus (see [gensim "tranformations" doc](https://radimrehurek.com/gensim/tut2.html) for more on this)


LSI Modeling
------------

[model-distributed.sh](./scripts/model_distributed.sh): this is where the LSI model is built. I was following the instructions on the [gensim page](https://radimrehurek.com/gensim/dist_lsi.html), with one giant deviation: i did everything on one box, because i didn't have time to learn how to spin up and manage a cluster of ec2's.  so what's happening is that we spun up a box with an insane amount of cores.  this script  pins a bunch of workers to the different cores, and then pins the dispatcher to the first core. Then it runs [build_distributed_model.py](./scripts/build_distributed_model.py), which opens up the dictionary and tfidf corpus, and builds the model in a distributed way.


Hierarchical Clustering
-----------------------

[hybrid_clustering.py](./scripts/hybrid_clustering.py): this script takes the LSI model and creates a MatrixSimilarity  model, which is basically an index that will allow you to return the most similar document in the corpus to some query. It takes advantage of the matrix representation, though, so that it can ask, for any arbitrary group of documents, how great is their variance (in the space created by the LSI model)? It uses that variance metric to do hierarchical clustering using a home-brewed algorithm that i lovingly refer to as Shitty ANOVA (tm).

[kanopy_cluster_tree.py](./scripts/kanopy_cluster_tree.py): this takes the cluster information produced in the last step and builds the data structure that we used in the final visualization. It builds a JSON representation of the tree that can be used by the visualization code (which is a modified version of the [d3js circle-packing example](https://bl.ocks.org/mbostock/4063530)). It also collects the list of documents that belong to each cluster and tries to identify five key words that describe the cluster


Visualization
-------------

The code for the [main visualization](http://openinternet-pt2.widgets.sunlightfoundation.com.s3.amazonaws.com/index.html#) itself is in the [cluster_viz directory](https://github.com/sunlightlabs/fcc-net-neutrality-comments/tree/master/cluster_viz).

The [pro/anti visualization](https://s3.amazonaws.com/openinternet.widgets.sunlightfoundation.com/index.html?t=form) involved an intermediate step where we reviewed the clusters and identified their sources. That was the manual coding step that I referred to before. That's why there's a script for downloading a csv from gdocs in the cluster_viz folder.
