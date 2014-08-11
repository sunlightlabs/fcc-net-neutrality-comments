# IPython log file
import sys
import logging
from gensim import models, corpora

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    filename='log/build_distributed_model.log', filemode='a',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def do_lsi(num_topics):
    logger.info('reading source corpus and id2word')
    tfidf_corpus = corpora.MmCorpus('persistence/tfidf_corpus.mm')
    my_dict = corpora.Dictionary.load('persistence/my_dict')

    logger.info('building LSI model')
    lsi_model = models.LsiModel(tfidf_corpus, id2word=my_dict,
                                num_topics=num_topics, distributed=True)

    persist_model = 'persistence/lsi_model-%d' % num_topics
    logger.info('persisting model in '+persist_model)
    lsi_model.save(persist_model)

    logger.info('transforming tfidf corpus')
    tfidf_corpus_lsi = lsi_model[tfidf_corpus]

    persist_corpus = 'persistence/tfidf_corpus_lsi-%d' % num_topics
    logger.info('persisting transformed corpus in '+persist_corpus)
    corpora.MmCorpus.serialize(persist_corpus, tfidf_corpus_lsi)
    logger.info('finished LSI')


def do_lda(num_topics):
    logger.info('reading source corpus and id2word')
    corpus = corpora.MmCorpus('persistence/test_corpus.mm')
    my_dict = corpora.Dictionary.load('persistence/my_dict')

    logger.info('building LDA model')
    lda_model = models.LdaModel(corpus, id2word=my_dict,
                                num_topics=num_topics, distributed=True)

    persist_model = 'persistence/lda_model-%d' % num_topics
    logger.info('persisting model in '+persist_model)
    lda_model.save(persist_model)

    logger.info('transforming corpus')
    corpus_lda = lda_model[corpus]

    persist_corpus = 'persistence/corpus_lda-%d' % num_topics
    logger.info('persisting transformed corpus in '+persist_corpus)
    corpora.MmCorpus.serialize(persist_corpus, corpus_lda)
    logger.info('finished LDA')


if __name__ == "__main__":
    modeltype = sys.argv[1].lower()
    num_topics = int(sys.argv[2])
    if modeltype == 'lda':
        do_lda(num_topics)
    elif modeltype == 'lsi':
        do_lsi(num_topics)
